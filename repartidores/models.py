from django.db import models
from django.conf import settings
from django.utils.translation import gettext_lazy as _
from django.core.validators import MinValueValidator, MaxValueValidator
# from usuarios.models import Usuario


class Repartidor(models.Model):
    """Modelo para repartidores que coincide con la tabla repartidores existente."""
    class EstadoRepartidor(models.TextChoices):
        DISPONIBLE = 'disponible', _('Disponible')
        OCUPADO = 'ocupado', _('Ocupado')
        INACTIVO = 'inactivo', _('Inactivo')
        EN_PAUSA = 'en_pausa', _('En Pausa')
    
    id_repartidor = models.AutoField(primary_key=True)
    # id_usuario = models.OneToOneField(
    #     Usuario,
    #     on_delete=models.CASCADE,
    #     related_name='repartidor_profile',
    #     verbose_name=_('usuario'),
    #     db_column='id_usuario'
    # )
    estado = models.CharField(
        _('estado'),
        max_length=20,
        choices=EstadoRepartidor.choices,
        default=EstadoRepartidor.INACTIVO
    )
    telefono = models.CharField(_('teléfono'), max_length=20, null=True, blank=True)
    ubicacion_actual = models.JSONField(
        _('ubicación actual'),
        null=True,
        blank=True,
        help_text=_('Ubicación actual en formato JSON con latitud y longitud')
    )
    disponibilidad = models.CharField(
        _('disponibilidad'),
        max_length=50,
        default='disponible',
        help_text=_('Estado de disponibilidad del repartidor')
    )
    calificacion_promedio = models.DecimalField(
        _('calificación promedio'),
        max_digits=3,
        decimal_places=2,
        default=0.0,
        validators=[MinValueValidator(0), MaxValueValidator(5)]
    )
    vehiculo = models.JSONField(
        _('vehículo'),
        null=True,
        blank=True,
        help_text=_('Información del vehículo en formato JSON')
    )
    fecha_registro = models.DateTimeField(_('fecha de registro'), auto_now_add=True)
    ultima_actividad = models.DateTimeField(
        _('última actividad'),
        auto_now=True,
        help_text=_('Fecha y hora de la última actividad registrada')
    )
    activo = models.BooleanField(_('activo'), default=True)
    
    class Meta:
        db_table = 'repartidores'
        verbose_name = _('repartidor')
        verbose_name_plural = _('repartidores')
        ordering = ['-fecha_registro']

    def __str__(self):
        return f"{self.id_usuario.nombre_usuario} {self.id_usuario.apellido_usuario} - {self.get_estado_display()}"
    
    @property
    def nombre_completo(self):
        """Retorna el nombre completo del repartidor."""
        return f"{self.id_usuario.nombre_usuario} {self.id_usuario.apellido_usuario}"
    
    def actualizar_ubicacion(self, latitud, longitud):
        """Actualiza la ubicación actual del repartidor."""
        self.ubicacion_actual = {
            'latitud': float(latitud),
            'longitud': float(longitud),
            'fecha_actualizacion': timezone.now().isoformat()
        }
        self.ultima_actividad = timezone.now()
        self.save(update_fields=['ubicacion_actual', 'ultima_actividad'])
    
    def actualizar_estado(self, nuevo_estado):
        """Actualiza el estado del repartidor."""
        if nuevo_estado in dict(self.EstadoRepartidor.choices):
            self.estado = nuevo_estado
            self.ultima_actividad = timezone.now()
            self.save(update_fields=['estado', 'ultima_actividad'])
            return True
        return False


class Vehiculo(models.Model):
    """Modelo para almacenar la información de los vehículos de los repartidores."""
    class TipoVehiculo(models.TextChoices):
        MOTO = 'moto', _('Moto')
        BICICLETA = 'bicicleta', _('Bicicleta')
        AUTO = 'auto', _('Automóvil')
        CAMIONETA = 'camioneta', _('Camioneta')
        PIE = 'pie', _('A pie')
    
    repartidor = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='vehiculos',
        verbose_name=_('repartidor')
    )
    tipo = models.CharField(
        _('tipo de vehículo'),
        max_length=20,
        choices=TipoVehiculo.choices,
        default=TipoVehiculo.MOTO
    )
    marca = models.CharField(_('marca'), max_length=100)
    modelo = models.CharField(_('modelo'), max_length=100)
    anio = models.PositiveIntegerField(_('año'))
    color = models.CharField(_('color'), max_length=50)
    placa = models.CharField(_('placa patente'), max_length=20, unique=True, null=True, blank=True)
    seguro = models.CharField(_('n° de seguro'), max_length=100, blank=True, null=True)
    vencimiento_seguro = models.DateField(_('vencimiento del seguro'), null=True, blank=True)
    foto_vehiculo = models.ImageField(_('foto del vehículo'), upload_to='vehiculos/', null=True, blank=True)
    foto_licencia = models.ImageField(_('foto de la licencia'), upload_to='licencias/', null=True, blank=True)
    licencia = models.CharField(_('n° de licencia'), max_length=50, null=True, blank=True)
    vencimiento_licencia = models.DateField(_('vencimiento de la licencia'), null=True, blank=True)
    activo = models.BooleanField(_('activo'), default=True)
    fecha_creacion = models.DateTimeField(_('fecha de creación'), auto_now_add=True)
    fecha_actualizacion = models.DateTimeField(_('fecha de actualización'), auto_now=True)

    class Meta:
        verbose_name = _('vehículo')
        verbose_name_plural = _('vehículos')
        ordering = ['-activo', 'tipo', 'marca', 'modelo']

    def __str__(self):
        return f"{self.get_tipo_display()} - {self.marca} {self.modelo} ({self.placa or 'Sin placa'})"


class DisponibilidadRepartidor(models.Model):
    """Modelo para gestionar la disponibilidad de los repartidores."""
    repartidor = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='disponibilidad',
        verbose_name=_('repartidor')
    )
    disponible = models.BooleanField(_('disponible'), default=True)
    en_servicio = models.BooleanField(_('en servicio'), default=False)
    ultima_ubicacion = models.JSONField(_('última ubicación'), null=True, blank=True)  # {lat: x, lng: y}
    ultima_actualizacion_ubicacion = models.DateTimeField(_('última actualización de ubicación'), null=True, blank=True)
    radio_entrega = models.PositiveIntegerField(_('radio de entrega (metros)'), default=10000)  # 10km por defecto
    vehiculo_actual = models.ForeignKey(
        Vehiculo,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='disponibilidad_actual',
        verbose_name=_('vehículo actual')
    )
    modo_conexion = models.CharField(_('modo de conexión'), max_length=20, default='online')  # online, offline, pausado
    modo_entrega = models.CharField(_('modo de entrega'), max_length=20, default='normal')  # normal, rapido, programado
    fecha_creacion = models.DateTimeField(_('fecha de creación'), auto_now_add=True)
    fecha_actualizacion = models.DateTimeField(_('fecha de actualización'), auto_now=True)

    class Meta:
        verbose_name = _('disponibilidad de repartidor')
        verbose_name_plural = _('disponibilidad de repartidores')
        ordering = ['-disponible', '-en_servicio']

    def __str__(self):
        return f"{self.repartidor.get_full_name()} - {'Disponible' if self.disponible else 'No disponible'}"


class HistorialUbicacion(models.Model):
    """Modelo para registrar el historial de ubicaciones de los repartidores."""
    id_historial = models.AutoField(primary_key=True)
    repartidor = models.ForeignKey(
        Repartidor,
        on_delete=models.CASCADE,
        related_name='historial_ubicaciones',
        verbose_name=_('repartidor'),
        db_column='id_repartidor'
    )
    latitud = models.DecimalField(
        _('latitud'), 
        max_digits=10, 
        decimal_places=7,
        help_text=_('Coordenada de latitud')
    )
    longitud = models.DecimalField(
        _('longitud'), 
        max_digits=10, 
        decimal_places=7,
        help_text=_('Coordenada de longitud')
    )
    direccion = models.TextField(
        _('dirección'), 
        blank=True, 
        null=True,
        help_text=_('Dirección completa de la ubicación')
    )
    fecha_registro = models.DateTimeField(
        _('fecha de registro'), 
        auto_now_add=True,
        help_text=_('Fecha y hora en que se registró la ubicación')
    )
    precision = models.FloatField(
        _('precisión (metros)'), 
        null=True, 
        blank=True,
        help_text=_('Precisión de la ubicación en metros')
    )
    velocidad = models.FloatField(
        _('velocidad (km/h)'), 
        null=True, 
        blank=True,
        help_text=_('Velocidad en kilómetros por hora')
    )
    direccion_grados = models.FloatField(
        _('dirección en grados'), 
        null=True, 
        blank=True,
        help_text=_('Dirección en grados (0-360)')
    )
    altitud = models.FloatField(
        _('altitud (metros)'), 
        null=True, 
        blank=True,
        help_text=_('Altitud sobre el nivel del mar en metros')
    )
    exactitud_altitud = models.FloatField(
        _('exactitud de altitud (metros)'), 
        null=True, 
        blank=True,
        help_text=_('Exactitud de la altitud en metros')
    )
    proveedor = models.CharField(
        _('proveedor de ubicación'), 
        max_length=50, 
        blank=True, 
        null=True,
        help_text=_('Fuente de la ubicación (GPS, red, etc.)')
    )
    bateria_nivel = models.PositiveIntegerField(
        _('nivel de batería (%)'), 
        null=True, 
        blank=True,
        validators=[MinValueValidator(0), MaxValueValidator(100)],
        help_text=_('Nivel de batería del dispositivo')
    )
    actividad = models.CharField(
        _('actividad detectada'), 
        max_length=50, 
        blank=True, 
        null=True,
        help_text=_('Tipo de actividad detectada (caminando, en vehículo, etc.)')
    )
    confianza_actividad = models.PositiveIntegerField(
        _('confianza de actividad (%)'), 
        null=True, 
        blank=True,
        validators=[MinValueValidator(0), MaxValueValidator(100)],
        help_text=_('Nivel de confianza de la actividad detectada')
    )
    es_simulado = models.BooleanField(
        _('ubicación simulada'), 
        default=False,
        help_text=_('Indica si la ubicación fue simulada')
    )
    datos_brutos = models.JSONField(
        _('datos brutos'), 
        default=dict, 
        blank=True,
        help_text=_('Datos adicionales de la ubicación')
    )

    class Meta:
        db_table = 'historial_ubicaciones'
        verbose_name = _('historial de ubicación')
        verbose_name_plural = _('historial de ubicaciones')
        ordering = ['-fecha_registro']
        indexes = [
            models.Index(fields=['repartidor', '-fecha_registro']),
            models.Index(fields=['fecha_registro']),
        ]

    def __str__(self):
        return f"{self.repartidor.nombre_completo} - {self.fecha_registro}"

    @property
    def coordenadas(self):
        """Retorna las coordenadas como un diccionario."""
        return {
            'latitud': float(self.latitud),
            'longitud': float(self.longitud),
            'precision': float(self.precision) if self.precision else None
        }


class HistorialTrabajo(models.Model):
    """Modelo para registrar el historial de trabajo de los repartidores."""
    class EstadoTrabajo(models.TextChoices):
        INICIADO = 'iniciado', _('Iniciado')
        EN_CURSO = 'en_curso', _('En Curso')
        PAUSADO = 'pausado', _('Pausado')
        COMPLETADO = 'completado', _('Completado')
        CANCELADO = 'cancelado', _('Cancelado')
        FALLIDO = 'fallido', _('Fallido')

    id_historial = models.AutoField(primary_key=True)
    repartidor = models.ForeignKey(
        Repartidor,
        on_delete=models.CASCADE,
        related_name='historial_trabajos',
        verbose_name=_('repartidor'),
        db_column='id_repartidor'
    )
    estado = models.CharField(
        _('estado'),
        max_length=20,
        choices=EstadoTrabajo.choices,
        default=EstadoTrabajo.INICIADO
    )
    fecha_inicio = models.DateTimeField(
        _('fecha de inicio'),
        help_text=_('Fecha y hora de inicio del turno de trabajo')
    )
    fecha_fin = models.DateTimeField(
        _('fecha de fin'),
        null=True,
        blank=True,
        help_text=_('Fecha y hora de finalización del turno de trabajo')
    )
    ubicacion_inicio = models.JSONField(
        _('ubicación de inicio'),
        null=True,
        blank=True,
        help_text=_('Coordenadas de inicio del turno')
    )
    ubicacion_fin = models.JSONField(
        _('ubicación de fin'),
        null=True,
        blank=True,
        help_text=_('Coordenadas de fin del turno')
    )
    distancia_total = models.FloatField(
        _('distancia total (km)'),
        default=0,
        help_text=_('Distancia total recorrida durante el turno')
    )
    tiempo_activo = models.DurationField(
        _('tiempo activo'),
        null=True,
        blank=True,
        help_text=_('Tiempo total activo durante el turno')
    )
    ingresos = models.DecimalField(
        _('ingresos generados'),
        max_digits=10,
        decimal_places=2,
        default=0,
        help_text=_('Ingresos generados durante el turno')
    )
    pedidos_completados = models.PositiveIntegerField(
        _('pedidos completados'),
        default=0,
        help_text=_('Número de pedidos completados durante el turno')
    )
    calificacion_promedio = models.DecimalField(
        _('calificación promedio'),
        max_digits=3,
        decimal_places=2,
        default=0,
        help_text=_('Calificación promedio recibida en el turno')
    )
    notas = models.TextField(
        _('notas'),
        blank=True,
        null=True,
        help_text=_('Notas adicionales sobre el turno')
    )
    dispositivo = models.CharField(
        _('dispositivo'),
        max_length=100,
        blank=True,
        null=True,
        help_text=_('Modelo del dispositivo utilizado')
    )
    sistema_operativo = models.CharField(
        _('sistema operativo'),
        max_length=50,
        blank=True,
        null=True,
        help_text=_('Sistema operativo del dispositivo')
    )
    version_app = models.CharField(
        _('versión de la aplicación'),
        max_length=20,
        blank=True,
        null=True,
        help_text=_('Versión de la aplicación móvil')
    )
    datos_adicionales = models.JSONField(
        _('datos adicionales'),
        default=dict,
        blank=True,
        help_text=_('Datos adicionales en formato JSON')
    )
    fecha_creacion = models.DateTimeField(
        _('fecha de creación'),
        auto_now_add=True
    )
    fecha_actualizacion = models.DateTimeField(
        _('fecha de actualización'),
        auto_now=True
    )

    class Meta:
        db_table = 'historial_trabajo'
        verbose_name = _('historial de trabajo')
        verbose_name_plural = _('historial de trabajos')
        ordering = ['-fecha_inicio']
        indexes = [
            models.Index(fields=['repartidor', '-fecha_inicio']),
            models.Index(fields=['estado', 'fecha_inicio']),
        ]

    def __str__(self):
        return f"{self.repartidor.nombre_completo} - {self.get_estado_display()} ({self.fecha_inicio})"

    def calcular_tiempo_activo(self):
        """Calcula el tiempo activo basado en las fechas de inicio y fin."""
        if self.fecha_inicio and self.fecha_fin:
            self.tiempo_activo = self.fecha_fin - self.fecha_inicio
            self.save(update_fields=['tiempo_activo'])
            return self.tiempo_activo
        return None
        
    def finalizar_turno(self, ubicacion_fin=None):
        """Método para finalizar el turno de trabajo."""
        if not self.fecha_fin:
            self.fecha_fin = timezone.now()
            self.estado = self.EstadoTrabajo.COMPLETADO
            if ubicacion_fin:
                self.ubicacion_fin = ubicacion_fin
            self.save(update_fields=['estado', 'fecha_fin', 'ubicacion_fin'])
            return True
        return False


class ZonaCobertura(models.Model):
    """Modelo para definir las zonas de cobertura de los repartidores."""
    nombre = models.CharField(_('nombre de la zona'), max_length=100)
    descripcion = models.TextField(_('descripción'), blank=True, null=True)
    poligono = models.JSONField(_('coordenadas del polígono'))  # Lista de coordenadas {lat, lng}
    activa = models.BooleanField(_('activa'), default=True)
    radio_metros = models.PositiveIntegerField(_('radio en metros'), help_text=_('Radio circular aproximado en metros'))
    fecha_creacion = models.DateTimeField(_('fecha de creación'), auto_now_add=True)
    fecha_actualizacion = models.DateTimeField(_('fecha de actualización'), auto_now=True)

    class Meta:
        verbose_name = _('zona de cobertura')
        verbose_name_plural = _('zonas de cobertura')
        ordering = ['nombre']

    def __str__(self):
        return self.nombre


class RepartidorZona(models.Model):
    """Modelo para relacionar repartidores con zonas de cobertura."""
    repartidor = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='zonas_asignadas',
        verbose_name=_('repartidor')
    )
    zona = models.ForeignKey(
        ZonaCobertura,
        on_delete=models.CASCADE,
        related_name='repartidores_asignados',
        verbose_name=_('zona de cobertura')
    )
    activo = models.BooleanField(_('activo'), default=True)
    fecha_asignacion = models.DateTimeField(_('fecha de asignación'), auto_now_add=True)
    fecha_actualizacion = models.DateTimeField(_('fecha de actualización'), auto_now=True)

    class Meta:
        verbose_name = _('repartidor por zona')
        verbose_name_plural = _('repartidores por zona')
        unique_together = ('repartidor', 'zona')
        ordering = ['-activo', '-fecha_asignacion']

    def __str__(self):
        return f"{self.repartidor.get_full_name()} - {self.zona.nombre}"
