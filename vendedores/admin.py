from django.contrib import admin
from django.utils.translation import gettext_lazy as _
from .models import Vendedor, Categoria, Producto, ValoracionProducto


class ProductoInline(admin.TabularInline):
    """Inline para los productos en el admin de Vendedor."""
    model = Producto
    extra = 1
    fields = ('nombre_producto', 'descripcion', 'precio', 'stock', 'disponible')
    show_change_link = True


class ValoracionProductoInline(admin.TabularInline):
    """Inline para las valoraciones en el admin de Producto."""
    model = ValoracionProducto
    extra = 1
    readonly_fields = ('fecha_valoracion',)
    fields = ('id_cliente', 'puntuacion', 'comentario', 'fecha_valoracion')


@admin.register(Vendedor)
class VendedorAdmin(admin.ModelAdmin):
    """Configuración del admin para el modelo Vendedor."""
    list_display = ('id_vendedor', 'nombre_negocio', 'id_usuario', 'telefono_negocio', 'estado', 'activo')
    list_filter = ('estado', 'activo', 'fecha_registro')
    search_fields = ('nombre_negocio', 'id_usuario__email_usuario', 'telefono_negocio')
    readonly_fields = ('fecha_registro', 'ultima_actualizacion', 'calificacion_promedio', 'total_valoraciones')
    date_hierarchy = 'fecha_registro'
    inlines = [ProductoInline]
    fieldsets = (
        (_('Información del Negocio'), {
            'fields': (
                'id_usuario',
                'nombre_negocio',
                'descripcion_negocio',
                'img_negocio',
                'estado',
                'activo'
            )
        }),
        (_('Información de Contacto'), {
            'fields': (
                'telefono_negocio',
                'email_negocio',
                'horario_atencion',
                'direccion_negocio',
            )
        }),
        (_('Calificaciones'), {
            'fields': (
                'calificacion_promedio',
                'total_valoraciones',
            )
        }),
        (_('Auditoría'), {
            'classes': ('collapse',),
            'fields': ('fecha_registro', 'ultima_actualizacion')
        }),
    )


@admin.register(Producto)
class ProductoAdmin(admin.ModelAdmin):
    """Configuración del admin para el modelo Producto."""
    list_display = ('id_producto', 'nombre_producto', 'id_vendedor', 'precio', 'stock', 'disponible', 'fecha_creacion')
    list_filter = ('disponible', 'id_vendedor', 'categorias')
    search_fields = ('nombre_producto', 'descripcion', 'id_vendedor__nombre_negocio')
    list_editable = ('precio', 'stock', 'disponible')
    readonly_fields = ('fecha_creacion', 'fecha_actualizacion')
    filter_horizontal = ('categorias',)
    inlines = [ValoracionProductoInline]
    date_hierarchy = 'fecha_creacion'
    fieldsets = (
        (None, {
            'fields': (
                'id_vendedor',
                'nombre_producto',
                'descripcion',
                'categorias',
            )
        }),
        (_('Precio y Disponibilidad'), {
            'fields': (
                'precio',
                'precio_descuento',
                'stock',
                'unidad_medida',
                'disponible',
            )
        }),
        (_('Imágenes'), {
            'fields': ('imagen_principal', 'imagenes_adicionales')
        }),
        (_('Auditoría'), {
            'classes': ('collapse',),
            'fields': ('fecha_creacion', 'fecha_actualizacion')
        }),
    )


@admin.register(Categoria)
class CategoriaAdmin(admin.ModelAdmin):
    """Configuración del admin para el modelo Categoria."""
    list_display = ('id_categoria', 'nombre_categoria', 'descripcion', 'activo')
    list_filter = ('activo',)
    search_fields = ('nombre_categoria', 'descripcion')
    prepopulated_fields = {'slug': ('nombre_categoria',)}
    fieldsets = (
        (None, {
            'fields': (
                'nombre_categoria',
                'slug',
                'descripcion',
                'imagen_categoria',
                'activo',
            )
        }),
    )


@admin.register(ValoracionProducto)
class ValoracionProductoAdmin(admin.ModelAdmin):
    """Configuración del admin para el modelo ValoracionProducto."""
    list_display = ('id_valoracion', 'id_producto', 'id_cliente', 'puntuacion', 'fecha_valoracion')
    list_filter = ('puntuacion', 'fecha_valoracion')
    search_fields = ('id_producto__nombre_producto', 'id_cliente__nombre_cliente', 'comentario')
    readonly_fields = ('fecha_valoracion', 'fecha_actualizacion')
    date_hierarchy = 'fecha_valoracion'
    fieldsets = (
        (None, {
            'fields': (
                'id_producto',
                'id_cliente',
                'puntuacion',
                'comentario',
            )
        }),
        (_('Auditoría'), {
            'classes': ('collapse',),
            'fields': ('fecha_valoracion', 'fecha_actualizacion')
        }),
    )
