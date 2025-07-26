from django.apps import AppConfig


class PedidosConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'pedidos'
    
    def ready(self):
        # Importa las señales para que se registren
        import pedidos.signals
