from django.db import models
from django.utils.translation import gettext_lazy as _
from django.utils import timezone
from django.core.validators import MinValueValidator
from clientes.models import Cliente
from vendedores.models import Vendedor, Producto
from repartidores.models import Repartidor
from .db_utils import JSONFieldExtended, JSONFieldMixin, SQLViewMixin


class Pedido(JSONFieldMixin, models.Model):
    """
    Modelo para la tabla 'pedidos' que representa los pedidos realizados por los clientes.
    """
    class EstadoPedido(models.TextChoices):
        PENDIENTE = 'pendiente', _('Pendiente')
        CONFIRMADO = 'confirmado', _('Confirmado')
        EN_PREPARACION = 'en_preparacion', _('En Preparación')
        LISTO_PARA_ENVIO = 'listo_para_envio', _('Listo para Envío')
        EN_CAMINO = 'en_camino', _('En Camino')
        ENTREGADO = 'entregado', _('Entregado')
        CANCELADO = 'cancelado', _('Cancelado')
        RECHAZADO = 'rechazado', _('Rechazado')
    
    class MetodoPago(models.TextChoices):
        EFECTIVO = 'efectivo', _('Efectivo')
        TARJETA = 'tarjeta', _('Tarjeta de Crédito/Débito')
        TRANSFERENCIA = 'transferencia', _('Transferencia Bancaria')
        MERCADO_PAGO = 'mercado_pago', _('Mercado Pago')
        OTRO = 'otro', _('Otro')
    
    id_pedido = models.AutoField(primary_key=True, verbose_name=_('ID del Pedido'))
    id_cliente = models.ForeignKey(
        Cliente,
        on_delete=models.PROTECT,
        related_name='pedidos',
        verbose_name=_('Cliente')
    )
    id_vendedor = models.ForeignKey(
        Vendedor,
        on_delete=models.PROTECT,
        related_name='pedidos_recibidos',
        verbose_name=_('Vendedor')
    )
    id_repartidor = models.ForeignKey(
        Repartidor,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='pedidos_asignados',
        verbose_name=_('Repartidor')
    )
    fecha_pedido = models.DateTimeField(_('Fecha del Pedido'), default=timezone.now)
    fecha_entrega = models.DateTimeField(_('Fecha de Entrega'), null=True, blank=True)
    estado_pedido = JSONFieldExtended(_('Estado del Pedido'), default=dict)
    direccion_pedido = JSONFieldExtended(_('Dirección de Entrega'), default=dict)
    metodo_pago = models.CharField(
        _('Método de Pago'),
        max_length=20,
        choices=MetodoPago.choices,
        default=MetodoPago.EFECTIVO
    )
    instrucciones_entrega = models.TextField(_('Instrucciones de Entrega'), blank=True)
    total = models.DecimalField(_('Total'), max_digits=10, decimal_places=2, default=0.00)
    two_factor_auth = models.BooleanField(_('Autenticación en Dos Pasos'), default=False)
    fecha_creacion = models.DateTimeField(_('Fecha de Creación'), auto_now_add=True)
    fecha_actualizacion = models.DateTimeField(_('Última Actualización'), auto_now=True)

    class Meta:
        db_table = 'pedidos'
        verbose_name = _('Pedido')
        verbose_name_plural = _('Pedidos')
        ordering = ['-fecha_pedido']
        indexes = [
            models.Index(fields=['fecha_pedido']),
            models.Index(fields=['estado_pedido'], name='idx_estado_pedido'),
            models.Index(fields=['id_cliente', 'id_vendedor']),
        ]

    def __str__(self):
        return f"Pedido #{self.id_pedido} - {self.get_estado_actual_display()}"
    
    def get_estado_actual(self):
        """
        Obtiene el estado actual del pedido.
        """
        if not self.estado_pedido:
            return self.EstadoPedido.PENDIENTE
        
        # Ordena los estados por fecha y devuelve el más reciente
        estados_ordenados = sorted(
            self.estado_pedido.items(),
            key=lambda x: x[1]['fecha'],
            reverse=True
        )
        return estados_ordenados[0][0] if estados_ordenados else self.EstadoPedido.PENDIENTE
    
    def get_estado_actual_display(self):
        """
        Obtiene la representación legible del estado actual.
        """
        estado_actual = self.get_estado_actual()
        return dict(self.EstadoPedido.choices).get(estado_actual, estado_actual)
    
    def actualizar_estado(self, nuevo_estado, notas='', usuario=None):
        """
        Actualiza el estado del pedido con un nuevo estado.
        """
        if nuevo_estado not in dict(self.EstadoPedido.choices):
            raise ValueError(f"Estado '{nuevo_estado}' no válido")
        
        self.update_json_field('estado_pedido', {
            nuevo_estado: {
                'fecha': timezone.now().isoformat(),
                'notas': notas,
                'usuario': str(usuario) if usuario else 'sistema'
            }
        })
        
        # Si el estado es ENTREGADO, actualizar la fecha de entrega
        if nuevo_estado == self.EstadoPedido.ENTREGADO and not self.fecha_entrega:
            self.fecha_entrega = timezone.now()
            self.save(update_fields=['estado_pedido', 'fecha_entrega', 'fecha_actualizacion'])
        else:
            self.save(update_fields=['estado_pedido', 'fecha_actualizacion'])
    
    def get_historial_estados(self):
        """
        Devuelve el historial de estados ordenados por fecha.
        """
        if not self.estado_pedido:
            return []
            
        return sorted(
            [
                {
                    'estado': estado,
                    'estado_display': dict(self.EstadoPedido.choices).get(estado, estado),
                    **datos
                }
                for estado, datos in self.estado_pedido.items()
            ],
            key=lambda x: x['fecha'],
            reverse=True
        )
    
    def calcular_total(self):
        """
        Calcula el total del pedido sumando los subtotales de los detalles.
        """
        total = sum(detalle.subtotal for detalle in self.detalles.all())
        self.total = total
        self.save(update_fields=['total', 'fecha_actualizacion'])
        return total
    
    def get_direccion_formateada(self):
        """
        Devuelve la dirección de entrega formateada.
        """
        if not self.direccion_pedido:
            return ""
        
        direccion = self.direccion_pedido
        partes = [
            direccion.get('calle', ''),
            direccion.get('numero', ''),
            direccion.get('piso', ''),
            direccion.get('depto', ''),
            direccion.get('localidad', ''),
            direccion.get('provincia', ''),
            direccion.get('codigo_postal', '')
        ]
        return ", ".join(filter(None, partes))


class DetallePedido(models.Model):
    """
    Modelo para la tabla 'detalle_pedido' que contiene los productos de cada pedido.
    """
    id_detalle = models.AutoField(primary_key=True, verbose_name=_('ID del Detalle'))
    id_pedido = models.ForeignKey(
        Pedido,
        on_delete=models.CASCADE,
        related_name='detalles',
        verbose_name=_('Pedido')
    )
    id_producto = models.ForeignKey(
        Producto,
        on_delete=models.PROTECT,
        related_name='detalles_pedido',
        verbose_name=_('Producto')
    )
    cantidad_producto = models.PositiveIntegerField(
        _('Cantidad'),
        validators=[MinValueValidator(1)]
    )
    precio_unitario = models.DecimalField(
        _('Precio Unitario'),
        max_digits=10,
        decimal_places=2
    )
    subtotal = models.DecimalField(
        _('Subtotal'),
        max_digits=12,
        decimal_places=2,
        editable=False
    )
    notas = models.TextField(_('Notas'), blank=True)
    fecha_creacion = models.DateTimeField(_('Fecha de Creación'), auto_now_add=True)
    fecha_actualizacion = models.DateTimeField(_('Última Actualización'), auto_now=True)

    class Meta:
        db_table = 'detalle_pedido'
        verbose_name = _('Detalle de Pedido')
        verbose_name_plural = _('Detalles de Pedidos')
        ordering = ['-fecha_creacion']
        indexes = [
            models.Index(fields=['id_pedido', 'id_producto']),
        ]
        constraints = [
            models.UniqueConstraint(
                fields=['id_pedido', 'id_producto'],
                name='unique_producto_por_pedido'
            )
        ]

    def __str__(self):
        return f"{self.cantidad_producto}x {self.id_producto} - ${self.subtotal}"
    
    def save(self, *args, **kwargs):
        """
        Sobrescribes el método save para calcular el subtotal antes de guardar.
        """
        # Si es un nuevo registro o se actualizó la cantidad o el precio
        if not self.pk or 'cantidad_producto' in kwargs.get('update_fields', []) or 'precio_unitario' in kwargs.get('update_fields', []):
            self.subtotal = self.calcular_subtotal()
        
        super().save(*args, **kwargs)
        
        # Actualizar el total del pedido
        if hasattr(self, 'id_pedido'):
            self.id_pedido.calcular_total()
    
    def delete(self, *args, **kwargs):
        """
        Sobrescribes el método delete para actualizar el total del pedido.
        """
        pedido = getattr(self, 'id_pedido', None)
        super().delete(*args, **kwargs)
        
        # Actualizar el total del pedido si existe
        if pedido:
            pedido.calcular_total()
    
    def calcular_subtotal(self):
        """
        Calcula el subtotal del detalle del pedido.
        """
        return self.cantidad_producto * self.precio_unitario
    
    def get_precio_unitario_display(self):
        """
        Devuelve el precio unitario formateado como moneda.
        """
        return f"${self.precio_unitario:,.2f}"
    
    def get_subtotal_display(self):
        """
        Devuelve el subtotal formateado como moneda.
        """
        return f"${self.subtotal:,.2f}"
