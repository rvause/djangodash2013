Deed Hero
=========

[![Build Status](https://travis-ci.org/rvause/djangodash2013.png?branch=master)](https://travis-ci.org/rvause/djangodash2013)

http://www.deedhero.com

A simple application that provides suggestions of kind gestures for your loved
ones, be it a friend, relative, SO, or pet.

## Project Setup

1. Create a new virtualenv: `virtualenv env` and `source env/bin/activate`.
2. Install requirements: `pip install -r requirements.txt`.
3. Set DATABASE_URL and DJANGO_SECRET_KEY in your environment.
4. Sync the database: `python manage.py syncdb`.
5. Run migrationsL `python manage.py migrate`.
6. Finally you can run the project `python manage.py runserver`

## Environment Variables

A number of settings need to be set in your environment

Required:

* DATABASE_URL - URL to connect to your PostgreSQL database.
* DJANGO_SECRET_KEY - Secret key for the project.

Optional:

* SOCIAL_AUTH_TWITTER_KEY - Twitter API key
* SOCIAL_AUTH_TWITTER_SECRET - Twitter API secret
* SOCIAL_AUTH_FACEBOOK_KEY - Facebook API key
* SOCIAL_AUTH_FACEBOOK_SECRET - Facebook API secret


## Authors

* Rick Vause
* Mike Buttery


Built for Django Dash 2013  -  http://djangodash.com/
