from django.shortcuts import render, get_object_or_404, redirect
from django.views.generic import ListView, DetailView, TemplateView, View, UpdateView, CreateView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib import messages
from django.urls import reverse_lazy, reverse
from django.db.models import Q, Count, Avg, F
from django.http import JsonResponse, HttpResponseRedirect
from django.views.decorators.http import require_POST
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.utils import timezone
from django.db import transaction

from .models import Cliente, Favorito
from vendedores.models import Producto, Categoria, ValoracionProducto
from pedidos.models import Pedido, DetallePedido, EstadoPedido

# Vistas principales
class HomeView(TemplateView):
    """Página de inicio para clientes."""
    template_name = 'clientes/home.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['productos_destacados'] = Producto.objects.annotate(
            avg_rating=Avg('valoraciones__valoracion')
        ).order_by('-avg_rating')[:8]
        context['categorias_populares'] = Categoria.objects.annotate(
            num_productos=Count('productos')
        ).order_by('-num_productos')[:6]
        return context

class CatalogoProductosView(ListView):
    """Vista para mostrar el catálogo de productos con filtros."""
    model = Producto
    template_name = 'clientes/catalogo.html'
    context_object_name = 'productos'
    paginate_by = 12
    
    def get_queryset(self):
        queryset = Producto.objects.filter(activo=True).select_related('vendedor', 'categoria')
        categoria_id = self.request.GET.get('categoria')
        if categoria_id:
            queryset = queryset.filter(categoria_id=categoria_id)
        busqueda = self.request.GET.get('q')
        if busqueda:
            queryset = queryset.filter(
                Q(nombre__icontains=busqueda) |
                Q(descripcion__icontains=busqueda) |
                Q(categoria__nombre__icontains=busqueda)
            )
        orden = self.request.GET.get('orden', 'relevancia')
        if orden == 'precio_asc':
            queryset = queryset.order_by('precio')
        elif orden == 'precio_desc':
            queryset = queryset.order_by('-precio')
        elif orden == 'nuevos':
            queryset = queryset.order_by('-fecha_creacion')
        elif orden == 'valoracion':
            queryset = queryset.annotate(
                avg_rating=Avg('valoraciones__valoracion')
            ).order_by('-avg_rating')
        return queryset
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['categorias'] = Categoria.objects.all()
        context['categoria_actual'] = self.request.GET.get('categoria')
        context['busqueda'] = self.request.GET.get('q', '')
        context['orden_actual'] = self.request.GET.get('orden', 'relevancia')
        return context

class DetalleProductoView(DetailView):
    """Vista para mostrar los detalles de un producto."""
    model = Producto
    template_name = 'clientes/detalle_producto.html'
    context_object_name = 'producto'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        producto = self.get_object()
        valoraciones = producto.valoraciones.filter(aprobado=True).select_related('cliente')
        valoracion_promedio = valoraciones.aggregate(avg_rating=Avg('valoracion'))
        
        context.update({
            'valoraciones': valoraciones,
            'valoracion_promedio': valoracion_promedio['avg_rating'] or 0,
            'productos_relacionados': Producto.objects.filter(
                categoria=producto.categoria
            ).exclude(id=producto.id)[:4],
            'en_favoritos': Favorito.objects.filter(
                cliente=self.request.user.cliente,
                producto=producto
            ).exists() if self.request.user.is_authenticated and hasattr(self.request.user, 'cliente') else False,
        })
        return context

# Vistas del carrito de compras
class CarritoView(LoginRequiredMixin, TemplateView):
    """Vista para ver y gestionar el carrito de compras."""
    template_name = 'clientes/carrito.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        carrito = self.request.session.get('carrito', {})
        productos_ids = carrito.keys()
        
        productos_en_carrito = []
        total = 0
        
        for producto_id, item in carrito.items():
            try:
                producto = Producto.objects.get(id=producto_id)
                cantidad = item['cantidad']
                subtotal = producto.precio * cantidad
                total += subtotal
                
                productos_en_carrito.append({
                    'id': producto.id,
                    'producto': producto,
                    'cantidad': cantidad,
                    'subtotal': subtotal
                })
            except Producto.DoesNotExist:
                continue
        
        context['productos_en_carrito'] = productos_en_carrito
        context['total_carrito'] = total
        context['direcciones_entrega'] = self.request.user.cliente.direcciones.all()
        return context

@require_POST
def agregar_al_carrito(request, producto_id):
    """Vista para agregar un producto al carrito."""
    cantidad = int(request.POST.get('cantidad', 1))
    
    carrito = request.session.get('carrito', {})
    
    if str(producto_id) in carrito:
        carrito[str(producto_id)]['cantidad'] += cantidad
    else:
        carrito[str(producto_id)] = {'cantidad': cantidad}
    
    request.session['carrito'] = carrito
    messages.success(request, 'Producto agregado al carrito')
    
    next_url = request.POST.get('next', reverse('clientes:carrito'))
    return redirect(next_url)

@require_POST
def eliminar_del_carrito(request, item_id):
    """Vista para eliminar un producto del carrito."""
    carrito = request.session.get('carrito', {})
    
    if str(item_id) in carrito:
        del carrito[str(item_id)]
        request.session['carrito'] = carrito
        messages.success(request, 'Producto eliminado del carrito')
    
    return redirect('clientes:carrito')

@require_POST
def actualizar_carrito(request):
    """Vista para actualizar las cantidades de los productos en el carrito."""
    carrito = request.session.get('carrito', {})
    
    for producto_id, cantidad in request.POST.items():
        if producto_id != 'csrfmiddlewaretoken' and producto_id in carrito:
            carrito[producto_id]['cantidad'] = int(cantidad)
    
    request.session['carrito'] = carrito
    messages.success(request, 'Carrito actualizado')
    return redirect('clientes:carrito')
