from django.urls import path
from rest_framework.routers import DefaultRouter
from . import api_views

router = DefaultRouter()

urlpatterns = [
    # Estado del repartidor
    path('estado/', api_views.RepartidorViewSet.as_view({'get': 'estado'}), name='repartidor-estado'),
    
    # Gestión de pedidos
    path('pedidos/disponibles/', 
         api_views.RepartidorViewSet.as_view({'get': 'pedidos_disponibles'}), 
         name='repartidor-pedidos-disponibles'),
    path('pedidos/<int:pk>/tomar/', 
         api_views.RepartidorViewSet.as_view({'post': 'tomar_pedido'}), 
         name='repartidor-tomar-pedido'),
    path('pedidos/<int:pk>/actualizar-estado/', 
         api_views.RepartidorViewSet.as_view({'post': 'actualizar_estado'}), 
         name='repartidor-actualizar-estado'),
    
    # Historial de entregas
    path('historial/', 
         api_views.RepartidorViewSet.as_view({'get': 'historial'}), 
         name='repartidor-historial'),
    
    # Actualización de ubicación en tiempo real
    path('ubicacion/actualizar/', 
         api_views.RepartidorViewSet.as_view({'post': 'actualizar_ubicacion'}), 
         name='repartidor-actualizar-ubicacion'),
]
