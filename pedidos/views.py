from rest_framework import viewsets, status, permissions, filters
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, IsAdminUser
from django_filters.rest_framework import DjangoFilterBackend
from django.shortcuts import get_object_or_404
from django.db import transaction
from django.utils import timezone

from .models import Pedido, DetallePedido
from .serializers import (
    PedidoSerializer, 
    DetallePedidoSerializer,
    PedidoCreateSerializer,
    PedidoUpdateSerializer,
    DetallePedidoCreateUpdateSerializer
)
from .permissions import (
    IsClienteOwner, 
    IsVendedorOwner, 
    IsRepartidorOrVendedor,
    IsClienteOrVendedor
)


class PedidoViewSet(viewsets.ModelViewSet):
    """
    API endpoint que permite ver y editar pedidos.
    """
    queryset = Pedido.objects.all()
    serializer_class = PedidoSerializer
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter, filters.SearchFilter]
    filterset_fields = {
        'estado_pedido': ['exact', 'contains'],
        'fecha_pedido': ['gte', 'lte', 'exact'],
        'id_cliente': ['exact'],
        'id_vendedor': ['exact'],
        'id_repartidor': ['exact'],
        'metodo_pago': ['exact'],
    }
    ordering_fields = ['fecha_pedido', 'total', 'fecha_entrega']
    search_fields = ['id_pedido', 'id_cliente__nombre_cliente', 'id_vendedor__nombre_negocio']
    ordering = ['-fecha_pedido']

    def get_serializer_class(self):
        """
        Retorna el serializador apropiado según la acción.
        """
        if self.action == 'create':
            return PedidoCreateSerializer
        elif self.action in ['update', 'partial_update']:
            return PedidoUpdateSerializer
        return self.serializer_class

    def get_permissions(self):
        """
        Instancia y retorna la lista de permisos que requiere la vista.
        """
        if self.action in ['list', 'retrieve']:
            permission_classes = [IsAuthenticated]
        elif self.action == 'create':
            permission_classes = [IsAuthenticated, IsClienteOwner]
        elif self.action in ['update', 'partial_update', 'cambiar_estado']:
            permission_classes = [IsAuthenticated, IsVendedorOwner | IsAdminUser]
        elif self.action == 'asignar_repartidor':
            permission_classes = [IsAuthenticated, IsVendedorOwner | IsAdminUser]
        elif self.action == 'marcar_entregado':
            permission_classes = [IsAuthenticated, IsRepartidorOrVendedor]
        else:
            permission_classes = [IsAdminUser]
        
        return [permission() for permission in permission_classes]

    def get_queryset(self):
        """
        Filtra los pedidos según el tipo de usuario.
        """
        user = self.request.user
        queryset = super().get_queryset()

        # Si es administrador, ve todos los pedidos
        if user.is_staff:
            return queryset
        
        # Si es cliente, solo ve sus propios pedidos
        if hasattr(user, 'cliente_profile'):
            return queryset.filter(id_cliente=user.cliente_profile)
        
        # Si es vendedor, ve los pedidos de su negocio
        if hasattr(user, 'vendedor_profile'):
            return queryset.filter(id_vendedor=user.vendedor_profile)
        
        # Si es repartidor, ve los pedidos asignados a él
        if hasattr(user, 'repartidor_profile'):
            return queryset.filter(id_repartidor=user.repartidor_profile)
        
        return queryset.none()

    @transaction.atomic
    def create(self, request, *args, **kwargs):
        """
        Crea un nuevo pedido con sus detalles.
        """
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        with transaction.atomic():
            # Crear el pedido
            pedido = serializer.save()
            
            # Crear los detalles del pedido
            detalles_data = request.data.get('detalles', [])
            for detalle_data in detalles_data:
                detalle_serializer = DetallePedidoCreateUpdateSerializer(data=detalle_data)
                detalle_serializer.is_valid(raise_exception=True)
                DetallePedido.objects.create(
                    id_pedido=pedido,
                    **detalle_serializer.validated_data
                )
            
            # Calcular el total del pedido
            pedido.calcular_total()
            
            # Actualizar el estado inicial del pedido
            pedido.actualizar_estado(
                Pedido.EstadoPedido.PENDIENTE,
                'Pedido creado',
                request.user
            )
        
        headers = self.get_success_headers(serializer.data)
        return Response(
            self.serializer_class(pedido).data,
            status=status.HTTP_201_CREATED,
            headers=headers
        )

    @action(detail=True, methods=['post'])
    def cambiar_estado(self, request, pk=None):
        """
        Acción personalizada para cambiar el estado de un pedido.
        """
        pedido = self.get_object()
        nuevo_estado = request.data.get('estado')
        notas = request.data.get('notas', '')
        
        if not nuevo_estado:
            return Response(
                {'error': 'El campo "estado" es requerido'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            pedido.actualizar_estado(nuevo_estado, notas, request.user)
            return Response({'status': 'Estado actualizado correctamente'})
        except ValueError as e:
            return Response(
                {'error': str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )
    
    @action(detail=True, methods=['post'])
    def asignar_repartidor(self, request, pk=None):
        """
        Asigna un repartidor a un pedido.
        """
        pedido = self.get_object()
        repartidor_id = request.data.get('repartidor_id')
        
        if not repartidor_id:
            return Response(
                {'error': 'El campo "repartidor_id" es requerido'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        from repartidores.models import Repartidor
        try:
            repartidor = Repartidor.objects.get(id_repartidor=repartidor_id)
        except Repartidor.DoesNotExist:
            return Response(
                {'error': 'Repartidor no encontrado'},
                status=status.HTTP_404_NOT_FOUND
            )
        
        pedido.id_repartidor = repartidor
        pedido.save()
        
        # Actualizar el estado del pedido
        pedido.actualizar_estado(
            Pedido.EstadoPedido.EN_CAMINO,
            f'Pedido asignado al repartidor {repartidor.id_usuario.get_full_name()}',
            request.user
        )
        
        return Response({'status': 'Repartidor asignado correctamente'})
    
    @action(detail=True, methods=['post'])
    def marcar_entregado(self, request, pk=None):
        """
        Marca un pedido como entregado.
        """
        pedido = self.get_object()
        
        # Verificar que el pedido esté en estado EN_CAMINO
        if pedido.get_estado_actual() != Pedido.EstadoPedido.EN_CAMINO:
            return Response(
                {'error': 'El pedido no está en estado "En Camino"'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Actualizar el estado del pedido a ENTREGADO
        pedido.actualizar_estado(
            Pedido.EstadoPedido.ENTREGADO,
            'Pedido entregado al cliente',
            request.user
        )
        
        # Actualizar la fecha de entrega
        pedido.fecha_entrega = timezone.now()
        pedido.save(update_fields=['fecha_entrega'])
        
        return Response({'status': 'Pedido marcado como entregado'})


class DetallePedidoViewSet(viewsets.ModelViewSet):
    """
    API endpoint que permite ver y editar detalles de pedidos.
    """
    queryset = DetallePedido.objects.all()
    serializer_class = DetallePedidoSerializer
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['id_pedido', 'id_producto']
    permission_classes = [IsAuthenticated, IsClienteOrVendedor | IsAdminUser]

    def get_serializer_class(self):
        """
        Retorna el serializador apropiado según la acción.
        """
        if self.action in ['create', 'update', 'partial_update']:
            return DetallePedidoCreateUpdateSerializer
        return self.serializer_class

    def get_queryset(self):
        """
        Filtra los detalles de pedido según el tipo de usuario.
        """
        user = self.request.user
        queryset = super().get_queryset()

        # Si es administrador, ve todos los detalles
        if user.is_staff:
            return queryset
        
        # Si es cliente, solo ve los detalles de sus pedidos
        if hasattr(user, 'cliente_profile'):
            return queryset.filter(id_pedido__id_cliente=user.cliente_profile)
        
        # Si es vendedor, ve los detalles de los pedidos de su negocio
        if hasattr(user, 'vendedor_profile'):
            return queryset.filter(id_pedido__id_vendedor=user.vendedor_profile)
        
        return queryset.none()

    def perform_create(self, serializer):
        """
        Crea un nuevo detalle de pedido y actualiza el total del pedido.
        """
        with transaction.atomic():
            detalle = serializer.save()
            detalle.id_pedido.calcular_total()
    
    def perform_update(self, serializer):
        """
        Actualiza un detalle de pedido y actualiza el total del pedido.
        """
        with transaction.atomic():
            detalle = serializer.save()
            detalle.id_pedido.calcular_total()
    
    def perform_destroy(self, instance):
        """
        Elimina un detalle de pedido y actualiza el total del pedido.
        """
        pedido = instance.id_pedido
        with transaction.atomic():
            instance.delete()
            pedido.calcular_total()
