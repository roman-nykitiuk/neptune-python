# Neptune-PPA

[![Coverage Status](https://coveralls.io/repos/github/EastAgile/Neptune/badge.svg?branch=feature%2F639-master-admin-add-client&t=Wdm1ll)](https://coveralls.io/github/EastAgile/Neptune?branch=feature%2F639-master-admin-add-client)

### Required environments

+ Python 3.6.5
+ Django 2.0.4
+ Postgresql 10.3
+ Node >=4 <=9
+ Yarn
+ Set up environment variables in `.env` file, which is cloned from `.env.example` file

### Project's main structure
```
neptune
|___neptune
|   |___urls.py
|   |___wsgi.py
|   |___settings
|       |___base.py
|       |___local.py
|       |___circleci.py
|
|___manage.py
|___.env
|___.env.example
|___requirements
|       |___base.txt
|       |___local.txt
|       |___circleci.txt
|       |___prod.txt
|
|___package.json
|___webpack.config.js

```

### Development

Use [**virtualenvwrapper**](https://virtualenvwrapper.readthedocs.io/en/latest/) to manage development environment *neptune*

```bash
workon neptune
pip install -r requirements/local.txt
yarn install
yarn build
python manage.py migrate
python manage.py runserver
```


### Testing

```bash
# React app
yarn lint
yarn test

# Django app
flake8
coverage run manage.py test
```

### Deployment
- Manual deployment with [ElasticBeanstalk CLI](https://docs.aws.amazon.com/elasticbeanstalk/latest/dg/eb-cli3.html)
- Auto deployment from CircleCI with *circleci* IAM user

