web: python manage.py check_redis && daphne classroom.asgi:application --port $PORT --bind 0.0.0.0
release: python manage.py migrate --noinput && python manage.py collectstatic --noinput