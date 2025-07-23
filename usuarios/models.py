from django.db import models
from django.contrib.auth.models import AbstractUser, BaseUserManager, PermissionsMixin
from django.utils.translation import gettext_lazy as _
from django.utils import timezone

class UsuarioManager(BaseUserManager):
    """Manager personalizado para el modelo Usuario."""
    
    def create_user(self, email_usuario, password=None, **extra_fields):
        """Crea y guarda un usuario con el email y contraseña dados."""
        if not email_usuario:
            raise ValueError(_('El email es obligatorio'))
        email_usuario = self.normalize_email(email_usuario)
        user = self.model(email_usuario=email_usuario, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email_usuario, password=None, **extra_fields):
        """Crea y guarda un superusuario con el email y contraseña dados."""
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        extra_fields.setdefault('is_active', True)

        if extra_fields.get('is_staff') is not True:
            raise ValueError(_('Superusuario debe tener is_staff=True.'))
        if extra_fields.get('is_superuser') is not True:
            raise ValueError(_('Superusuario debe tener is_superuser=True.'))

        return self.create_user(email_usuario, password, **extra_fields)

class Usuario(AbstractUser, PermissionsMixin):
    """Modelo de usuario personalizado que coincide con la tabla usuarios existente."""
    
    # Campos del modelo
    id_usuario = models.AutoField(primary_key=True)
    nombre_usuario = models.CharField(_('nombre'), max_length=50)
    apellido_usuario = models.CharField(_('apellido'), max_length=50)
    email_usuario = models.EmailField(_('correo electrónico'), unique=True)
    password = models.CharField(_('contraseña'), max_length=255)
    telefono = models.CharField(_('teléfono'), max_length=20, blank=True, null=True)
    direccion = models.JSONField(_('dirección'), blank=True, null=True)
    fecha_nacimiento = models.DateField(_('fecha de nacimiento'), null=True, blank=True)
    img_usuario = models.TextField(_('imagen de perfil'), blank=True, null=True)
    fecha_registro = models.DateTimeField(_('fecha de registro'), auto_now_add=True)
    ultimo_acceso = models.DateTimeField(_('último acceso'), null=True, blank=True)
    estado = models.BooleanField(_('activo'), default=True)
    
    # Campos para autenticación
    is_active = models.BooleanField(_('activo'), default=True)
    is_staff = models.BooleanField(_('es staff'), default=False)
    is_superuser = models.BooleanField(_('es superusuario'), default=False)
    
    # Especificamos que el campo email_usuario es el que se usará para autenticación
    USERNAME_FIELD = 'email_usuario'
    REQUIRED_FIELDS = ['nombre_usuario', 'apellido_usuario']
    
    objects = UsuarioManager()
    
    class Meta:
        db_table = 'usuarios'
        verbose_name = _('usuario')
        verbose_name_plural = _('usuarios')
    
    def __str__(self):
        return f"{self.nombre_usuario} {self.apellido_usuario} ({self.email_usuario})"
    
    @property
    def nombre_completo(self):
        """Retorna el nombre completo del usuario."""
        return f"{self.nombre_usuario} {self.apellido_usuario}".strip()
    
    def get_short_name(self):
        """Retorna el nombre corto del usuario."""
        return self.nombre_usuario
    
    def get_full_name(self):
        """Retorna el nombre completo del usuario."""
        return self.nombre_completo
    
    def update_last_login(self):
        """Actualiza la fecha del último acceso."""
        self.ultimo_acceso = timezone.now()
        self.save(update_fields=['ultimo_acceso'])
