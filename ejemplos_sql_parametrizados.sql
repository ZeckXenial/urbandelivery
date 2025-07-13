-- =============================================
-- EJEMPLOS DE SENTENCIAS SQL PARAMETRIZADAS
-- =============================================

-- 1. USUARIOS Y AUTENTICACIÓN
-- ==========================

-- Registrar un nuevo usuario
-- Parámetros: nombre, apellido, email, contraseña_encriptada, rol
INSERT INTO usuarios (nombre_usuario, apellido_usuario, email_usuario, contrasena_usuario, rol_usuario)
VALUES (?, ?, ?, ?, ?);

-- Iniciar sesión
-- Parámetros: email, contraseña_encriptada
SELECT u.*, 
       CASE 
           WHEN u.rol_usuario = 'cliente' THEN (SELECT id_cliente FROM clientes WHERE id_usuario = u.id_usuario)
           WHEN u.rol_usuario = 'vendedor' THEN (SELECT id_vendedor FROM vendedor WHERE id_usuario = u.id_usuario)
           WHEN u.rol_usuario = 'repartidor' THEN (SELECT id_repartidor FROM repartidores WHERE id_usuario = u.id_usuario)
           ELSE NULL 
       END as id_rol_especifico
FROM usuarios u
WHERE u.email_usuario = ? AND u.contrasena_usuario = ?;

-- Actualizar perfil de usuario
-- Parámetros: nombre, apellido, email, id_usuario
UPDATE usuarios 
SET nombre_usuario = ?, 
    apellido_usuario = ?, 
    email_usuario = ?,
    img_usuario = ?
WHERE id_usuario = ?;

-- 2. CLIENTES
-- ==========

-- Registrar un nuevo cliente
-- Parámetros: id_usuario, teléfono, dirección (JSON)
INSERT INTO clientes (id_usuario, telefono, direccion_entrega)
VALUES (?, ?, ?);

-- Actualizar dirección de entrega
-- Parámetros: nueva_direccion (JSON), id_cliente
UPDATE clientes 
SET direccion_entrega = ?
WHERE id_cliente = ?;

-- 3. VENDEDORES
-- ============

-- Registrar un nuevo vendedor
-- Parámetros: id_usuario, id_negocio, teléfono
INSERT INTO vendedor (id_usuario, id_negocio, telefono_vendedor, nombre_vendedor)
VALUES (?, ?, ?, ?);

-- Añadir producto (para vendedor)
-- Parámetros: id_vendedor, nombre, descripción, precio, stock, id_categoria, imagen
INSERT INTO productos (id_vendedor, nombre_producto, descripcion, precio_producto, stock_producto, id_categoria, img_producto)
VALUES (?, ?, ?, ?, ?, ?, ?);

-- 4. REPARTIDORES
-- ==============

-- Registrar un nuevo repartidor
-- Parámetros: id_usuario, teléfono, disponibilidad
INSERT INTO repartidores (id_usuario, telefono, estado, calificacion_promedio)
VALUES (?, ?, TRUE, 5.0);

-- Actualizar ubicación del repartidor
-- Parámetros: latitud, longitud, id_repartidor
UPDATE repartidores 
SET ubicacion_actual = json_object('latitud', ?, 'longitud', ?, 'ultima_actualizacion', datetime('now'))
WHERE id_repartidor = ?;

-- 5. PEDIDOS
-- =========

-- Crear un nuevo pedido
-- Parámetros: id_cliente, id_vendedor, dirección_entrega (JSON), total, método_pago
INSERT INTO pedidos (id_cliente, id_vendedor, direccion_pedido, total, metodo_pago, estado_pedido)
VALUES (?, ?, ?, ?, ?, json_object('estado', 'pendiente', 'fecha_estado', datetime('now')));

-- Añadir productos al pedido
-- Parámetros: id_pedido, id_producto, cantidad, precio_unitario
INSERT INTO detalle_pedido (id_pedido, id_producto, cantidad_producto, precio_unitario)
VALUES (?, ?, ?, ?);

-- Actualizar estado del pedido
-- Parámetros: nuevo_estado, id_pedido
UPDATE pedidos 
SET estado_pedido = json_object('estado', ?, 'fecha_estado', datetime('now'))
WHERE id_pedido = ?;

-- 6. VALORACIONES
-- ==============

-- Añadir valoración a un producto
-- Parámetros: id_producto, id_usuario, id_vendedor, estrellas, comentario
INSERT INTO valoracion_producto (id_producto, id_usuario, id_vendedor, valoracion)
VALUES (?, ?, ?, json_object('estrellas', ?, 'comentario', ?, 'fecha', datetime('now')));

-- 7. BÚSQUEDAS Y FILTRADOS
-- =======================

-- Buscar productos por nombre o descripción
-- Parámetros: término_búsqueda
SELECT p.*, v.nombre_vendedor, c.nombre_categoria
FROM productos p
JOIN vendedor v ON p.id_vendedor = v.id_vendedor
LEFT JOIN categorias c ON p.id_categoria = c.id_categoria
WHERE p.nombre_producto LIKE ? OR p.descripcion LIKE ?
  AND p.stock_producto > 0;

-- Filtrar productos por categoría y rango de precios
-- Parámetros: id_categoria, precio_min, precio_max
SELECT p.*, v.nombre_vendedor
FROM productos p
JOIN vendedor v ON p.id_vendedor = v.id_vendedor
WHERE p.id_categoria = ? 
  AND p.precio_producto BETWEEN ? AND ?
  AND p.stock_producto > 0
ORDER BY p.precio_producto;

-- 8. REPORTES
-- ==========

-- Ventas por período (para vendedor)
-- Parámetros: fecha_inicio, fecha_fin, id_vendedor
SELECT 
    DATE(p.fecha_pedido) as fecha,
    COUNT(DISTINCT p.id_pedido) as total_pedidos,
    SUM(dp.cantidad_producto) as unidades_vendidas,
    SUM(dp.subtotal) as ingreso_total
FROM pedidos p
JOIN detalle_pedido dp ON p.id_pedido = dp.id_pedido
JOIN productos pr ON dp.id_producto = pr.id_producto
WHERE p.fecha_pedido BETWEEN ? AND ?
  AND pr.id_vendedor = ?
GROUP BY DATE(p.fecha_pedido)
ORDER BY fecha;

-- 9. NOTIFICACIONES
-- ================

-- Enviar notificación
-- Parámetros: id_usuario, título, mensaje, tipo
INSERT INTO notificaciones (id_usuario, titulo, mensaje, tipo, leida, fecha_creacion)
VALUES (?, ?, ?, ?, 0, datetime('now'));

-- Marcar notificación como leída
-- Parámetros: id_notificacion
UPDATE notificaciones 
SET leida = 1, 
    fecha_lectura = datetime('now')
WHERE id_notificacion = ?;

-- 10. SISTEMA DE FIDELIZACIÓN
-- ==========================

-- Canjear puntos por recompensa
-- Parámetros: id_cliente, id_recompensa
BEGIN TRANSACTION;
    -- Insertar canje
    INSERT INTO recompensas_canjeadas (id_cliente, id_recompensa, fecha_canje, codigo_canje)
    VALUES (?, ?, datetime('now'), substr(md5(random()::text), 1, 10));
    
    -- Actualizar puntos del cliente
    UPDATE clientes 
    SET puntos_fidelidad = puntos_fidelidad - (SELECT puntos_requeridos FROM recompensas WHERE id_recompensa = ?)
    WHERE id_cliente = ?;
    
    -- Actualizar stock de la recompensa si es necesario
    UPDATE recompensas 
    SET stock = stock - 1 
    WHERE id_recompensa = ? AND stock IS NOT NULL;
COMMIT;

-- 11. GESTIÓN DE INVENTARIO
-- ========================

-- Actualizar stock de producto
-- Parámetros: id_producto, cantidad (puede ser negativo para restar)
UPDATE productos 
SET stock_producto = stock_producto + ?
WHERE id_producto = ?;

-- Registrar movimiento de inventario
-- Parámetros: id_producto, cantidad, tipo_movimiento, motivo, id_usuario, notas
INSERT INTO movimientos_inventario (id_producto, cantidad, tipo_movimiento, motivo, id_usuario, notas, fecha_movimiento)
VALUES (?, ?, ?, ?, ?, ?, datetime('now'));

-- 12. SISTEMA DE SOPORTE
-- =====================

-- Crear ticket de soporte
-- Parámetros: id_usuario, asunto, descripción, categoría, prioridad
INSERT INTO tickets_soporte (id_usuario, asunto, descripcion, categoria, prioridad, estado, fecha_creacion)
VALUES (?, ?, ?, ?, ?, 'abierto', datetime('now'));

-- Añadir mensaje a ticket
-- Parámetros: id_ticket, id_usuario, mensaje
INSERT INTO mensajes_soporte (id_ticket, id_usuario, mensaje, fecha_envio)
VALUES (?, ?, ?, datetime('now'));

-- 13. CONSULTAS AVANZADAS
-- ======================

-- Obtener historial de pedidos de un cliente con detalles
-- Parámetros: id_cliente, límite
SELECT 
    p.id_pedido,
    p.fecha_pedido,
    p.total,
    p.estado_pedido->>'estado' as estado,
    v.nombre_vendedor,
    (
        SELECT json_group_array(
            json_object(
                'producto', pr.nombre_producto,
                'cantidad', dp.cantidad_producto,
                'precio_unitario', dp.precio_unitario,
                'subtotal', dp.subtotal
            )
        )
        FROM detalle_pedido dp
        JOIN productos pr ON dp.id_producto = pr.id_producto
        WHERE dp.id_pedido = p.id_pedido
    ) as productos
FROM pedidos p
JOIN vendedor v ON p.id_vendedor = v.id_vendedor
WHERE p.id_cliente = ?
ORDER BY p.fecha_pedido DESC
LIMIT ?;

-- 14. SEGURIDAD Y AUDITORÍA
-- =======================

-- Cambiar contraseña de usuario
-- Parámetros: nueva_contraseña_encriptada, id_usuario
UPDATE usuarios 
SET contrasena_usuario = ?,
    fecha_actualizacion = datetime('now')
WHERE id_usuario = ?;

-- Registrar intento de inicio de sesión fallido
-- Parámetros: email, dirección_ip
INSERT INTO intentos_login (email, direccion_ip, exito, fecha_intento)
VALUES (?, ?, 0, datetime('now'));

-- 15. LIMPIEZA DE DATOS
-- ===================

-- Eliminar cuentas inactivas (más de 1 año sin actividad)
-- Sin parámetros necesarios
DELETE FROM usuarios 
WHERE id_usuario IN (
    SELECT u.id_usuario 
    FROM usuarios u
    LEFT JOIN auth a ON u.id_usuario = a.id_usuario
    WHERE (julianday('now') - julianday(COALESCE(MAX(a.fecha_auth), u.fecha_registro))) > 365
);

-- =============================================
-- NOTAS IMPORTANTES:
-- 1. Reemplaza los signos de interrogación (?) por los valores reales en tu aplicación.
-- 2. Asegúrate de usar consultas preparadas para prevenir inyección SQL.
-- 3. Maneja las transacciones adecuadamente para mantener la integridad de los datos.
-- 4. Ajusta los nombres de las tablas y columnas según tu esquema real.
-- 5. Considera agregar índices a las columnas usadas en las cláusulas WHERE y JOIN.
-- 6. Implementa un sistema de respaldo de la base de datos.
-- =============================================
