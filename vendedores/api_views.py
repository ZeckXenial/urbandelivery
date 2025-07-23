from rest_framework import status, viewsets, permissions
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework_simplejwt.authentication import JWTAuthentication
from django.shortcuts import get_object_or_404
import json
from datetime import datetime, timedelta

class VendedorViewSet(viewsets.ViewSet):
    """
    API endpoints para vendedores (restaurantes)
    """
    authentication_classes = [JWTAuthentication]
    permission_classes = [permissions.IsAuthenticated]

    @action(detail=False, methods=['get'])
    def dashboard(self, request):
        """Obtener datos del dashboard del vendedor"""
        # Datos simulados
        hoy = datetime.now().date()
        ultimos_7_dias = [hoy - timedelta(days=i) for i in range(6, -1, -1)]
        
        dashboard_data = {
            'resumen': {
                'ventas_hoy': 125000,
                'pedidos_hoy': 15,
                'nuevos_clientes': 8,
                'valoracion_promedio': 4.5
            },
            'ventas_ultimos_7_dias': [
                {'fecha': dia.strftime('%Y-%m-%d'), 'ventas': 10000 + (i * 2000)}
                for i, dia in enumerate(ultimos_7_dias)
            ],
            'pedidos_recientes': [
                {
                    'id': 1001 + i,
                    'cliente': f'Cliente {i}',
                    'hora': (datetime.now() - timedelta(minutes=30*i)).strftime('%H:%M'),
                    'total': 15000 + (i * 2000),
                    'estado': ['pendiente', 'en_preparacion', 'en_camino', 'entregado'][i % 4]
                }
                for i in range(5)
            ]
        }
        return Response(dashboard_data)

    @action(detail=False, methods=['get'])
    def pedidos(self, request):
        """Obtener lista de pedidos del restaurante"""
        # Filtros simulados
        estado = request.query_params.get('estado', None)
        fecha_inicio = request.query_params.get('fecha_inicio', None)
        fecha_fin = request.query_params.get('fecha_fin', None)
        
        # Datos simulados
        pedidos = [
            {
                'id': 1001 + i,
                'fecha': (datetime.now() - timedelta(hours=i)).isoformat(),
                'cliente': f'Cliente {i}',
                'estado': ['pendiente', 'en_preparacion', 'en_camino', 'entregado', 'cancelado'][i % 5],
                'total': 15000 + (i * 1500),
                'detalle': [
                    {'producto': f'Producto {j+1}', 'cantidad': 1 + (i + j) % 3, 'precio': 5000 + (j * 1000)}
                    for j in range(1 + (i % 3))
                ]
            }
            for i in range(10)
        ]
        
        # Aplicar filtros simulados
        if estado:
            pedidos = [p for p in pedidos if p['estado'] == estado]
            
        return Response(pedidos)

    @action(detail=True, methods=['post'])
    def actualizar_estado_pedido(self, request, pk=None):
        """Actualizar el estado de un pedido"""
        nuevo_estado = request.data.get('estado')
        
        if not nuevo_estado:
            return Response(
                {'error': 'El campo estado es requerido'},
                status=status.HTTP_400_BAD_REQUEST
            )
            
        # En producción, aquí se actualizaría el estado en la base de datos
        pedido = {
            'id': pk,
            'estado': nuevo_estado,
            'mensaje': f'Estado actualizado a {nuevo_estado}'
        }
        
        return Response(pedido)

    @action(detail=False, methods=['get'])
    def menu(self, request):
        """Obtener el menú del restaurante"""
        menu = {
            'restaurante': 'Mi Restaurante',
            'categorias': [
                {
                    'id': 1,
                    'nombre': 'Entradas',
                    'productos': [
                        {'id': 101, 'nombre': 'Empanadas', 'descripcion': 'Empanadas de pino', 'precio': 2000, 'disponible': True},
                        {'id': 102, 'nombre': 'Palitos de queso', 'descripcion': 'Palitos de queso horneados', 'precio': 3500, 'disponible': True}
                    ]
                },
                {
                    'id': 2,
                    'nombre': 'Platos Principales',
                    'productos': [
                        {'id': 201, 'nombre': 'Lomo a lo pobre', 'descripcion': 'Lomo con huevo frito, cebolla y papas fritas', 'precio': 8500, 'disponible': True},
                        {'id': 202, 'nombre': 'Parrillada para dos', 'descripcion': 'Variedad de carnes y embutidos', 'precio': 15000, 'disponible': True}
                    ]
                },
                {
                    'id': 3,
                    'nombre': 'Postres',
                    'productos': [
                        {'id': 301, 'nombre': 'Mousse de chocolate', 'descripcion': 'Delicioso postre de chocolate', 'precio': 3500, 'disponible': True},
                        {'id': 302, 'nombre': 'Tres leches', 'descripcion': 'Bizcocho bañado en leche', 'precio': 3000, 'disponible': False}
                    ]
                }
            ]
        }
        return Response(menu)
