import os

from django.conf import settings
from django.contrib.auth import get_user_model
from django.core.exceptions import ObjectDoesNotExist
from django.core.files import File
from django.core.management import BaseCommand
from django.db.utils import IntegrityError

import MySQLdb
import pandas as pd
from decouple import config

from device.models import Manufacturer, Specialty, Category, Product, CategoryFeature, Feature
from device.constants import ProductLevel
from hospital.models import Client, Role, Account, Device, Item
from hospital.constants import CONSIGNMENT_PURCHASE, BULK_PURCHASE
from price.models import ClientPrice, Discount
from price.constants import VALUE_DISCOUNT, UNIT_COST, PERCENT_DISCOUNT, SYSTEM_COST, DISCOUNTS, ON_DOCTOR_ORDER

User = get_user_model()


def upload_shared_image(name, folder):
    from neptune.models import SharedImage

    shared_image_name = f'{name}.png'
    shared_image_path = os.path.join(settings.BASE_DIR, f'assets/images/{folder}/{shared_image_name}')

    if os.path.exists(shared_image_path):
        print(f'Upload shared image {folder}/{shared_image_name}')
        shared_image = SharedImage.objects.get_or_create(name=name)[0]
        if not shared_image.image:
            shared_image.image.save(shared_image_name, File(open(shared_image_path, 'rb')), save=True)

        return shared_image


class Command(BaseCommand):
    def add_arguments(self, parser):
        parser.add_argument('--media_path', default='old-uploads')
        parser.add_argument('--upload', action='store_true')

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.db = None
        self.media_path = None
        self.skipped_upload = True
        self.warnings = []

    def connect_mysqldb(self):
        self.db = MySQLdb.connect(host=config('OLD_NEPTUNE_DB_HOST', default='localhost'),
                                  port=int(config('OLD_NEPTUNE_DB_PORT', default=3306)),
                                  user=config('OLD_NEPTUNE_DB_USER'),
                                  password=config('OLD_NEPTUNE_DB_PASSWORD'),
                                  db=config('OLD_NEPTUNE_DB_NAME'))
        print('Database connected')

    def upload_image(self, image_name, obj, new_image_name=None):
        try:
            image_url = obj.image.url
            image_status = f'exists {image_url}'
        except ValueError:
            new_image_name = new_image_name or image_name
            if self.skipped_upload:
                image_prefix = obj.__class__._meta.get_field('image').upload_to
                obj.image = image_prefix(obj, new_image_name)
                obj.save()
                image_status = f'skipped uploading {obj.image}'
            else:
                image_path = f'{self.media_path}/{image_name}'
                if os.path.isfile(image_path):
                    obj.image.save(new_image_name, File(open(image_path, 'rb')), save=True)
                    image_status = f'copied from local {image_path}'
                else:
                    image_status = f'not found from local {image_path}'

        return image_status

    def import_manufacturers(self):
        sql = '''
        SELECT manufacturer_name, manufacturer_logo, id
        FROM manufacturers;
        '''
        manufacturers_df = pd.io.sql.read_sql(sql, self.db)
        results = {}
        for index, row in manufacturers_df.iterrows():
            name, logo, old_id = self.sanitize_row(row)
            manufacturer, created = Manufacturer.objects.get_or_create(name=name)
            image_status = self.upload_image(logo, manufacturer)
            print(f'''Manufacturer {name}
                {"created" if created else "exists"}
                image {image_status}
            ''')
            results[old_id] = manufacturer.id

        return results

    def import_device_categories(self):
        sql = '''
            SELECT projects.project_name, category_name, category.image, category.id
            FROM projects, category
            WHERE projects.id = category.project_name;
        '''
        categories_df = pd.io.sql.read_sql(sql, self.db)
        results = {}
        for index, row in categories_df.iterrows():
            specialty_name, category_name, category_image, old_id = self.sanitize_row(row)
            specialty, created = Specialty.objects.get_or_create(name=specialty_name)
            print(f'Specialty {specialty_name} {"created" if created else "exists"}')
            category, created = Category.objects.get_or_create(name=category_name, specialty=specialty)
            image_status = self.upload_image(f'category/{category_image}', category, category_image)
            print(f'Category {category_name} {"created" if created else "exists"} image {image_status}')
            results[old_id] = category.id
        return results

    def import_products(self, manufacturers, categories):
        results = {}
        sql = '''
            SELECT level_name, category_name, manufacturer_name, device_name, model_name, device_image, status, id
            FROM device;
        '''
        products_df = pd.io.sql.read_sql(sql, self.db)
        for index, row in products_df.iterrows():
            (level_name, old_category_id, manufacturer_id, device_name, model_name,
                device_image, status, old_product_id) = self.sanitize_row(row)

            if level_name == 'Entry Level':
                level = ProductLevel.ENTRY.value
            elif level_name == 'Advanced Level':
                level = ProductLevel.ADVANCED.value
            else:
                level = ProductLevel.UNASSIGNED.value
            enabled = status == 'Enabled'
            category_id = categories.get(old_category_id)
            if category_id:
                product, created = Product.objects.get_or_create(level=level, enabled=enabled,
                                                                 name=device_name, model_number=model_name,
                                                                 category_id=category_id,
                                                                 manufacturer_id=manufacturers.get(manufacturer_id))

                image_status = self.upload_image(device_image, product)
                results[old_product_id] = product.id
                print(f'''Product {device_name}
                    {"created" if created else "exists"}
                    image {image_status}
                ''')
            else:
                self.warnings.append(f'Product {device_name} skipped')
        return results

    def import_clients(self):
        sql = 'SELECT client_name, street_address, city, state, image, id FROM clients'
        results = {}
        clients_df = pd.io.sql.read_sql(sql, self.db)
        for index, row in clients_df.iterrows():
            client_name, street, city, state, image, old_client_id = self.sanitize_row(row)
            client, created = Client.objects.get_or_create(name=client_name, street=street, city=city,
                                                           state=state, country='US')
            client_image = image.replace('upload/', '')
            new_image_name = client_image.replace('client/', '')
            image_status = self.upload_image(client_image, client, new_image_name)
            results[old_client_id] = client.id
            print(f'''Client {client_name}
                {"created" if created else "exists"}
                image {image_status}
            ''')
        return results

    def import_client_prices(self, products, clients):
        sql = '''
        SELECT id, device_id, client_name,
               unit_cost, unit_cost_check,
               system_cost, system_cost_check
        FROM client_price;
        '''
        results = {}
        prices_df = pd.io.sql.read_sql(sql, self.db)

        for index, row in prices_df.iterrows():
            (old_price_id, old_product_id, old_client_id,
             unit_cost, unit_cost_enabled, system_cost, system_cost_enabled) = self.sanitize_row(row)

            unit_cost = unit_cost if unit_cost_enabled == 'True' else 0
            system_cost = system_cost if system_cost_enabled == 'True' else 0
            if products.get(old_product_id) and clients.get(old_client_id):
                price, created = ClientPrice.objects.get_or_create(
                    product_id=products[old_product_id],
                    client_id=clients[old_client_id],
                )
                price.unit_cost = unit_cost
                price.system_cost = system_cost
                price.save()
                results[old_price_id] = price.id
                print(f'Product {price.product} price set for {price.client} {"created" if created else "exists"}')

        return results

    def import_discounts(self, prices, discount_field, discount_name, discount_type=PERCENT_DISCOUNT, cost_type=None):
        sql = f'''
        SELECT id, {discount_field}
        FROM client_price
        WHERE {discount_field}_check = 'True';
        '''
        discounts_df = pd.io.sql.read_sql(sql, self.db)

        for index, row in discounts_df.iterrows():
            old_price_id, value = self.sanitize_row(row)
            if prices.get(old_price_id) and value > 0:
                discount = Discount.objects.get_or_create(name=discount_name,
                                                          client_price_id=prices[old_price_id],
                                                          cost_type=cost_type)[0]
                if discount_type == PERCENT_DISCOUNT:
                    discount.percent = value if value < 100 else 0
                else:
                    discount.value = value

                discount.apply_type = DISCOUNTS.get(discount_name, ON_DOCTOR_ORDER)
                discount.discount_type = discount_type
                discount.shared_image = upload_shared_image(discount_name, 'discounts')
                discount.save()
                print(f'Discount {discount_name} added to ClientPrice#{prices[old_price_id]}')

    def import_costs(self, prices):
        self.import_discounts(prices, discount_field='cco_discount', discount_name='CCO',
                              discount_type=PERCENT_DISCOUNT, cost_type=UNIT_COST)
        self.import_discounts(prices, discount_field='cco', discount_name='CCO',
                              discount_type=VALUE_DISCOUNT, cost_type=UNIT_COST)

        self.import_discounts(prices, discount_field='bulk_unit_cost', discount_name='Bulk',
                              discount_type=PERCENT_DISCOUNT, cost_type=UNIT_COST)
        self.import_discounts(prices, discount_field='bulk_system_cost', discount_name='Bulk',
                              discount_type=PERCENT_DISCOUNT, cost_type=SYSTEM_COST)

        self.import_discounts(prices, discount_field='unit_repless_discount', discount_name='Repless',
                              discount_type=PERCENT_DISCOUNT, cost_type=UNIT_COST)
        self.import_discounts(prices, discount_field='unit_rep_cost', discount_name='Repless',
                              discount_type=VALUE_DISCOUNT, cost_type=UNIT_COST)
        self.import_discounts(prices, discount_field='system_repless_discount', discount_name='Repless',
                              discount_type=PERCENT_DISCOUNT, cost_type=SYSTEM_COST)
        self.import_discounts(prices, discount_field='system_repless_cost', discount_name='Repless',
                              discount_type=VALUE_DISCOUNT, cost_type=SYSTEM_COST)

    def import_standard_feature(self, feature_name, products, categories, check=True):
        sql_check_condition = f"WHERE {feature_name}_check = 'True'" if check else ''
        sql = f'''
        SELECT id, category_name,
               {feature_name}
        FROM device
        {sql_check_condition};
        '''
        features_df = pd.io.sql.read_sql(sql, self.db)
        for index, row in features_df.iterrows():
            old_product_id, old_catgory_id, feature_value = self.sanitize_row(row)

            category_id = categories.get(old_catgory_id)
            product_id = products.get(old_product_id)
            if product_id:
                if category_id:
                    category_feature, created = CategoryFeature.objects.get_or_create(category_id=category_id,
                                                                                      name=feature_name)
                    image_status = 'exists'
                    if not category_feature.shared_image:
                        category_feature.shared_image = upload_shared_image(feature_name, 'features')
                        category_feature.save()
                        image_status = 'updated'

                    print(f'''Category feature {feature_name}
                        {"created" if created else "exists"}
                        image {image_status}
                    ''')
                else:
                    category_feature = None
                feature, created = Feature.objects.get_or_create(name=feature_name,
                                                                 category_feature=category_feature,
                                                                 product_id=product_id)
                if not feature.value:
                    self.sanitize_feature_value(feature, feature_value)

                print(f'''Feature {feature_name} for product#{product_id} {"created" if created else "exists"}''')

    def import_additional_features(self, products):
        sql = '''
        SELECT device_id, field_name, field_value
        FROM device_custom_field
        WHERE field_check = 'True';
        '''
        features_df = pd.io.sql.read_sql(sql, self.db)
        for index, row in features_df.iterrows():
            old_product_id, feature_name, feature_value = self.sanitize_row(row)

            product_id = products.get(old_product_id)
            if product_id:
                feature, created = Feature.objects.get_or_create(name=feature_name, value=str(feature_value),
                                                                 product_id=product_id)
                if not feature.value:
                    self.sanitize_feature_value(feature, feature_value)

                print(f'''Feature {feature_name} for product#{product_id} {"created" if created else "exists"}''')

    def import_product_features(self, products, categories):
        for feature in ['longevity', 'exclusive', 'shock', 'size', 'research', 'website_page', 'overall_value']:
            self.import_standard_feature(feature, products, categories)

        for feature in ['url']:
            self.import_standard_feature(feature, products, categories, check=False)

        self.import_additional_features(products)

    def import_roles(self):
        sql = f'''
        SELECT id, roll_name
        FROM roll;
        '''
        roles_df = pd.io.sql.read_sql(sql, self.db)
        results = {}
        for index, row in roles_df.iterrows():
            old_role_id, role_name = self.sanitize_row(row)
            role, created = Role.objects.get_or_create(name=role_name)

            results[old_role_id] = role.id
            print(f'Role {role_name} {"created" if created else "exists"}')

        return results

    def import_users(self):
        sql = f'''
        SELECT id, name, email, profilePic
        FROM users
        WHERE is_delete = 0;
        '''
        users_df = pd.io.sql.read_sql(sql, self.db)
        results = {}
        for index, row in users_df.iterrows():
            old_user_id, name, email, image_name = self.sanitize_row(row)
            created = False
            try:
                user = User.objects.get(email=email)
            except ObjectDoesNotExist:
                user = User.objects.create(name=name, email=email)
                created = True
            image_status = self.upload_image(image_name=f'user/{image_name}',
                                             obj=user,
                                             new_image_name=image_name)
            print(f'''User {email}
                {"created" if created else "exists"}
                image {image_status}
            ''')
            results[old_user_id] = user.id
        return results

    def import_client_users(self, clients):
        roles = self.import_roles()
        users = self.import_users()
        sql = f'''
        SELECT userId, clientId, users.roll
        FROM users, user_clients
        WHERE users.id = user_clients.userId;
        '''
        accounts_df = pd.io.sql.read_sql(sql, self.db)

        for index, row in accounts_df.iterrows():
            old_user_id, old_client_id, old_role_id = self.sanitize_row(row)
            user_id = users.get(old_user_id)
            client_id = clients.get(old_client_id)
            role_id = roles.get(old_role_id)
            if user_id and client_id and role_id:
                account, created = Account.objects.get_or_create(user_id=user_id, client_id=client_id, role_id=role_id)
                print(f'Account {account} {"created" if created else "exists"}')

    def import_client_devices(self, clients, products, prices):
        sql = '''
        SELECT serialdetail.serialNumber, clientId, deviceId,
               purchaseDate, expiryDate, new_purchase_date, new_expiry_date, hospitalPart,
               serialdetail.discount, client_price.id AS client_price_id,
               serialdetail.status, serialdetail.purchaseType, item_file_entry.cco_check, item_file_entry.repless_check
        FROM serialdetail JOIN item_file_entry ON item_file_entry.serialNumber = serialdetail.serialNumber
                          JOIN client_price ON serialdetail.clientId = client_price.client_name
                                            AND serialdetail.deviceId = client_price.device_id;
        '''
        items_df = pd.io.sql.read_sql(sql, self.db)

        for index, row in items_df.iterrows():
            serial_number, old_client_id, old_product_id, purchase_date, expiry_date, \
                new_purchase_date, new_expiry_date, hospital_number, old_discount_percent, old_client_price_id, \
                status, purchase_type, cco_check, repless_check = self.sanitize_row(row)
            client_id = clients.get(old_client_id)
            product_id = products.get(old_product_id)
            expired_date = new_expiry_date or expiry_date or None
            purchased_date = new_purchase_date or purchase_date or None
            purchase_type = BULK_PURCHASE if purchase_type == 'Bulk' else CONSIGNMENT_PURCHASE
            is_used = status != ''
            if client_id and product_id and serial_number:
                device = Device.objects.get_or_create(client_id=client_id, product_id=product_id)[0]
                if hospital_number:
                    if not device.hospital_number:
                        device.hospital_number = hospital_number
                        device.save()
                    elif hospital_number != device.hospital_number:
                        self.warnings.append(f'Client {device.client} has different hospital number {hospital_number} '
                                             f'for product {device.product}')
                try:
                    item, created = Item.objects.get_or_create(device=device, serial_number=serial_number,
                                                               purchased_date=purchased_date,
                                                               expired_date=expired_date,
                                                               purchase_type=purchase_type)
                    try:
                        price = ClientPrice.objects.get(id=prices.get(old_client_price_id))
                    except ObjectDoesNotExist:
                        self.warnings.append(
                            f'Could not find cost for imported item with serial number: {serial_number}')
                    finally:
                        cost_type = SYSTEM_COST if price.system_cost > 0 else UNIT_COST

                        discounted_names = []

                        if old_discount_percent > 0:
                            discounted_names.append('Bulk')
                        if repless_check == 'True':
                            discounted_names.append('Repless')
                        if cco_check == 'True':
                            discounted_names.append('CCO')
                            cost_type = UNIT_COST

                        item_discounts = price.discounts(cost_type).filter(name__in=discounted_names)
                        item.cost_type = cost_type
                        item.is_used = is_used
                        item.save(discounts=item_discounts)
                        item.discounts.set(item_discounts)
                        print(f'Item {item} {"created" if created else "exists"}')
                except IntegrityError:
                    self.warnings.append(f'Duplicated items with serial number {serial_number}')

    def print_warnings(self):
        print('====== WARNINGS =====')
        for warning in self.warnings:
            print(warning)

    def import_physician_specialties(self):
        sql = f'''
        SELECT email, projects.project_name, clients.client_name
        FROM users
            LEFT JOIN user_projects ON users.id = user_projects.userId
            LEFT JOIN projects ON user_projects.projectId = projects.id
            LEFT JOIN user_clients ON users.id = user_clients.userId
            LEFT JOIN clients ON clients.id = user_clients.clientId
        WHERE users.roll IN (2, 3)
            AND projects.id IS NOT NULL;
        '''
        accounts_df = pd.io.sql.read_sql(sql, self.db)

        for index, row in accounts_df.iterrows():
            user_email, specialty_name, client_name = self.sanitize_row(row)
            try:
                specialty = Specialty.objects.get(name=specialty_name)
                client = Client.objects.get(name=client_name)
                user = User.objects.get(email=user_email)
                account = Account.objects.get(user=user, client=client)
                account.specialties.add(specialty)
                print(f'Added {specialty} to account {account}')
            except ObjectDoesNotExist as error:
                self.warnings.append(f'{error}: {user_email} - {client_name}: {specialty_name}')

    def sanitize_row(self, row):
        return [str(cell).strip() if isinstance(cell, str) else cell for cell in row]

    def sanitize_feature_value(self, feature, feature_value):
        value = str(feature_value)

        if feature.name == 'longevity':
            value = f'{value} Years'
        elif feature.name == 'size':
            gram_cc = value.split('/')
            gram = gram_cc[0]
            cc = '' if len(gram_cc) == 1 else gram_cc[1]
            value = f'{gram}g/{cc}cc'
        elif feature.name == 'shock':
            joule_sec = value.split('/')
            joule = joule_sec[0]
            sec = '' if len(joule_sec) == 1 else joule_sec[1]
            value = f'{joule}J/{sec}s'

        feature.value = value
        feature.save()

    def handle(self, *args, **kwargs):
        self.connect_mysqldb()
        self.media_path = kwargs['media_path']
        self.skipped_upload = not kwargs['upload']

        manufacturers = self.import_manufacturers()
        categories = self.import_device_categories()

        products = self.import_products(manufacturers, categories)
        self.import_product_features(products, categories)

        clients = self.import_clients()
        self.import_client_users(clients)

        prices = self.import_client_prices(products, clients)
        self.import_costs(prices)

        self.import_client_devices(clients, products, prices)

        self.import_physician_specialties()

        self.db.close()

        self.print_warnings()
