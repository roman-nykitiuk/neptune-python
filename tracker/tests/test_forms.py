from django.test import TestCase

from hospital.factories import ClientFactory, AccountFactory
from tracker.forms import RepCaseForm
from tracker.models import NEW_CASE


class RepCaseFormTestCase(TestCase):
    def test_form_invalid(self):
        client = ClientFactory()
        account = AccountFactory()
        form = RepCaseForm(data={'client': client.id, 'owners': [account.id]})
        self.assertFalse(form.is_valid())
        self.assertEqual(form.errors['__all__'],
                         [f'Invalid {account.role.name} {account.user.email} for {client.name}'])

        account_1, account_2, account_3 = AccountFactory.create_batch(3, client=client)
        form = RepCaseForm(data={'client': client.id,
                                 'owners': [account_1.id, account_3.id],
                                 'physician': account_2.id,
                                 'procedure_date': '2000-11-22',
                                 'status': NEW_CASE})
        self.assertTrue(form.is_valid())
