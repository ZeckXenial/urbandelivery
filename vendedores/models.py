from django.db import models
from django.conf import settings
from django.utils.translation import gettext_lazy as _
from django.core.validators import MinValueValidator, MaxValueValidator
from django.utils import timezone
from usuarios.models import Usuario


class Vendedor(models.Model):
    """Modelo para vendedores que coincide con la tabla vendedor existente."""
    
    class EstadoVendedor(models.TextChoices):
        ACTIVO = 'activo', _('Activo')
        INACTIVO = 'inactivo', _('Inactivo')
        SUSPENDIDO = 'suspendido', _('Suspendido')
        PENDIENTE = 'pendiente', _('Pendiente de Aprobación')
    
    id_vendedor = models.AutoField(primary_key=True)
    id_usuario = models.OneToOneField(
        Usuario,
        on_delete=models.CASCADE,
        related_name='vendedor_profile',
        verbose_name=_('usuario'),
        null=True,
        blank=True,
        db_column='id_usuario',
        help_text=_('Usuario del sistema asociado a este vendedor')
    )
    direccion_negocio = models.JSONField(
        _('dirección del negocio'),
        help_text=_('Dirección del negocio en formato JSON'),
        default=dict
    )
    nombre_negocio = models.CharField(
        _('nombre del negocio'),
        max_length=100,
        help_text=_('Nombre comercial del negocio')
    )
    descripcion_negocio = models.TextField(
        _('descripción del negocio'),
        null=True,
        blank=True,
        help_text=_('Descripción detallada del negocio y sus productos')
    )
    img_negocio = models.TextField(
        _('imagen del negocio'),
        null=True,
        blank=True,
        help_text=_('URL o ruta de la imagen del negocio')
    )
    telefono_negocio = models.CharField(
        _('teléfono del negocio'),
        max_length=20,
        null=True,
        blank=True,
        help_text=_('Número de teléfono de contacto del negocio')
    )
    email_negocio = models.EmailField(
        _('correo electrónico del negocio'),
        null=True,
        blank=True,
        help_text=_('Correo electrónico de contacto del negocio')
    )
    horario_atencion = models.JSONField(
        _('horario de atención'),
        null=True,
        blank=True,
        help_text=_('Horario de atención en formato JSON')
    )
    estado = models.CharField(
        _('estado'),
        max_length=20,
        choices=EstadoVendedor.choices,
        default=EstadoVendedor.PENDIENTE,
        help_text=_('Estado actual del vendedor en el sistema')
    )
    calificacion_promedio = models.DecimalField(
        _('calificación promedio'),
        max_digits=3,
        decimal_places=2,
        default=0.0,
        validators=[MinValueValidator(0), MaxValueValidator(5)],
        help_text=_('Calificación promedio basada en las valoraciones de los clientes')
    )
    total_valoraciones = models.PositiveIntegerField(
        _('total de valoraciones'),
        default=0,
        help_text=_('Número total de valoraciones recibidas')
    )
    fecha_registro = models.DateTimeField(
        _('fecha de registro'),
        auto_now_add=True,
        help_text=_('Fecha en que se registró el vendedor')
    )
    ultima_actualizacion = models.DateTimeField(
        _('última actualización'),
        auto_now=True,
        help_text=_('Fecha de la última actualización del perfil')
    )
    activo = models.BooleanField(
        _('activo'),
        default=True,
        help_text=_('Indica si el vendedor está activo en el sistema')
    )

    class Meta:
        db_table = 'vendedor'
        verbose_name = _('vendedor')
        verbose_name_plural = _('vendedores')
        ordering = ['nombre_negocio']

    def __str__(self):
        return self.nombre_negocio


class Categoria(models.Model):
    """Modelo para categorías de productos."""
    id_categoria = models.AutoField(primary_key=True)
    nombre_categoria = models.CharField(_('nombre de la categoría'), max_length=50, unique=True)

    class Meta:
        db_table = 'categorias'
        verbose_name = _('categoría')
        verbose_name_plural = _('categorías')
        ordering = ['nombre_categoria']

    def __str__(self):
        return self.nombre_categoria


class Producto(models.Model):
    """Modelo para productos que coincide con la tabla productos existente."""
    id_producto = models.AutoField(primary_key=True)
    nombre_producto = models.CharField(_('nombre del producto'), max_length=100)
    descripcion = models.TextField(_('descripción'), null=True, blank=True)
    precio_producto = models.DecimalField(
        _('precio del producto'),
        max_digits=10,
        decimal_places=2
    )
    stock_producto = models.IntegerField(
        _('stock del producto'),
        default=0,
        help_text=_('Cantidad disponible en inventario')
    )
    img_producto = models.TextField(
        _('imagen del producto'),
        null=True,
        blank=True,
        help_text=_('URL o ruta de la imagen del producto')
    )
    id_vendedor = models.ForeignKey(
        Vendedor,
        on_delete=models.CASCADE,
        related_name='productos',
        verbose_name=_('vendedor'),
        db_column='id_vendedor'
    )
    id_categoria = models.ForeignKey(
        Categoria,
        on_delete=models.SET_NULL,
        related_name='productos',
        verbose_name=_('categoría'),
        null=True,
        blank=True,
        db_column='id_categoria'
    )
    fecha_creacion = models.DateTimeField(_('fecha de creación'), auto_now_add=True)
    fecha_actualizacion = models.DateTimeField(_('fecha de actualización'), auto_now=True)
    activo = models.BooleanField(_('activo'), default=True)

    class Meta:
        db_table = 'productos'
        verbose_name = _('producto')
        verbose_name_plural = _('productos')
        ordering = ['nombre_producto']
        indexes = [
            models.Index(fields=['id_vendedor', 'activo']),
            models.Index(fields=['id_categoria', 'activo']),
        ]

    def __str__(self):
        return f"{self.nombre_producto} - {self.id_vendedor.nombre_negocio}"

    @property
    def en_stock(self):
        """Indica si el producto está en stock."""
        return self.stock_producto > 0


class ValoracionProducto(models.Model):
    """Modelo para valoraciones de productos."""
    id_valoracion = models.AutoField(primary_key=True)
    id_producto = models.ForeignKey(
        Producto,
        on_delete=models.CASCADE,
        related_name='valoraciones',
        verbose_name=_('producto'),
        db_column='id_producto'
    )
    id_cliente = models.ForeignKey(
        'clientes.Cliente',
        on_delete=models.SET_NULL,
        related_name='valoraciones',
        verbose_name=_('cliente'),
        null=True,
        blank=True,
        db_column='id_cliente'
    )
    valoracion = models.JSONField(
        _('valoración'),
        help_text=_('Detalles de la valoración en formato JSON')
    )
    fecha_valoracion = models.DateTimeField(_('fecha de valoración'), auto_now_add=True)
    comentario = models.TextField(_('comentario'), null=True, blank=True)
    aprobado = models.BooleanField(_('aprobado'), default=False)

    class Meta:
        db_table = 'valoracion_producto'
        verbose_name = _('valoración de producto')
        verbose_name_plural = _('valoraciones de productos'
    )
        ordering = ['-fecha_valoracion']

    def __str__(self):
        return f"Valoración de {self.id_producto.nombre_producto} por {self.id_cliente.nombre_completo if self.id_cliente else 'Anónimo'}"
