from django.urls import path, include
from rest_framework.routers import DefaultRouter

from . import views

# Crear un router y registrar nuestros viewsets
router = DefaultRouter()
router.register(r'pedidos', views.PedidoViewSet, basename='pedido')
router.register(r'detalles-pedido', views.DetallePedidoViewSet, basename='detalle-pedido')

# Las URLs de la API ahora se determinan automáticamente por el router
urlpatterns = [
    path('', include(router.urls)),
    
    # Endpoints adicionales para acciones personalizadas
    path('pedidos/<int:pk>/cambiar-estado/', 
         views.PedidoViewSet.as_view({'post': 'cambiar_estado'}), 
         name='pedido-cambiar-estado'),
    path('pedidos/<int:pk>/asignar-repartidor/', 
         views.PedidoViewSet.as_view({'post': 'asignar_repartidor'}), 
         name='pedido-asignar-repartidor'),
    path('pedidos/<int:pk>/marcar-entregado/', 
         views.PedidoViewSet.as_view({'post': 'marcar_entregado'}), 
         name='pedido-marcar-entregado'),
]
