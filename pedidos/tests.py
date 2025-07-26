from django.test import TestCase, RequestFactory
from django.urls import reverse
from django.contrib.auth import get_user_model
from rest_framework.test import APITestCase, APIClient
from rest_framework import status
from django.utils import timezone

from productos.models import Producto, Categoria
from usuarios.models import Cliente, Vendedor, Repartidor
from .models import Pedido, DetallePedido
from .serializers import PedidoSerializer, DetallePedidoSerializer

User = get_user_model()


class PedidoModelTest(TestCase):
    """Test para el modelo Pedido."""
    
    def setUp(self):
        # Crear usuario y perfil de cliente
        self.user_cliente = User.objects.create_user(
            username='cliente_test',
            email='cliente@test.com',
            password='testpass123'
        )
        self.cliente = Cliente.objects.create(
            id_usuario=self.user_cliente,
            nombre_cliente='Cliente Test',
            telefono_contacto='1234567890'
        )
        
        # Crear usuario y perfil de vendedor
        self.user_vendedor = User.objects.create_user(
            username='vendedor_test',
            email='vendedor@test.com',
            password='testpass123'
        )
        self.vendedor = Vendedor.objects.create(
            id_usuario=self.user_vendedor,
            nombre_negocio='Tienda Test',
            descripcion_negocio='Descripción de prueba',
            telefono_contacto='0987654321'
        )
        
        # Crear categoría y producto
        self.categoria = Categoria.objects.create(
            nombre='Categoría Test',
            descripcion='Descripción de categoría de prueba'
        )
        
        self.producto = Producto.objects.create(
            id_vendedor=self.vendedor,
            nombre='Producto Test',
            descripcion='Descripción de producto de prueba',
            precio=10000,
            stock_disponible=10,
            categoria=self.categoria
        )
        
        # Crear pedido de prueba
        self.pedido = Pedido.objects.create(
            id_cliente=self.cliente,
            id_vendedor=self.vendedor,
            metodo_pago='efectivo',
            direccion_entrega={
                'calle': 'Calle Falsa',
                'numero': '123',
                'ciudad': 'Ciudad Test',
                'codigo_postal': '12345',
                'pais': 'País Test'
            },
            subtotal=10000,
            costo_envio=2000,
            impuestos=1900,
            total=13900
        )
        
        # Crear detalle de pedido de prueba
        self.detalle_pedido = DetallePedido.objects.create(
            id_pedido=self.pedido,
            id_producto=self.producto,
            cantidad=1,
            precio_unitario=10000,
            notas='Sin notas'
        )
    
    def test_creacion_pedido(self):
        """Test para verificar la creación de un pedido."""
        self.assertEqual(self.pedido.id_cliente, self.cliente)
        self.assertEqual(self.pedido.id_vendedor, self.vendedor)
        self.assertEqual(self.pedido.metodo_pago, 'efectivo')
        self.assertEqual(self.pedido.total, 13900)
        self.assertEqual(self.pedido.estado_pedido, 'pendiente')
    
    def test_actualizar_estado_pedido(self):
        """Test para verificar la actualización del estado de un pedido."""
        self.pedido.actualizar_estado(
            'en_proceso',
            'El pedido está siendo preparado',
            self.user_vendedor
        )
        
        self.assertEqual(self.pedido.estado_pedido, 'en_proceso')
        historial = self.pedido.get_historial_estados()
        self.assertEqual(len(historial), 2)  # Estado inicial + nuevo estado
        self.assertEqual(historial[1]['estado'], 'en_proceso')
        self.assertEqual(historial[1]['notas'], 'El pedido está siendo preparado')
    
    def test_calcular_total_pedido(self):
        """Test para verificar el cálculo del total de un pedido."""
        # Crear un segundo detalle para el mismo pedido
        DetallePedido.objects.create(
            id_pedido=self.pedido,
            id_producto=self.producto,
            cantidad=2,
            precio_unitario=10000,
            notas='Segundo producto'
        )
        
        # El subtotal debería ser 30000 (10000 + 20000)
        # El total debería ser 33900 (30000 + 2000 + 1900)
        self.pedido.calcular_total()
        self.assertEqual(self.pedido.subtotal, 30000)
        self.assertEqual(self.pedido.total, 33900)


class DetallePedidoModelTest(TestCase):
    """Test para el modelo DetallePedido."""
    
    def setUp(self):
        # Configuración similar a PedidoModelTest
        self.user_cliente = User.objects.create_user(
            username='cliente_test',
            email='cliente@test.com',
            password='testpass123'
        )
        self.cliente = Cliente.objects.create(
            id_usuario=self.user_cliente,
            nombre_cliente='Cliente Test',
            telefono_contacto='1234567890'
        )
        
        self.user_vendedor = User.objects.create_user(
            username='vendedor_test',
            email='vendedor@test.com',
            password='testpass123'
        )
        self.vendedor = Vendedor.objects.create(
            id_usuario=self.user_vendedor,
            nombre_negocio='Tienda Test',
            descripcion_negocio='Descripción de prueba',
            telefono_contacto='0987654321'
        )
        
        self.categoria = Categoria.objects.create(
            nombre='Categoría Test',
            descripcion='Descripción de categoría de prueba'
        )
        
        self.producto = Producto.objects.create(
            id_vendedor=self.vendedor,
            nombre='Producto Test',
            descripcion='Descripción de producto de prueba',
            precio=10000,
            stock_disponible=10,
            categoria=self.categoria
        )
        
        self.pedido = Pedido.objects.create(
            id_cliente=self.cliente,
            id_vendedor=self.vendedor,
            metodo_pago='efectivo',
            direccion_entrega={
                'calle': 'Calle Falsa',
                'numero': '123',
                'ciudad': 'Ciudad Test',
                'codigo_postal': '12345',
                'pais': 'País Test'
            },
            subtotal=0,  # Se calculará
            costo_envio=2000,
            impuestos=0,  # Se calculará
            total=0      # Se calculará
        )
        
        self.detalle_pedido = DetallePedido.objects.create(
            id_pedido=self.pedido,
            id_producto=self.producto,
            cantidad=2,
            precio_unitario=10000,
            notas='Sin notas'
        )
    
    def test_creacion_detalle_pedido(self):
        """Test para verificar la creación de un detalle de pedido."""
        self.assertEqual(self.detalle_pedido.id_pedido, self.pedido)
        self.assertEqual(self.detalle_pedido.id_producto, self.producto)
        self.assertEqual(self.detalle_pedido.cantidad, 2)
        self.assertEqual(self.detalle_pedido.precio_unitario, 10000)
        self.assertEqual(self.detalle_pedido.subtotal, 20000)
    
    def test_actualizar_detalle_pedido(self):
        """Test para verificar la actualización de un detalle de pedido."""
        self.detalle_pedido.cantidad = 3
        self.detalle_pedido.save()
        
        # Verificar que el subtotal se actualizó correctamente
        self.assertEqual(self.detalle_pedido.subtotal, 30000)
        
        # Verificar que el total del pedido se actualizó
        self.pedido.refresh_from_db()
        self.assertEqual(self.pedido.subtotal, 30000)
        self.assertEqual(self.pedido.impuestos, 5700)  # 19% de 30000
        self.assertEqual(self.pedido.total, 37700)     # 30000 + 2000 + 5700


class PedidoAPITest(APITestCase):
    """Test para las vistas de la API de Pedidos."""
    
    def setUp(self):
        # Configuración similar a los tests anteriores
        self.factory = RequestFactory()
        
        # Crear usuarios
        self.user_cliente = User.objects.create_user(
            username='cliente_test',
            email='cliente@test.com',
            password='testpass123'
        )
        self.cliente = Cliente.objects.create(
            id_usuario=self.user_cliente,
            nombre_cliente='Cliente Test',
            telefono_contacto='1234567890'
        )
        
        self.user_vendedor = User.objects.create_user(
            username='vendedor_test',
            email='vendedor@test.com',
            password='testpass123'
        )
        self.vendedor = Vendedor.objects.create(
            id_usuario=self.user_vendedor,
            nombre_negocio='Tienda Test',
            descripcion_negocio='Descripción de prueba',
            telefono_contacto='0987654321'
        )
        
        self.user_repartidor = User.objects.create_user(
            username='repartidor_test',
            email='repartidor@test.com',
            password='testpass123'
        )
        self.repartidor = Repartidor.objects.create(
            id_usuario=self.user_repartidor,
            nombre_completo='Repartidor Test',
            telefono_contacto='55555555',
            estado='disponible'
        )
        
        # Crear categoría y producto
        self.categoria = Categoria.objects.create(
            nombre='Categoría Test',
            descripcion='Descripción de categoría de prueba'
        )
        
        self.producto = Producto.objects.create(
            id_vendedor=self.vendedor,
            nombre='Producto Test',
            descripcion='Descripción de producto de prueba',
            precio=10000,
            stock_disponible=10,
            categoria=self.categoria
        )
        
        # Crear pedido de prueba
        self.pedido = Pedido.objects.create(
            id_cliente=self.cliente,
            id_vendedor=self.vendedor,
            metodo_pago='efectivo',
            direccion_entrega={
                'calle': 'Calle Falsa',
                'numero': '123',
                'ciudad': 'Ciudad Test',
                'codigo_postal': '12345',
                'pais': 'País Test'
            },
            subtotal=10000,
            costo_envio=2000,
            impuestos=1900,
            total=13900
        )
        
        # Crear detalle de pedido de prueba
        self.detalle_pedido = DetallePedido.objects.create(
            id_pedido=self.pedido,
            id_producto=self.producto,
            cantidad=1,
            precio_unitario=10000,
            notas='Sin notas'
        )
        
        # URLs
        self.list_url = reverse('pedido-list')
        self.detail_url = reverse('pedido-detail', kwargs={'pk': self.pedido.pk})
        self.cambiar_estado_url = reverse('pedido-cambiar-estado', kwargs={'pk': self.pedido.pk})
        self.asignar_repartidor_url = reverse('pedido-asignar-repartidor', kwargs={'pk': self.pedido.pk})
        self.marcar_entregado_url = reverse('pedido-marcar-entregado', kwargs={'pk': self.pedido.pk})
        
        # Cliente API client
        self.client_cliente = APIClient()
        self.client_cliente.force_authenticate(user=self.user_cliente)
        
        # Vendedor API client
        self.client_vendedor = APIClient()
        self.client_vendedor.force_authenticate(user=self.user_vendedor)
        
        # Repartidor API client
        self.client_repartidor = APIClient()
        self.client_repartidor.force_authenticate(user=self.user_repartidor)
    
    def test_listar_pedidos_cliente(self):
        """Test para listar los pedidos de un cliente."""
        response = self.client_cliente.get(self.list_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 1)
        self.assertEqual(response.data['results'][0]['id_pedido'], self.pedido.id_pedido)
    
    def test_crear_pedido(self):
        """Test para crear un nuevo pedido."""
        data = {
            'id_vendedor': self.vendedor.id_vendedor,
            'metodo_pago': 'efectivo',
            'direccion_entrega': {
                'calle': 'Otra Calle',
                'numero': '456',
                'ciudad': 'Otra Ciudad',
                'codigo_postal': '54321',
                'pais': 'Otro País'
            },
            'instrucciones_entrega': 'Dejar en la puerta',
            'detalles': [
                {
                    'id_producto': self.producto.id_producto,
                    'cantidad': 2,
                    'notas': 'Sin cebolla'
                }
            ]
        }
        
        response = self.client_cliente.post(self.list_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Pedido.objects.count(), 2)
        self.assertEqual(DetallePedido.objects.count(), 2)
        
        # Verificar que se actualizó el stock del producto
        self.producto.refresh_from_db()
        self.assertEqual(self.producto.stock_disponible, 8)  # 10 - 2
    
    def test_cambiar_estado_pedido(self):
        """Test para cambiar el estado de un pedido."""
        data = {
            'estado': 'en_proceso',
            'notas': 'El pedido está siendo preparado'
        }
        
        response = self.client_vendedor.post(self.cambiar_estado_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        # Verificar que el estado se actualizó
        self.pedido.refresh_from_db()
        self.assertEqual(self.pedido.estado_pedido, 'en_proceso')
        
        # Verificar que se registró en el historial
        historial = self.pedido.get_historial_estados()
        self.assertEqual(historial[1]['estado'], 'en_proceso')
        self.assertEqual(historial[1]['notas'], 'El pedido está siendo preparado')
    
    def test_asignar_repartidor(self):
        """Test para asignar un repartidor a un pedido."""
        data = {
            'repartidor_id': self.repartidor.id_repartidor
        }
        
        response = self.client_vendedor.post(self.asignar_repartidor_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        # Verificar que se asignó el repartidor
        self.pedido.refresh_from_db()
        self.assertEqual(self.pedido.id_repartidor, self.repartidor)
        self.assertEqual(self.pedido.estado_pedido, 'en_camino')
    
    def test_marcar_entregado(self):
        """Test para marcar un pedido como entregado."""
        # Primero asignar un repartidor y cambiar el estado a 'en_camino'
        self.pedido.id_repartidor = self.repartidor
        self.pedido.estado_pedido = 'en_camino'
        self.pedido.save()
        
        response = self.client_repartidor.post(self.marcar_entregado_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        # Verificar que el estado se actualizó a 'entregado'
        self.pedido.refresh_from_db()
        self.assertEqual(self.pedido.estado_pedido, 'entregado')
        self.assertIsNotNone(self.pedido.fecha_entrega)
    
    def test_permisos_vistas(self):
        """Test para verificar los permisos de las vistas."""
        # Cliente no puede cambiar el estado de un pedido
        response = self.client_cliente.post(
            self.cambiar_estado_url,
            {'estado': 'en_proceso'},
            format='json'
        )
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        
        # Repartidor no puede asignar repartidor
        response = self.client_repartidor.post(
            self.asignar_repartidor_url,
            {'repartidor_id': self.repartidor.id_repartidor},
            format='json'
        )
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        
        # Usuario no autenticado no puede ver pedidos
        client = APIClient()
        response = client.get(self.list_url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
