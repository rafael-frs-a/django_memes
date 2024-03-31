# About

It's supposed to be a meme platform built with Django that I made to learn the framework. Since it's main idea is very similar to my [the-flaskington-post](https://github.com/rafael-frs-a/the-flaskington-post) project, a significant part of the html/css was reused.

![Screenshot 2024-03-31 123603](https://github.com/rafael-frs-a/django_memes/assets/76019940/5f6ec838-beba-4904-842d-81b305fedab4)

![Screenshot 2024-03-31 124020](https://github.com/rafael-frs-a/django_memes/assets/76019940/e537c003-d9f5-4a56-9013-0610ba238c14)


# Features

- Account features:
  - Sign up;
  - Account confirmation via email;
  - Login/logout;
  - Password recovery;
  - Upload profile picture;
  - Change email with validation;
  - Delete account;
- Security:
  - Default Django security features;
- Default Django admin interface;
- Moderation interface:
  - Approve/deny posts;
  - Ban user;
  - CRUD personal post denial reasons;
- Sending emails;
- Basic PWA functionality, like installing and offline page;
- Automated tests using Pytest-Django;
- Automatic image tagging/text-extraction using Google Cloud Vision.

# Dependencies

The project was made using Python 3.9.1, with the used packages listed in the *requirements.txt* at the root.
The database used is PostgreSQL beacause of it's built in [full text search](https://docs.djangoproject.com/en/3.2/ref/contrib/postgres/search/) feature and native Django support.
This project uses Google Cloud for storage and AI vision, so it's necessary to have an account and inform a valid JSON key file, although the Google Cloud storage can be easily deactivated changing the settings file.
This project also uses Celery to execute parallel tasks, like sending emails, so you have to define a message broker to work with it. The one I used was RabbitMQ.

# Configuration

## Environment Variables

- **SECRET_KEY**: Django secret key;
- **SITE_HOST**: host set to *ALLOWED_HOSTS* when the project is not in debug;
- **SITE_URL**: path of the project domain and port. It's used as a shortcut to generate full url paths meant to be accessed externally, like the links in the automatically-generated emails;
- **DEBUG**: optional variable. If set to *True*, the project will run in debug mode;
- **DATABASE_URL**: project database configuration. It must be something like *psql://database_user:database_password@database_host:database_port/database_name*;
- **CELERY_BROKER_URL**: path to the broker used to deliver tasks to Celery;
- **EMAIL_HOST**, **EMAIL_PORT**, **EMAIL_HOST_USER**, **EMAIL_HOST_PASSWORD**, **EMAIL_USE_TLS** and **EMAIL_USE_SSL**: configuration of the email address used to send emails to users;
- **EMAIL_TEST_USER**: extra email address used in the automated tests. It can be the same as **EMAIL_HOST_USER**, but ideally should be different for the tests logic;
- **GOOGLE_APPLICATION_CREDENTIALS**: path to the Google Cloud JSON key file.

This project uses *python-dotenv*, so you can store these variables in a *.env* file at the root.

# Code quality

Codebeat quality review available on [this link](https://codebeat.co/projects/github-com-rafael-frs-a-django_memes-master).
