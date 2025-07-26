from django.db import models
from django.conf import settings
from django.utils.translation import gettext_lazy as _
from django.utils import timezone
from usuarios.models import Usuario


class Cliente(models.Model):
    """Modelo para clientes que coincide con la tabla clientes existente."""
    id_cliente = models.AutoField(primary_key=True)
    nombre_cliente = models.CharField(_('nombre'), max_length=50)
    apellido_cliente = models.CharField(_('apellido'), max_length=50)
    email_cliente = models.EmailField(_('correo electrónico'), unique=True)
    two_factor_auth = models.CharField(
        _('código 2FA'),
        max_length=255,
        null=True,
        blank=True,
        help_text=_('Código de autenticación de dos factores')
    )
    id_usuario = models.OneToOneField(
        Usuario,
        on_delete=models.CASCADE,
        related_name='cliente_profile',
        verbose_name=_('usuario'),
        null=True,
        blank=True,
        db_column='id_usuario',
        help_text=_('Usuario del sistema asociado a este cliente')
    )
    telefono = models.CharField(
        _('teléfono'),
        max_length=20,
        null=True,
        blank=True,
        help_text=_('Número de teléfono de contacto')
    )
    direccion_entrega = models.JSONField(
        _('dirección de entrega'),
        null=True,
        blank=True,
        help_text=_('Direcciones de entrega en formato JSON')
    )
    horario_atencion = models.TextField(
        _('horario de atención'),
        null=True,
        blank=True,
        help_text=_('Horario preferido de atención')
    )
    puntos_fidelidad = models.IntegerField(
        _('puntos de fidelidad'),
        default=0,
        help_text=_('Puntos acumulados en el programa de fidelización')
    )
    fecha_registro = models.DateTimeField(
        _('fecha de registro'),
        auto_now_add=True,
        help_text=_('Fecha en que se registró el cliente')
    )
    ultima_actualizacion = models.DateTimeField(
        _('última actualización'),
        auto_now=True,
        help_text=_('Fecha de la última actualización del perfil')
    )
    activo = models.BooleanField(
        _('activo'),
        default=True,
        help_text=_('Indica si el cliente está activo en el sistema')
    )

    class Meta:
        db_table = 'clientes'
        verbose_name = _('cliente')
        verbose_name_plural = _('clientes')
        ordering = ['apellido_cliente', 'nombre_cliente']

    def __str__(self):
        return f"{self.nombre_cliente} {self.apellido_cliente}"

    @property
    def nombre_completo(self):
        """Retorna el nombre completo del cliente."""
        return f"{self.nombre_cliente} {self.apellido_cliente}".strip()


class Favorito(models.Model):
    """Modelo para almacenar los productos favoritos de un cliente."""
    cliente = models.ForeignKey(
        Cliente,
        on_delete=models.CASCADE,
        related_name='favoritos',
        verbose_name=_('cliente')
    )
    producto = models.ForeignKey(
        'vendedores.Producto',
        on_delete=models.CASCADE,
        related_name='clientes_favoritos',
        verbose_name=_('producto')
    )
    fecha_agregado = models.DateTimeField(_('fecha de agregado'), auto_now_add=True)

    class Meta:
        db_table = 'favoritos'
        verbose_name = _('favorito')
        verbose_name_plural = _('favoritos')
        unique_together = ('cliente', 'producto')
        ordering = ['-fecha_agregado']

    def __str__(self):
        return f"{self.cliente.nombre_completo} - {self.producto.nombre_producto}"
