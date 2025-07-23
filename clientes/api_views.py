from rest_framework import status, viewsets, permissions
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework_simplejwt.authentication import JWTAuthentication
from django.shortcuts import get_object_or_404
import json

class ClienteViewSet(viewsets.ViewSet):
    """
    API endpoints para clientes
    """
    authentication_classes = [JWTAuthentication]
    permission_classes = [permissions.IsAuthenticated]

    @action(detail=False, methods=['get'])
    def perfil(self, request):
        """Obtener perfil del cliente autenticado"""
        # En un entorno real, esto vendría de la base de datos
        perfil = {
            'id': request.user.id,
            'nombre': request.user.get_full_name(),
            'email': request.user.email,
            'telefono': '+56912345678',
            'direccion': 'Calle Falsa 123, Santiago',
            'fecha_registro': '2023-01-15T00:00:00Z',
            'preferencias': {
                'notificaciones': True,
                'tema_oscuro': False,
                'idioma': 'es'
            }
        }
        return Response(perfil)

    @action(detail=False, methods=['get'])
    def pedidos(self, request):
        """Obtener historial de pedidos del cliente"""
        # Datos simulados - en producción vendrían de la base de datos
        pedidos = [
            {
                'id': 1,
                'fecha': '2023-05-15T14:30:00Z',
                'restaurante': 'Pizza Hut',
                'estado': 'entregado',
                'total': 12500,
                'productos': [
                    {'nombre': 'Pizza Familiar', 'cantidad': 1, 'precio': 10000},
                    {'nombre': 'Bebida 1.5L', 'cantidad': 1, 'precio': 2500}
                ]
            },
            {
                'id': 2,
                'fecha': '2023-05-10T20:15:00Z',
                'restaurante': 'Sushi Express',
                'estado': 'cancelado',
                'total': 8900,
                'productos': [
                    {'nombre': 'Combo Sushi 20 piezas', 'cantidad': 1, 'precio': 8900}
                ]
            }
        ]
        return Response(pedidos)

    @action(detail=False, methods=['get'])
    def direcciones(self, request):
        """Obtener direcciones guardadas del cliente"""
        direcciones = [
            {
                'id': 1,
                'alias': 'Casa',
                'direccion': 'Calle Falsa 123, Santiago',
                    'coordenadas': {
                    'lat': -33.45694,
                    'lng': -70.64827
                },
                'es_principal': True
            },
            {
                'id': 2,
                'alias': 'Trabajo',
                'direccion': 'Av. Providencia 1234, Providencia',
                'coordenadas': {
                    'lat': -33.43148,
                    'lng': -70.62472
                },
                'es_principal': False
            }
        ]
        return Response(direcciones)
