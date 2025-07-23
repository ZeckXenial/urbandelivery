from django.urls import path
from rest_framework.routers import DefaultRouter
from . import api_views

router = DefaultRouter()

urlpatterns = [
    # Dashboard del vendedor
    path('dashboard/', api_views.VendedorViewSet.as_view({'get': 'dashboard'}), name='vendedor-dashboard'),
    
    # Gestión de pedidos
    path('pedidos/', api_views.VendedorViewSet.as_view({'get': 'pedidos'}), name='vendedor-pedidos'),
    path('pedidos/<int:pk>/actualizar-estado/', 
         api_views.VendedorViewSet.as_view({'post': 'actualizar_estado_pedido'}), 
         name='vendedor-actualizar-estado-pedido'),
    
    # Gestión del menú
    path('menu/', api_views.VendedorViewSet.as_view({'get': 'menu'}), name='vendedor-menu'),
]
