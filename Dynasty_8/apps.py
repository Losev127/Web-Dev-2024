from django.apps import AppConfig


class Dynasty8Config(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'Dynasty_8'

class Dynasty8Config(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'Dynasty_8'

# Dynasty_8/apps.py
def ready(self):
    import Dynasty_8.signals
