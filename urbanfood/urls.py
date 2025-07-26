"""
URL configuration for urbanfood project.
"""
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.views.generic import RedirectView
from django.contrib.auth import views as auth_views
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
    TokenVerifyView,
)

# Importar vistas locales
from . import views as core_views

# API URLS
api_urlpatterns = [
    # API Base
    path('api/', include('api.urls')),
    
    # API Clientes
    path('api/clientes/', include('clientes.api_urls')),
    
    # API Vendedores
    path('api/vendedores/', include('vendedores.api_urls')),
    
    # API Repartidores
    path('api/repartidores/', include('repartidores.api_urls')),
    
    # API Pedidos
    path('api/pedidos/', include('pedidos.urls')),
    
    # API Autenticación JWT
    path('api/token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('api/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('api/token/verify/', TokenVerifyView.as_view(), name='token_verify'),
]

# URLS de autenticación de Django REST Framework
rest_auth_urls = [
    path('api/auth/', include('rest_framework.urls')),
]

# URLS de autenticación de Django
auth_urls = [
    path('iniciar-sesion/', auth_views.LoginView.as_view(template_name='auth/login.html'), name='login'),
    path('cerrar-sesion/', auth_views.LogoutView.as_view(next_page='home'), name='logout'),
    path('cambiar-password/', auth_views.PasswordChangeView.as_view(
        template_name='auth/change_password.html',
        success_url='/'
    ), name='password_change'),
    path('restablecer-password/', auth_views.PasswordResetView.as_view(
        template_name='auth/password_reset.html',
        email_template_name='auth/emails/password_reset_email.html',
        subject_template_name='auth/emails/password_reset_subject.txt'
    ), name='password_reset'),
    path('restablecer-password/hecho/', auth_views.PasswordResetDoneView.as_view(
        template_name='auth/password_reset_done.html'
    ), name='password_reset_done'),
    path('restablecer-password/confirmar/<uidb64>/<token>/', auth_views.PasswordResetConfirmView.as_view(
        template_name='auth/password_reset_confirm.html'
    ), name='password_reset_confirm'),
    path('restablecer-password/completo/', auth_views.PasswordResetCompleteView.as_view(
        template_name='auth/password_reset_complete.html'
    ), name='password_reset_complete'),
]

# URLS principales del sitio
urlpatterns = [
    # Páginas principales
    path('', core_views.HomeView.as_view(), name='home'),
    path('acerca-de/', core_views.AboutView.as_view(), name='about'),
    path('contacto/', core_views.ContactView.as_view(), name='contact'),
    
    # Autenticación
    path('cuenta/', include(auth_urls)),
    
    # Perfil de usuario
    path('perfil/', core_views.ProfileView.as_view(), name='profile'),
    
    # Clientes
    path('cliente/', include('clientes.urls', namespace='clientes')),
    
    # Admin
    path('admin/', admin.site.urls),
    
    # API
    *api_urlpatterns,
    
    # Autenticación API
    *rest_auth_urls,
    
    # Redireccionar favicon.ico
    path('favicon.ico', RedirectView.as_view(url=settings.STATIC_URL + 'img/favicon.ico')),
]

# Configuración para servir archivos estáticos en desarrollo
if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    
    # Debug toolbar (solo en desarrollo)
    if 'debug_toolbar' in settings.INSTALLED_APPS:
        import debug_toolbar
        urlpatterns = [
            path('__debug__/', include(debug_toolbar.urls)),
        ] + urlpatterns
