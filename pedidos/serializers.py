from rest_framework import serializers
from django.utils import timezone

from .models import Pedido, DetallePedido
from productos.models import Producto
from usuarios.models import Cliente, Vendedor, Repartidor


class DetallePedidoCreateUpdateSerializer(serializers.ModelSerializer):
    """
    Serializador para la creación y actualización de detalles de pedido.
    """
    id_producto = serializers.PrimaryKeyRelatedField(
        queryset=Producto.objects.all(),
        source='id_producto.id_producto'  # Asegura que se use el ID del producto
    )
    
    class Meta:
        model = DetallePedido
        fields = ['id_producto', 'cantidad', 'precio_unitario', 'notas']
        read_only_fields = ['precio_unitario']
    
    def validate_cantidad(self, value):
        if value <= 0:
            raise serializers.ValidationError("La cantidad debe ser mayor a cero.")
        return value
    
    def validate(self, data):
        """
        Valida que el producto pertenezca al vendedor.
        """
        producto = data.get('id_producto', {}).get('id_producto')
        
        # En caso de actualización, el pedido ya existe
        if self.instance and self.instance.id_pedido:
            vendedor = self.instance.id_pedido.id_vendedor
            if producto.id_vendedor != vendedor:
                raise serializers.ValidationError(
                    "El producto no pertenece al vendedor del pedido."
                )
        
        # Validar que haya suficiente stock
        if producto.stock_disponible < data['cantidad']:
            raise serializers.ValidationError(
                f"No hay suficiente stock. Stock disponible: {producto.stock_disponible}"
            )
        
        # Establecer el precio unitario actual del producto
        data['precio_unitario'] = producto.precio
        
        return data


class DetallePedidoSerializer(serializers.ModelSerializer):
    """
    Serializador para la visualización de detalles de pedido.
    """
    id_producto = serializers.PrimaryKeyRelatedField(read_only=True)
    nombre_producto = serializers.CharField(source='id_producto.nombre', read_only=True)
    subtotal = serializers.DecimalField(
        max_digits=10, 
        decimal_places=2, 
        read_only=True
    )
    
    class Meta:
        model = DetallePedido
        fields = [
            'id_detalle', 'id_producto', 'nombre_producto', 'cantidad',
            'precio_unitario', 'subtotal', 'notas'
        ]
        read_only_fields = fields


class PedidoCreateSerializer(serializers.ModelSerializer):
    """
    Serializador para la creación de pedidos.
    """
    detalles = DetallePedidoCreateUpdateSerializer(many=True, required=True)
    direccion_entrega = serializers.JSONField(required=True)
    
    class Meta:
        model = Pedido
        fields = [
            'id_vendedor', 'metodo_pago', 'direccion_entrega',
            'instrucciones_entrega', 'detalles'
        ]
    
    def validate_detalles(self, value):
        if not value or len(value) == 0:
            raise serializers.ValidationError("El pedido debe tener al menos un producto.")
        return value
    
    def validate_direccion_entrega(self, value):
        required_fields = ['calle', 'numero', 'ciudad', 'codigo_postal', 'pais']
        for field in required_fields:
            if field not in value or not value[field]:
                raise serializers.ValidationError(
                    f"El campo '{field}' es requerido en la dirección de entrega."
                )
        return value
    
    def create(self, validated_data):
        ""
        Crea un nuevo pedido con sus detalles.
        """
        detalles_data = validated_data.pop('detalles')
        user = self.context['request'].user
        
        # Obtener el perfil de cliente del usuario
        try:
            cliente = Cliente.objects.get(id_usuario=user)
        except Cliente.DoesNotExist:
            raise serializers.ValidationError("El usuario no tiene un perfil de cliente.")
        
        # Verificar que el vendedor existe
        vendedor = validated_data.get('id_vendedor')
        if not vendedor:
            raise serializers.ValidationError("El vendedor es requerido.")
        
        # Crear el pedido
        pedido = Pedido.objects.create(
            id_cliente=cliente,
            **validated_data
        )
        
        # Crear los detalles del pedido
        for detalle_data in detalles_data:
            producto = detalle_data['id_producto']['id_producto']
            DetallePedido.objects.create(
                id_pedido=pedido,
                id_producto=producto,
                cantidad=detalle_data['cantidad'],
                precio_unitario=detalle_data['precio_unitario'],
                notas=detalle_data.get('notas', '')
            )
            
            # Actualizar el stock del producto
            producto.stock_disponible -= detalle_data['cantidad']
            producto.save(update_fields=['stock_disponible'])
        
        # Calcular el total del pedido
        pedido.calcular_total()
        
        return pedido


class PedidoUpdateSerializer(serializers.ModelSerializer):
    """
    Serializador para la actualización de pedidos.
    """
    class Meta:
        model = Pedido
        fields = [
            'estado_pedido', 'id_repartidor', 'fecha_entrega',
            'instrucciones_entrega'
        ]
        read_only_fields = ['fecha_entrega']
    
    def update(self, instance, validated_data):
        """
        Actualiza un pedido existente.
        """
        user = self.context['request'].user
        estado_anterior = instance.estado_pedido
        
        # Si se está actualizando el estado, registrar el cambio
        if 'estado_pedido' in validated_data:
            nuevo_estado = validated_data['estado_pedido']
            notas = f"Estado cambiado de {estado_anterior} a {nuevo_estado}"
            instance.actualizar_estado(nuevo_estado, notas, user)
            
            # Si el estado es ENTREGADO, establecer la fecha de entrega
            if nuevo_estado == Pedido.EstadoPedido.ENTREGADO and not instance.fecha_entrega:
                validated_data['fecha_entrega'] = timezone.now()
        
        # Actualizar los demás campos
        for attr, value in validated_data.items():
            if attr != 'estado_pedido':  # Ya manejado arriba
                setattr(instance, attr, value)
        
        instance.save()
        return instance


class PedidoSerializer(serializers.ModelSerializer):
    """
    Serializador para la visualización de pedidos.
    """
    detalles = DetallePedidoSerializer(many=True, read_only=True)
    id_cliente = serializers.PrimaryKeyRelatedField(read_only=True)
    nombre_cliente = serializers.CharField(source='id_cliente.nombre_cliente', read_only=True)
    id_vendedor = serializers.PrimaryKeyRelatedField(read_only=True)
    nombre_negocio = serializers.CharField(source='id_vendedor.nombre_negocio', read_only=True)
    id_repartidor = serializers.PrimaryKeyRelatedField(read_only=True, allow_null=True)
    nombre_repartidor = serializers.SerializerMethodField()
    estado_display = serializers.CharField(
        source='get_estado_pedido_display', 
        read_only=True
    )
    direccion_entrega = serializers.SerializerMethodField()
    historial_estados = serializers.SerializerMethodField()
    
    class Meta:
        model = Pedido
        fields = [
            'id_pedido', 'id_cliente', 'nombre_cliente', 'id_vendedor', 
            'nombre_negocio', 'id_repartidor', 'nombre_repartidor',
            'fecha_pedido', 'fecha_entrega', 'estado_pedido', 'estado_display',
            'metodo_pago', 'subtotal', 'costo_envio', 'impuestos', 'total',
            'direccion_entrega', 'instrucciones_entrega', 'detalles',
            'historial_estados', 'fecha_creacion', 'fecha_actualizacion'
        ]
        read_only_fields = fields
    
    def get_nombre_repartidor(self, obj):
        if obj.id_repartidor and obj.id_repartidor.id_usuario:
            return obj.id_repartidor.id_usuario.get_full_name()
        return None
    
    def get_direccion_entrega(self, obj):
        """
        Devuelve la dirección de entrega formateada.
        """
        if not obj.direccion_entrega:
            return None
        
        direccion = obj.direccion_entrega
        return {
            'calle': direccion.get('calle', ''),
            'numero': direccion.get('numero', ''),
            'departamento': direccion.get('departamento', ''),
            'ciudad': direccion.get('ciudad', ''),
            'region': direccion.get('region', ''),
            'codigo_postal': direccion.get('codigo_postal', ''),
            'pais': direccion.get('pais', ''),
            'referencias': direccion.get('referencias', '')
        }
    
    def get_historial_estados(self, obj):
        """
        Devuelve el historial de estados del pedido.
        """
        return obj.get_historial_estados()
