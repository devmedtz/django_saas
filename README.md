# django Software as a service (saas)
django-saas is a generic subscription billing system built for django projects. If you want to charge users on a for plans and features, this project is ideal for you.

## Features
1. User able to free signup for 14 days demo to access features
2. User able to comfirm registration by email or OTP
3. User able to select the plan on signup and he/she may buy or access    demo for 14 days
4. After 14 days ends, user may pay for next 1/6/12 month subscription for the plan selected, or upgrade or downgrade the plan
5. Payment gateway should be MPESA, by mpesa open api

## Installation
- Clone the repo

   ```git clone git@github.com:devmedtz/django_saas.git```

- Create virtual environment and activate it.

   ```
   virtualenv env

   env/scripts/activate
   ```

- Install the required packages

   ```pip install -r requirements.txt```

-  Create and apply migrations

   ```python manage.py makemigrations```

   ```python manage.py migrate```

- rename ```.env-sample``` to ```.env``` and fill accordingly.

- Create superuser

   ```python manage.py createsuperuser```

- Run development server

   ```python manage.py runserver```


### Contributions are warmly welcomed.

- Start contributing following the [contributing guide](CONTRIBUTING.md)
