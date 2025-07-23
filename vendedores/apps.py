from django.apps import AppConfig


class VendedoresConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'vendedores'
    verbose_name = 'Vendedores'
    
    def ready(self):
        # Import signals or other initialization code here
        pass
