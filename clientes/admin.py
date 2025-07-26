from django.contrib import admin
from django.utils.translation import gettext_lazy as _
from .models import Cliente, Favorito


class FavoritoInline(admin.TabularInline):
    """Inline para los productos favoritos en el admin de Cliente."""
    model = Favorito
    extra = 1
    autocomplete_fields = ('producto',)
    fields = ('producto', 'fecha_agregado')
    readonly_fields = ('fecha_agregado',)


@admin.register(Cliente)
class ClienteAdmin(admin.ModelAdmin):
    """Configuración del admin para el modelo Cliente."""
    list_display = ('id_cliente', 'nombre_completo', 'email_cliente', 'telefono', 'puntos_fidelidad', 'activo')
    list_filter = ('activo', 'fecha_registro')
    search_fields = ('nombre_cliente', 'apellido_cliente', 'email_cliente', 'telefono')
    readonly_fields = ('fecha_registro', 'ultima_actualizacion', 'puntos_fidelidad')
    date_hierarchy = 'fecha_registro'
    inlines = [FavoritoInline]
    fieldsets = (
        (_('Información Personal'), {
            'fields': (
                'id_usuario',
                ('nombre_cliente', 'apellido_cliente'),
                'email_cliente',
                'telefono',
                'two_factor_auth',
            )
        }),
        (_('Dirección y Horario'), {
            'fields': (
                'direccion_entrega',
                'horario_atencion',
            )
        }),
        (_('Puntos de Fidelidad'), {
            'fields': ('puntos_fidelidad',)
        }),
        (_('Estado'), {
            'fields': ('activo',)
        }),
        (_('Auditoría'), {
            'classes': ('collapse',),
            'fields': ('fecha_registro', 'ultima_actualizacion')
        }),
    )
    
    def nombre_completo(self, obj):
        """Método para mostrar el nombre completo en la lista."""
        return f"{obj.nombre_cliente} {obj.apellido_cliente}"
    nombre_completo.short_description = _('Nombre Completo')
    nombre_completo.admin_order_field = 'nombre_cliente'


@admin.register(Favorito)
class FavoritoAdmin(admin.ModelAdmin):
    """Configuración del admin para el modelo Favorito."""
    list_display = ('id', 'cliente', 'producto', 'fecha_agregado')
    list_filter = ('fecha_agregado',)
    search_fields = ('cliente__nombre_cliente', 'producto__nombre_producto')
    readonly_fields = ('fecha_agregado',)
    autocomplete_fields = ('cliente', 'producto')
    date_hierarchy = 'fecha_agregado'
    fieldsets = (
        (None, {
            'fields': ('cliente', 'producto')
        }),
        (_('Auditoría'), {
            'classes': ('collapse',),
            'fields': ('fecha_agregado',)
        }),
    )
