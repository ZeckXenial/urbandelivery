from django.db import models
from django.utils.translation import gettext_lazy as _

class Auth(models.Model):
    """Modelo para autenticaciones que coincide con la tabla auth existente."""
    
    id_auth = models.AutoField(primary_key=True)
    id_usuario = models.ForeignKey(
        'usuarios.Usuario',
        on_delete=models.CASCADE,
        related_name='autenticaciones',
        verbose_name=_('usuario'),
        db_column='id_usuario'
    )
    fecha_auth = models.DateTimeField(
        _('fecha de autenticación'),
        auto_now_add=True,
        help_text=_('Fecha y hora en que se realizó la autenticación')
    )
    token = models.CharField(
        _('token de autenticación'),
        max_length=255,
        null=True,
        blank=True,
        help_text=_('Token de autenticación si es necesario')
    )
    dispositivo = models.CharField(
        _('dispositivo'),
        max_length=100,
        null=True,
        blank=True,
        help_text=_('Información del dispositivo desde donde se autenticó')
    )
    direccion_ip = models.GenericIPAddressField(
        _('dirección IP'),
        null=True,
        blank=True,
        help_text=_('Dirección IP desde donde se realizó la autenticación')
    )
    activo = models.BooleanField(
        _('activo'),
        default=True,
        help_text=_('Indica si esta sesión está activa')
    )

    class Meta:
        db_table = 'auth'
        verbose_name = _('autenticación')
        verbose_name_plural = _('autenticaciones')
        ordering = ['-fecha_auth']
        indexes = [
            models.Index(fields=['id_usuario', 'activo']),
            models.Index(fields=['fecha_auth']),
        ]

    def __str__(self):
        return f"Autenticación de {self.id_usuario} el {self.fecha_auth}"
    
    def cerrar_sesion(self):
        """Marca la autenticación como inactiva."""
        self.activo = False
        self.save(update_fields=['activo'])
    
    @classmethod
    def obtener_sesiones_activas(cls, usuario):
        """Obtiene todas las sesiones activas de un usuario."""
        return cls.objects.filter(id_usuario=usuario, activo=True).order_by('-fecha_auth')
    
    @classmethod
    def cerrar_otras_sesiones(cls, usuario, sesion_actual_id=None):
        """Cierra todas las demás sesiones activas del usuario excepto la actual."""
        queryset = cls.objects.filter(id_usuario=usuario, activo=True)
        if sesion_actual_id:
            queryset = queryset.exclude(id_auth=sesion_actual_id)
        return queryset.update(activo=False)
