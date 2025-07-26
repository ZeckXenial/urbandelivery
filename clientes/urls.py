from django.urls import path
from . import views

app_name = 'clientes'

urlpatterns = [
    # Páginas principales
    path('', views.HomeView.as_view(), name='home'),
    path('catalogo/', views.CatalogoProductosView.as_view(), name='catalogo'),
    path('producto/<int:pk>/', views.DetalleProductoView.as_view(), name='detalle_producto'),
    
    # Carrito de compras
    path('carrito/', views.CarritoView.as_view(), name='carrito'),
    path('carrito/agregar/<int:producto_id>/', views.agregar_al_carrito, name='agregar_al_carrito'),
    path('carrito/eliminar/<int:item_id>/', views.eliminar_del_carrito, name='eliminar_del_carrito'),
    path('carrito/actualizar/', views.actualizar_carrito, name='actualizar_carrito'),
    
    # Pedidos
    path('pedidos/', views.ListaPedidosView.as_view(), name='lista_pedidos'),
    path('pedidos/<int:pk>/', views.DetallePedidoView.as_view(), name='detalle_pedido'),
    path('pedidos/<int:pedido_id>/seguimiento/', views.SeguimientoPedidoView.as_view(), name='seguimiento_pedido'),
    
    # Perfil y direcciones
    path('perfil/', views.PerfilClienteView.as_view(), name='perfil'),
    path('perfil/editar/', views.EditarPerfilView.as_view(), name='editar_perfil'),
    path('direcciones/', views.ListaDireccionesView.as_view(), name='lista_direcciones'),
    path('direcciones/agregar/', views.AgregarDireccionView.as_view(), name='agregar_direccion'),
    path('direcciones/<int:pk>/editar/', views.EditarDireccionView.as_view(), name='editar_direccion'),
    path('direcciones/<int:pk>/eliminar/', views.eliminar_direccion, name='eliminar_direccion'),
    
    # Favoritos
    path('favoritos/', views.ListaFavoritosView.as_view(), name='lista_favoritos'),
    path('favoritos/agregar/<int:producto_id>/', views.agregar_favorito, name='agregar_favorito'),
    path('favoritos/eliminar/<int:producto_id>/', views.eliminar_favorito, name='eliminar_favorito'),
]
