-- Enable foreign key constraints
PRAGMA foreign_keys = ON;

-- Create auth table
CREATE TABLE auth (
    id_auth INTEGER PRIMARY KEY AUTOINCREMENT,
    id_usuario INTEGER NOT NULL,
    fecha_auth TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Create usuarios table
CREATE TABLE usuarios (
    id_usuario INTEGER PRIMARY KEY AUTOINCREMENT,
    nombre_usuario VARCHAR(50) NOT NULL,
    apellido_usuario VARCHAR(50) NOT NULL,
    img_usuario TEXT,
    id_auth INTEGER,
    email_usuario VARCHAR(100) UNIQUE NOT NULL,
    fecha_registro TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    contrasena_usuario TEXT NOT NULL,
    rol_usuario ENUM('cliente', 'repartidor', 'vendedor') NOT NULL
);

-- Create negocios table
CREATE TABLE negocios (
    id_negocio INTEGER PRIMARY KEY AUTOINCREMENT,
    direccion_negocio JSON NOT NULL,
    nombre_negocio VARCHAR(100) NOT NULL,
    img_negocio TEXT,
    telefono_negocio INTEGER
);

-- Create categorias table
CREATE TABLE categorias (
    id_categoria INTEGER PRIMARY KEY AUTOINCREMENT,
    nombre_categoria VARCHAR(50) NOT NULL,
    UNIQUE(nombre_categoria)
);

-- Create vendedor table
CREATE TABLE vendedor (
    id_vendedor INTEGER PRIMARY KEY AUTOINCREMENT,
    nombre_vendedor VARCHAR(100) NOT NULL,
    id_negocio JSON NOT NULL,  -- Array of business IDs
    telefono_vendedor VARCHAR(20),
    id_usuario INTEGER,
    FOREIGN KEY (id_usuario) REFERENCES usuarios(id_usuario) ON DELETE SET NULL
);

-- Create productos table
CREATE TABLE productos (
    id_producto INTEGER PRIMARY KEY AUTOINCREMENT,
    nombre_producto VARCHAR(100) NOT NULL,
    id_vendedor INTEGER NOT NULL,
    id_categoria INTEGER,
    img_producto TEXT,
    precio_producto DECIMAL(10,2) NOT NULL,
    stock_producto INTEGER DEFAULT 0,
    descripcion TEXT,
    fecha_creacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (id_vendedor) REFERENCES vendedor(id_vendedor) ON DELETE CASCADE,
    FOREIGN KEY (id_categoria) REFERENCES categorias(id_categoria) ON DELETE SET NULL
);

-- Create valoracion_producto table
CREATE TABLE valoracion_producto (
    id_valoracion INTEGER PRIMARY KEY AUTOINCREMENT,
    id_producto INTEGER NOT NULL,
    id_vendedor INTEGER NOT NULL,
    id_usuario INTEGER NOT NULL,
    valoracion JSON NOT NULL,  -- {comentario, fecha_valoracion, estrellas}
    fecha_creacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (id_producto) REFERENCES productos(id_producto) ON DELETE CASCADE,
    FOREIGN KEY (id_vendedor) REFERENCES vendedor(id_vendedor) ON DELETE CASCADE,
    FOREIGN KEY (id_usuario) REFERENCES usuarios(id_usuario) ON DELETE CASCADE
);

-- Create repartidores table
CREATE TABLE repartidores (
    id_repartidor INTEGER PRIMARY KEY AUTOINCREMENT,
    nombre_repartidor VARCHAR(50) NOT NULL,
    apellido_repartidor VARCHAR(50) NOT NULL,
    email_repartidor VARCHAR(100) UNIQUE NOT NULL,
    id_usuario INTEGER,
    telefono VARCHAR(20),
    estado BOOLEAN DEFAULT TRUE,
    calificacion_promedio DECIMAL(3,2) DEFAULT 5.0,
    FOREIGN KEY (id_usuario) REFERENCES usuarios(id_usuario) ON DELETE SET NULL
);

-- Create clientes table
CREATE TABLE clientes (
    id_cliente INTEGER PRIMARY KEY AUTOINCREMENT,
    nombre_cliente VARCHAR(50) NOT NULL,
    apellido_cliente VARCHAR(50) NOT NULL,    
    email_cliente VARCHAR(100) UNIQUE NOT NULL,
    two_factor_auth VARCHAR(255),
    id_usuario INTEGER,
    telefono VARCHAR(20),
    direccion_entrega JSON,
    horario_atencion TEXT,
    puntos_fidelidad INTEGER DEFAULT 0,
    FOREIGN KEY (id_usuario) REFERENCES usuarios(id_usuario) ON DELETE SET NULL
);

-- Create pedidos table
CREATE TABLE pedidos (
    id_pedido INTEGER PRIMARY KEY AUTOINCREMENT,
    fecha_pedido TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    estado_pedido JSON NOT NULL,  -- {estado, fecha_estado}
    two_factor_auth VARCHAR(255),
    img_pedido TEXT,
    direccion_pedido JSON NOT NULL,  -- {direccion, latitud, longitud}
    id_cliente INTEGER NOT NULL,
    id_repartidor INTEGER,
    id_vendedor INTEGER NOT NULL,
    total DECIMAL(10,2) NOT NULL,
    metodo_pago VARCHAR(50),
    instrucciones_entrega TEXT,
    FOREIGN KEY (id_cliente) REFERENCES clientes(id_cliente) ON DELETE CASCADE,
    FOREIGN KEY (id_repartidor) REFERENCES repartidores(id_repartidor) ON DELETE SET NULL,
    FOREIGN KEY (id_vendedor) REFERENCES vendedor(id_vendedor) ON DELETE CASCADE
);

-- Create detalle_pedido table
CREATE TABLE detalle_pedido (
    id_detalle INTEGER PRIMARY KEY AUTOINCREMENT,
    id_pedido INTEGER NOT NULL,
    id_producto INTEGER NOT NULL,
    cantidad_producto INTEGER NOT NULL DEFAULT 1,
    precio_unitario DECIMAL(10,2) NOT NULL,
    subtotal DECIMAL(10,2) GENERATED ALWAYS AS (cantidad_producto * precio_unitario) STORED,
    notas TEXT,
    FOREIGN KEY (id_pedido) REFERENCES pedidos(id_pedido) ON DELETE CASCADE,
    FOREIGN KEY (id_producto) REFERENCES productos(id_producto) ON DELETE CASCADE
);

-- Create universidades table
CREATE TABLE universidades (
    id_universidad INTEGER PRIMARY KEY AUTOINCREMENT,
    id_negocio INTEGER NOT NULL,
    nombre_universidad VARCHAR(100) NOT NULL,
    direccion_universidad JSON NOT NULL,  -- {direccion, latitud, longitud}
    img_universidad TEXT,
    telefono_contacto VARCHAR(20),
    FOREIGN KEY (id_negocio) REFERENCES negocios(id_negocio) ON DELETE CASCADE
);

-- Create indexes for better performance
CREATE INDEX idx_pedidos_cliente ON pedidos(id_cliente);
CREATE INDEX idx_pedidos_vendedor ON pedidos(id_vendedor);
CREATE INDEX idx_pedidos_repartidor ON pedidos(id_repartidor);
CREATE INDEX idx_detalle_pedido_pedido ON detalle_pedido(id_pedido);
CREATE INDEX idx_detalle_pedido_producto ON detalle_pedido(id_producto);
CREATE INDEX idx_productos_vendedor ON productos(id_vendedor);
CREATE INDEX idx_productos_categoria ON productos(id_categoria);
CREATE INDEX idx_valoracion_producto ON valoracion_producto(id_producto, id_usuario);
CREATE INDEX idx_categorias_nombre ON categorias(nombre_categoria);

-- Add triggers for data integrity
CREATE TRIGGER after_pedido_insert
AFTER INSERT ON pedidos
FOR EACH ROW
BEGIN
    -- Update stock when order is placed
    UPDATE productos p
    JOIN detalle_pedido dp ON p.id_producto = dp.id_producto
    SET p.stock_producto = p.stock_producto - dp.cantidad_producto
    WHERE dp.id_pedido = NEW.id_pedido;
END;

-- Create view for product catalog
CREATE VIEW catalogo_productos AS
SELECT 
    p.id_producto,
    p.nombre_producto,
    p.descripcion,
    p.precio_producto,
    p.stock_producto,
    p.img_producto,
    v.id_vendedor,
    v.nombre_vendedor,
    c.id_categoria,
    c.nombre_categoria,
    COALESCE((
        SELECT json_object('puntuacion', AVG(json_extract(vp.valoracion, '$.estrellas')), 
                          'total_valoraciones', COUNT(*))
        FROM valoracion_producto vp
        WHERE vp.id_producto = p.id_producto
    ), json_object('puntuacion', 0, 'total_valoraciones', 0)) AS valoraciones
FROM productos p
LEFT JOIN vendedor v ON p.id_vendedor = v.id_vendedor
LEFT JOIN categorias c ON p.id_categoria = c.id_categoria
WHERE p.stock_producto > 0;

-- Create view for customer orders
CREATE VIEW historial_pedidos_cliente AS
SELECT 
    p.id_pedido,
    p.fecha_pedido,
    p.total_pedido,
    p.estado_pedido,
    v.nombre_vendedor,
    c.id_categoria,
    c.nombre_categoria,
    COALESCE((
        SELECT json_object('puntuacion', AVG(json_extract(vp.valoracion, '$.estrellas')), 
                          'total_valoraciones', COUNT(*))
        FROM valoracion_producto vp
        WHERE vp.id_pedido = p.id_pedido
    ), json_object('puntuacion', 0, 'total_valoraciones', 0)) AS valoraciones
FROM pedidos p
LEFT JOIN vendedor v ON p.id_vendedor = v.id_vendedor
LEFT JOIN categorias c ON p.id_categoria = c.id_categoria
WHERE p.id_cliente = (SELECT id_cliente FROM clientes WHERE id_usuario = (SELECT id_usuario FROM auth WHERE id_auth = (SELECT id_auth FROM auth ORDER BY fecha_auth DESC LIMIT 1)));

-- Create view for vendor orders
CREATE VIEW historial_pedidos_vendedor AS
SELECT 
    p.id_pedido,
    p.fecha_pedido,
    p.total_pedido,
    p.estado_pedido,
    c.id_categoria,
    c.nombre_categoria,
    COALESCE((
        SELECT json_object('puntuacion', AVG(json_extract(vp.valoracion, '$.estrellas')), 
                          'total_valoraciones', COUNT(*))
        FROM valoracion_producto vp
        WHERE vp.id_pedido = p.id_pedido
    ), json_object('puntuacion', 0, 'total_valoraciones', 0)) AS valoraciones
FROM pedidos p
LEFT JOIN categorias c ON p.id_categoria = c.id_categoria
WHERE p.id_vendedor = (SELECT id_vendedor FROM vendedor WHERE id_usuario = (SELECT id_usuario FROM auth WHERE id_auth = (SELECT id_auth FROM auth ORDER BY fecha_auth DESC LIMIT 1)));


-- Create view for customer orders
CREATE VIEW historial_pedidos_repartidor AS
SELECT 
    p.id_pedido,
    p.fecha_pedido,
    p.total_pedido,
    p.estado_pedido,
    c.id_categoria,
    c.nombre_categoria,
    COALESCE((
        SELECT json_object('puntuacion', AVG(json_extract(vp.valoracion, '$.estrellas')), 
                          'total_valoraciones', COUNT(*))
        FROM valoracion_producto vp
        WHERE vp.id_pedido = p.id_pedido
    ), json_object('puntuacion', 0, 'total_valoraciones', 0)) AS valoraciones
FROM pedidos p
LEFT JOIN categorias c ON p.id_categoria = c.id_categoria
WHERE p.id_repartidor = (SELECT id_repartidor FROM repartidores WHERE id_usuario = (SELECT id_usuario FROM auth WHERE id_auth = (SELECT id_auth FROM auth ORDER BY fecha_auth DESC LIMIT 1)));