#!/usr/bin/env bash
set -o errexit

pip install -r requirements.txt

python manage.py collectstatic --no-input
python manage.py migrate
python manage.py shell -c "from django.contrib.auth import get_user_model; User=get_user_model(); username='genta'; password='genta1915'; email='genta@example.com'; user, created = User.objects.get_or_create(username=username, defaults={'email': email, 'is_staff': True, 'is_superuser': True}); user.is_staff=True; user.is_superuser=True; user.set_password(password); user.save()"