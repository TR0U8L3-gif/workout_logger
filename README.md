# Workout Logger

### Packages

py-bycrypt: ```pip install bcrypt```

bootstrap ```pip install django-bootstrap-v5```

fontawesomefree ```pip install fontawesomefree```

### The development server

Change into the outer **exercise_logger** directory, if you haven’t already, and run the following commands:

```python manage.py runserver```

If you want to change the server’s IP, pass it along with the port:

```python manage.py runserver 0.0.0.0:8000```


### Database setup

```python manage.py migrate```

```python manage.py makemigrations [module name]```

```python manage.py sqlmigrate [module name] [file]```

```python manage.py createsuperuser```
