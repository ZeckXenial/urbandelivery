from rest_framework import status, viewsets, permissions
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework_simplejwt.authentication import JWTAuthentication
from django.shortcuts import get_object_or_404
from datetime import datetime, timedelta
import random

class RepartidorViewSet(viewsets.ViewSet):
    """
    API endpoints para repartidores
    """
    authentication_classes = [JWTAuthentication]
    permission_classes = [permissions.IsAuthenticated]

    @action(detail=False, methods=['get'])
    def estado(self, request):
        """Obtener estado actual del repartidor"""
        # En producción, esto vendría de la base de datos
        estado_repartidor = {
            'id': request.user.id,
            'nombre': f"{request.user.first_name} {request.user.last_name}",
            'estado': 'disponible',  # disponible, en_ruta, en_entrega, no_disponible
            'ubicacion_actual': {
                'lat': -33.4489 + random.uniform(-0.01, 0.01),  # Ubicación aleatoria cerca de Santiago
                'lng': -70.6693 + random.uniform(-0.01, 0.01)
            },
            'pedido_actual': None,
            'calificacion': 4.7,
            'total_entregas': 128,
            'vehiculo': {
                'tipo': 'moto',
                'patente': 'XX-YY-12',
                'marca': 'Yamaha',
                'modelo': 'FZ 2.0'
            }
        }
        return Response(estado_repartidor)

    @action(detail=False, methods=['get'])
    def pedidos_disponibles(self, request):
        """Obtener lista de pedidos disponibles para tomar"""
        # En producción, esto vendría de la base de datos con filtros de ubicación, etc.
        pedidos = [
            {
                'id': 500 + i,
                'restaurante': f'Restaurante {i+1}',
                'direccion_restaurante': f'Calle {i+1} #123, Santiago',
                'direccion_entrega': f'Av. Principal {1000 + i}, Santiago',
                'distancia': round(1.5 + (i * 0.3), 1),  # km
                'tiempo_estimado': 15 + (i * 3),  # minutos
                'monto': 8000 + (i * 1000),
                'items': [
                    'Combo Familiar' if i % 2 == 0 else 'Menú Ejecutivo',
                    'Bebida 1.5L'
                ]
            }
            for i in range(5)
        ]
        return Response(pedidos)

    @action(detail=True, methods=['post'])
    def tomar_pedido(self, request, pk=None):
        """Tomar un pedido disponible"""
        # En producción, aquí se asignaría el pedido al repartidor
        pedido = {
            'id': pk,
            'estado': 'en_camino',
            'mensaje': f'Pedido {pk} asignado correctamente',
            'detalles': {
                'restaurante': 'Restaurante Ejemplo',
                'direccion_restaurante': 'Calle Ejemplo 123, Santiago',
                'cliente': 'Juan Pérez',
                'direccion_entrega': 'Av. Principal 456, Santiago',
                'telefono_cliente': '+56912345678',
                'items': [
                    {'nombre': 'Combo Familiar', 'cantidad': 1},
                    {'nombre': 'Bebida 1.5L', 'cantidad': 2}
                ],
                'total': 12000,
                'instrucciones_especiales': 'Tocar timbre 2 veces',
                'hora_estimada_entrega': (datetime.now() + timedelta(minutes=25)).strftime('%H:%M')
            }
        }
        return Response(pedido)

    @action(detail=True, methods=['post'])
    def actualizar_estado(self, request, pk=None):
        """Actualizar el estado de un pedido (en_camino, entregado, etc.)"""
        nuevo_estado = request.data.get('estado')
        
        if not nuevo_estado:
            return Response(
                {'error': 'El campo estado es requerido'},
                status=status.HTTP_400_BAD_REQUEST
            )
            
        # En producción, aquí se actualizaría el estado en la base de datos
        respuesta = {
            'pedido_id': pk,
            'estado_anterior': 'en_camino',
            'estado_nuevo': nuevo_estado,
            'hora_actualizacion': datetime.now().isoformat(),
            'mensaje': f'Estado del pedido actualizado a: {nuevo_estado}'
        }
        
        return Response(respuesta)

    @action(detail=False, methods=['get'])
    def historial(self, request):
        """Obtener historial de entregas del repartidor"""
        # Filtros simulados
        fecha_inicio = request.query_params.get('fecha_inicio')
        fecha_fin = request.query_params.get('fecha_fin')
        
        # Datos simulados
        historial = [
            {
                'id': 100 + i,
                'fecha': (datetime.now() - timedelta(days=i)).strftime('%Y-%m-%d'),
                'restaurante': f'Restaurante {i % 5 + 1}',
                'cliente': f'Cliente {i}',
                'monto': 8000 + (i * 500),
                'propina': 1000 if i % 3 == 0 else 500,
                'calificacion': random.randint(3, 5),
                'estado': 'entregado'
            }
            for i in range(10)
        ]
        
        # Aplicar filtros simulados
        if fecha_inicio:
            historial = [h for h in historial if h['fecha'] >= fecha_inicio]
        if fecha_fin:
            historial = [h for h in historial if h['fecha'] <= fecha_fin]
            
        return Response(historial)

    @action(detail=False, methods=['post'])
    def actualizar_ubicacion(self, request):
        """Actualizar la ubicación actual del repartidor"""
        lat = request.data.get('lat')
        lng = request.data.get('lng')
        
        if not lat or not lng:
            return Response(
                {'error': 'Las coordenadas de latitud y longitud son requeridas'},
                status=status.HTTP_400_BAD_REQUEST
            )
            
        # En producción, aquí se actualizaría la ubicación en tiempo real
        respuesta = {
            'mensaje': 'Ubicación actualizada correctamente',
            'ubicacion': {
                'lat': float(lat),
                'lng': float(lng),
                'hora_actualizacion': datetime.now().isoformat()
            }
        }
        
        return Response(respuesta)
