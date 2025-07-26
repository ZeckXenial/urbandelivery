from django.contrib import admin
from django.utils.translation import gettext_lazy as _
from .models import Repartidor, UbicacionRepartidor, HistorialTrabajo, Vehiculo, DocumentoRepartidor


class UbicacionRepartidorInline(admin.TabularInline):
    """Inline para el historial de ubicaciones en el admin de Repartidor."""
    model = UbicacionRepartidor
    extra = 0
    readonly_fields = ('fecha_ubicacion',)
    fields = ('latitud', 'longitud', 'fecha_ubicacion')
    max_num = 1
    can_delete = False


class HistorialTrabajoInline(admin.TabularInline):
    """Inline para el historial de trabajo en el admin de Repartidor."""
    model = HistorialTrabajo
    extra = 1
    readonly_fields = ('fecha_inicio', 'fecha_fin')
    fields = ('fecha_inicio', 'fecha_fin', 'estado', 'comentarios')


class DocumentoRepartidorInline(admin.StackedInline):
    """Inline para los documentos en el admin de Repartidor."""
    model = DocumentoRepartidor
    extra = 1
    fields = ('tipo_documento', 'archivo', 'fecha_vencimiento', 'aprobado')


@admin.register(Repartidor)
class RepartidorAdmin(admin.ModelAdmin):
    """Configuración del admin para el modelo Repartidor."""
    list_display = (
        'id_repartidor', 
        'usuario_completo', 
        'tipo_documento', 
        'numero_documento', 
        'estado', 
        'activo'
    )
    list_filter = ('estado', 'activo', 'tipo_documento')
    search_fields = (
        'id_usuario__email_usuario', 
        'numero_documento', 
        'id_usuario__first_name', 
        'id_usuario__last_name'
    )
    readonly_fields = ('fecha_registro', 'ultima_actualizacion')
    inlines = [UbicacionRepartidorInline, HistorialTrabajoInline, DocumentoRepartidorInline]
    fieldsets = (
        (_('Información Personal'), {
            'fields': (
                'id_usuario',
                'tipo_documento',
                'numero_documento',
                'fecha_nacimiento',
                'genero',
            )
        }),
        (_('Información de Contacto'), {
            'fields': (
                'telefono_emergencia',
                'contacto_emergencia',
                'direccion',
            )
        }),
        (_('Información Laboral'), {
            'fields': (
                'estado',
                'fecha_ingreso',
                'fecha_vencimiento_licencia',
                'numero_seguro_social',
            )
        }),
        (_('Información Bancaria'), {
            'classes': ('collapse',),
            'fields': (
                'banco',
                'numero_cuenta',
                'tipo_cuenta',
            )
        }),
        (_('Estado'), {
            'fields': ('activo',)
        }),
        (_('Auditoría'), {
            'classes': ('collapse',),
            'fields': ('fecha_registro', 'ultima_actualizacion')
        }),
    )

    def usuario_completo(self, obj):
        """Método para mostrar el nombre completo del usuario."""
        if obj.id_usuario:
            return f"{obj.id_usuario.get_full_name()} ({obj.id_usuario.email_usuario})"
        return "Sin usuario asociado"
    usuario_completo.short_description = _('Usuario')
    usuario_completo.admin_order_field = 'id_usuario__first_name'


@admin.register(Vehiculo)
class VehiculoAdmin(admin.ModelAdmin):
    """Configuración del admin para el modelo Vehiculo."""
    list_display = ('id_vehiculo', 'id_repartidor', 'tipo_vehiculo', 'placa', 'anio', 'activo')
    list_filter = ('tipo_vehiculo', 'activo')
    search_fields = ('placa', 'marca', 'modelo', 'id_repartidor__id_usuario__email_usuario')
    list_editable = ('activo',)
    readonly_fields = ('fecha_registro', 'fecha_actualizacion')
    fieldsets = (
        (None, {
            'fields': (
                'id_repartidor',
                'tipo_vehiculo',
                'marca',
                'modelo',
                'anio',
                'color',
                'placa',
                'seguro',
                'activo',
            )
        }),
        (_('Documentos'), {
            'classes': ('collapse',),
            'fields': ('documento_seguro', 'documento_tarjeta_propiedad')
        }),
        (_('Auditoría'), {
            'classes': ('collapse',),
            'fields': ('fecha_registro', 'fecha_actualizacion')
        }),
    )


@admin.register(DocumentoRepartidor)
class DocumentoRepartidorAdmin(admin.ModelAdmin):
    """Configuración del admin para el modelo DocumentoRepartidor."""
    list_display = ('id_documento', 'id_repartidor', 'tipo_documento', 'fecha_vencimiento', 'aprobado')
    list_filter = ('tipo_documento', 'aprobado')
    search_fields = (
        'id_repartidor__id_usuario__email_usuario', 
        'id_repartidor__numero_documento',
        'tipo_documento'
    )
    list_editable = ('aprobado',)
    readonly_fields = ('fecha_subida', 'fecha_aprobacion')
    date_hierarchy = 'fecha_vencimiento'
    fieldsets = (
        (None, {
            'fields': (
                'id_repartidor',
                'tipo_documento',
                'archivo',
                'aprobado',
            )
        }),
        (_('Fechas'), {
            'fields': (
                'fecha_vencimiento',
                'fecha_subida',
                'fecha_aprobacion',
            )
        }),
        (_('Notas'), {
            'classes': ('collapse',),
            'fields': ('notas',)
        }),
    )
