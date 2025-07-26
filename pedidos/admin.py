from django.contrib import admin
from django.utils.translation import gettext_lazy as _
from .models import Pedido, DetallePedido

class DetallePedidoInline(admin.TabularInline):
    """Inline para los detalles de pedido en el admin de Pedido."""
    model = DetallePedido
    extra = 1
    fields = ('id_producto', 'cantidad_producto', 'precio_unitario', 'subtotal', 'notas')
    readonly_fields = ('subtotal',)
    autocomplete_fields = ('id_producto',)

@admin.register(Pedido)
class PedidoAdmin(admin.ModelAdmin):
    """Configuración del admin para el modelo Pedido."""
    list_display = ('id_pedido', 'fecha_pedido', 'id_cliente', 'id_vendedor', 'get_estado_actual', 'total')
    list_filter = ('fecha_pedido', 'id_vendedor', 'id_repartidor')
    search_fields = ('id_pedido', 'id_cliente__nombre_cliente', 'id_vendedor__nombre_negocio')
    readonly_fields = ('fecha_creacion', 'fecha_actualizacion', 'total')
    date_hierarchy = 'fecha_pedido'
    inlines = [DetallePedidoInline]
    fieldsets = (
        (_('Información Básica'), {
            'fields': ('id_pedido', 'fecha_pedido', 'estado_pedido', 'total')
        }),
        (_('Usuarios'), {
            'fields': ('id_cliente', 'id_vendedor', 'id_repartidor')
        }),
        (_('Información de Entrega'), {
            'fields': ('direccion_pedido', 'instrucciones_entrega')
        }),
        (_('Pago'), {
            'fields': ('metodo_pago', 'two_factor_auth')
        }),
        (_('Auditoría'), {
            'classes': ('collapse',),
            'fields': ('fecha_creacion', 'fecha_actualizacion')
        }),
    )

    def get_estado_actual(self, obj):
        """Método para mostrar el estado actual en la lista."""
        return obj.get_estado_actual()
    get_estado_actual.short_description = _('Estado Actual')
    get_estado_actual.admin_order_field = 'estado_pedido'

@admin.register(DetallePedido)
class DetallePedidoAdmin(admin.ModelAdmin):
    """Configuración del admin para el modelo DetallePedido."""
    list_display = ('id_detalle', 'id_pedido', 'id_producto', 'cantidad_producto', 'precio_unitario', 'subtotal')
    list_filter = ('id_pedido__id_vendedor',)
    search_fields = ('id_pedido__id_pedido', 'id_producto__nombre_producto')
    readonly_fields = ('subtotal', 'fecha_creacion', 'fecha_actualizacion')
    autocomplete_fields = ('id_pedido', 'id_producto')
    fieldsets = (
        (None, {
            'fields': ('id_pedido', 'id_producto', 'cantidad_producto', 'precio_unitario', 'subtotal', 'notas')
        }),
        (_('Auditoría'), {
            'classes': ('collapse',),
            'fields': ('fecha_creacion', 'fecha_actualizacion')
        }),
    )
