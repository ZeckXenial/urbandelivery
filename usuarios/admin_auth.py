from django.contrib import admin
from django.utils.translation import gettext_lazy as _
from .models_auth import Auth

@admin.register(Auth)
class AuthAdmin(admin.ModelAdmin):
    """Configuración del admin para el modelo Auth."""
    list_display = ('id_auth', 'id_usuario', 'fecha_auth', 'activo', 'dispositivo', 'direccion_ip')
    list_filter = ('activo', 'fecha_auth')
    search_fields = ('id_usuario__email_usuario', 'dispositivo', 'direccion_ip')
    readonly_fields = ('fecha_auth', 'token')
    date_hierarchy = 'fecha_auth'
    
    fieldsets = (
        (_('Información Básica'), {
            'fields': ('id_usuario', 'activo', 'fecha_auth')
        }),
        (_('Información del Dispositivo'), {
            'fields': ('dispositivo', 'direccion_ip')
        }),
        (_('Tokens'), {
            'classes': ('collapse',),
            'fields': ('token',)
        }),
    )
    
    def has_add_permission(self, request):
        ""
        Deshabilita la creación de autenticaciones desde el admin.
        Las autenticaciones deben crearse a través del proceso de login.
        ""
        return False
    
    def has_change_permission(self, request, obj=None):
        ""
        Solo permite cambiar el estado activo de la autenticación.
        ""
        if obj:
            return request.user.has_perm('usuarios.change_auth')
        return False
    
    def has_delete_permission(self, request, obj=None):
        ""
        Permite eliminar autenticaciones para forzar cierre de sesión.
        ""
        if obj:
            return request.user.has_perm('usuarios.delete_auth')
        return False
