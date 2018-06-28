#!/bin/env sh
#virtualenv env -ppython3
#. env/bin/activate
#pip install -r requirements.txt -t modules
export PYTHONPATH=modules
python manage.py collectstatic --noinput
python manage.py runserver 0.0.0.0:8080
