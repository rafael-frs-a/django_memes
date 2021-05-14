# About

It's supposed to be a meme platform built with Django that I made to learn the framework. Since it's main idea is very similar to my **the-flaskington-post** project, a significant part of the html/css was reused.

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

The project was made using Python 3.9.1, with the used packages listed in the *requirements.txt* at the root. The database used is PostgreSQL beacause of it's built in [full text search](https://docs.djangoproject.com/en/3.2/ref/contrib/postgres/search/) feature and native Django support. This project also uses Celery to execute parallel tasks, like sending emails, so it's necessary to define a message broker to work with it. The one I used was RabbitMQ.

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
- **GOOGLE_API_KEY_URL**: path relative to the project root of the Google Cloud JSON key file, needed to the Google Cloud Vision features.

This project uses *python-dotenv*, so you can store these variables in a *.env* file at the root.
