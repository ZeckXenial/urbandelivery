from django.apps import AppConfig


class RepartidoresConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'repartidores'
    verbose_name = 'Repartidores'
    
    def ready(self):
        # Import signals or other initialization code here
        pass
