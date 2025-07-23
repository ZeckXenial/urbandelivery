from django.shortcuts import render
from django.views import View
from django.utils.decorators import method_decorator
from django.contrib.auth.decorators import login_required

class HomeView(View):
    """Vista para la página de inicio."""
    def get(self, request, *args, **kwargs):
        context = {
            'title': 'Inicio',
            # Aquí podrías agregar datos dinámicos como ofertas especiales, etc.
        }
        return render(request, 'home.html', context)

class AboutView(View):
    """Vista para la página Acerca de Nosotros."""
    def get(self, request, *args, **kwargs):
        context = {
            'title': 'Acerca de Nosotros',
        }
        return render(request, 'about.html', context)

class ContactView(View):
    """Vista para la página de Contacto."""
    def get(self, request, *args, **kwargs):
        context = {
            'title': 'Contáctanos',
        }
        return render(request, 'contact.html', context)
    
    def post(self, request, *args, **kwargs):
        """Procesa el formulario de contacto"""
        # Aquí iría la lógica para procesar el formulario de contacto
        # Por ahora, simplemente redirigimos a la página de inicio
        from django.shortcuts import redirect
        from django.contrib import messages
        
        # Simulamos un envío exitoso
        messages.success(request, '¡Gracias por contactarnos! Te responderemos a la brevedad.')
        return redirect('home')

@method_decorator(login_required, name='dispatch')
class ProfileView(View):
    """Vista para el perfil del usuario autenticado."""
    def get(self, request, *args, **kwargs):
        """Muestra el perfil del usuario."""
        context = {
            'title': 'Mi Perfil',
            'user': request.user,
        }
        return render(request, 'profile.html', context)
