# Módulo de Pedidos

Este módulo maneja la lógica de negocio relacionada con los pedidos en UrbanFood, incluyendo la creación, seguimiento y gestión de pedidos, así como sus detalles.

## Modelos

### Pedido
Representa un pedido realizado por un cliente a un vendedor.

**Campos principales:**
- `id_pedido`: Identificador único del pedido (autoincremental)
- `id_cliente`: Cliente que realiza el pedido (relación con modelo Cliente)
- `id_vendedor`: Vendedor que recibe el pedido (relación con modelo Vendedor)
- `id_repartidor`: Repartidor asignado para la entrega (opcional, relación con modelo Repartidor)
- `fecha_pedido`: Fecha y hora en que se realizó el pedido
- `fecha_entrega`: Fecha y hora en que se entregó el pedido (opcional)
- `estado_pedido`: Estado actual del pedido (pendiente, en_proceso, en_camino, entregado, cancelado)
- `metodo_pago`: Método de pago utilizado (efectivo, tarjeta, transferencia)
- `subtotal`: Suma de los precios de los productos
- `costo_envio`: Costo del envío
- `impuestos`: Impuestos aplicados
- `total`: Monto total del pedido (subtotal + costo_envio + impuestos)
- `direccion_entrega`: JSON con la dirección de entrega
- `instrucciones_entrega`: Instrucciones especiales para la entrega
- `historial_estados`: JSON con el historial de cambios de estado

### DetallePedido
Representa un producto específico dentro de un pedido.

**Campos principales:**
- `id_detalle`: Identificador único del detalle (autoincremental)
- `id_pedido`: Pedido al que pertenece (relación con modelo Pedido)
- `id_producto`: Producto incluido (relación con modelo Producto)
- `cantidad`: Cantidad del producto
- `precio_unitario`: Precio unitario en el momento de la compra
- `subtotal`: Subtotal (cantidad * precio_unitario)
- `notas`: Notas adicionales para este producto

## API Endpoints

### Listar/Crear Pedidos
- **URL**: `/api/pedidos/pedidos/`
- **Método**: `GET`, `POST`
- **Autenticación requerida**: Sí
- **Permisos**: 
  - Cliente: Solo sus propios pedidos
  - Vendedor: Solo pedidos de su negocio
  - Administrador: Todos los pedidos

### Obtener/Actualizar/Eliminar Pedido
- **URL**: `/api/pedidos/pedidos/{id}/`
- **Método**: `GET`, `PUT`, `PATCH`, `DELETE`
- **Autenticación requerida**: Sí
- **Permisos**: 
  - Cliente: Solo sus propios pedidos
  - Vendedor: Solo pedidos de su negocio
  - Administrador: Cualquier pedido

### Cambiar Estado de un Pedido
- **URL**: `/api/pedidos/pedidos/{id}/cambiar-estado/`
- **Método**: `POST`
- **Autenticación requerida**: Sí
- **Permisos**: Vendedor o Administrador
- **Body**:
  ```json
  {
    "estado": "en_proceso",
    "notas": "El pedido está siendo preparado"
  }
  ```

### Asignar Repartidor a un Pedido
- **URL**: `/api/pedidos/pedidos/{id}/asignar-repartidor/`
- **Método**: `POST`
- **Autenticación requerida**: Sí
- **Permisos**: Vendedor o Administrador
- **Body**:
  ```json
  {
    "repartidor_id": 1
  }
  ```

### Marcar Pedido como Entregado
- **URL**: `/api/pedidos/pedidos/{id}/marcar-entregado/`
- **Método**: `POST`
- **Autenticación requerida**: Sí
- **Permisos**: Repartidor asignado o Vendedor o Administrador

### Listar/Detalles de Pedido
- **URL**: `/api/pedidos/detalles-pedido/`
- **Método**: `GET`, `POST`
- **Autenticación requerida**: Sí
- **Permisos**: 
  - Cliente: Solo detalles de sus pedidos
  - Vendedor: Solo detalles de pedidos de su negocio
  - Administrador: Todos los detalles

## Ejemplos de Uso

### Crear un Nuevo Pedido (Cliente)

```http
POST /api/pedidos/pedidos/
Content-Type: application/json
Authorization: Bearer <token>

{
  "id_vendedor": 1,
  "metodo_pago": "efectivo",
  "direccion_entrega": {
    "calle": "Calle Falsa",
    "numero": "123",
    "ciudad": "Ciudad Test",
    "codigo_postal": "12345",
    "pais": "País Test"
  },
  "instrucciones_entrega": "Dejar en la puerta principal",
  "detalles": [
    {
      "id_producto": 1,
      "cantidad": 2,
      "notas": "Sin cebolla por favor"
    },
    {
      "id_producto": 3,
      "cantidad": 1,
      "notas": "Bien cocido"
    }
  ]
}
```

### Cambiar Estado de un Pedido (Vendedor)

```http
POST /api/pedidos/pedidos/1/cambiar-estado/
Content-Type: application/json
Authorization: Bearer <token>

{
  "estado": "en_proceso",
  "notas": "El pedido está siendo preparado"
}
```

### Asignar Repartidor a un Pedido (Vendedor)

```http
POST /api/pedidos/pedidos/1/asignar-repartidor/
Content-Type: application/json
Authorization: Bearer <token>

{
  "repartidor_id": 1
}
```

### Marcar Pedido como Entregado (Repartidor)

```http
POST /api/pedidos/pedidos/1/marcar-entregado/
Content-Type: application/json
Authorization: Bearer <token>
```

## Señales (Signals)

El módulo incluye las siguientes señales para manejar eventos:

1. **post_save para DetallePedido**: Actualiza automáticamente el total del pedido cuando se guarda un detalle.
2. **post_delete para DetallePedido**: Actualiza el total del pedido cuando se elimina un detalle.
3. **pre_save para Pedido**: Maneja la lógica cuando cambia el estado de un pedido (ej: actualizar stock si se cancela).
4. **post_save para Pedido**: Notifica a los usuarios relevantes cuando cambia el estado de un pedido.

## Permisos Personalizados

- **IsClienteOwner**: Permite a los clientes acceder solo a sus propios pedidos.
- **IsVendedorOwner**: Permite a los vendedores acceder solo a los pedidos de su negocio.
- **IsRepartidorOrVendedor**: Permite a repartidores o vendedores realizar ciertas acciones.
- **IsClienteOrVendedor**: Permite a clientes o vendedores realizar ciertas acciones.

## Pruebas

El módulo incluye pruebas unitarias y de integración para:
- Modelos (`Pedido`, `DetallePedido`)
- Vistas de la API
- Serializadores
- Permisos personalizados

Para ejecutar las pruebas:

```bash
python manage.py test pedidos.tests
```
