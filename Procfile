web: python manage.py migrate && python manage.py collectstatic --noinput && gunicorn hall_crm.wsgi:application --bind 0.0.0.0:$PORT
