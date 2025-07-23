from django.urls import path
from rest_framework.routers import DefaultRouter
from . import api_views

router = DefaultRouter()

urlpatterns = [
    # Perfil del cliente
    path('perfil/', api_views.ClienteViewSet.as_view({'get': 'perfil'}), name='cliente-perfil'),
    
    # Pedidos del cliente
    path('pedidos/', api_views.ClienteViewSet.as_view({'get': 'pedidos'}), name='cliente-pedidos'),
    
    # Direcciones del cliente
    path('direcciones/', api_views.ClienteViewSet.as_view({'get': 'direcciones'}), name='cliente-direcciones'),
]
