-- phpMyAdmin SQL Dump
-- version 5.2.1
-- https://www.phpmyadmin.net/
--
-- Servidor: 127.0.0.1
-- Tiempo de generación: 23-07-2025 a las 04:43:36
-- Versión del servidor: 11.8.2-MariaDB
-- Versión de PHP: 8.2.12

SET SQL_MODE = "NO_AUTO_VALUE_ON_ZERO";
START TRANSACTION;
SET time_zone = "+00:00";


/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET @OLD_CHARACTER_SET_RESULTS=@@CHARACTER_SET_RESULTS */;
/*!40101 SET @OLD_COLLATION_CONNECTION=@@COLLATION_CONNECTION */;
/*!40101 SET NAMES utf8mb4 */;

--
-- Base de datos: `urbanfood`
--

-- --------------------------------------------------------

--
-- Estructura de tabla para la tabla `auth`
--

CREATE TABLE `auth` (
  `id_auth` int(11) NOT NULL,
  `id_usuario` int(11) NOT NULL,
  `fecha_auth` timestamp NULL DEFAULT current_timestamp()
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

-- --------------------------------------------------------

--
-- Estructura Stand-in para la vista `catalogo_productos`
-- (Véase abajo para la vista actual)
--
CREATE TABLE `catalogo_productos` (
`id_producto` int(11)
,`nombre_producto` varchar(100)
,`descripcion` text
,`precio_producto` decimal(10,2)
,`stock_producto` int(11)
,`img_producto` text
,`id_vendedor` int(11)
,`nombre_vendedor` varchar(100)
,`id_categoria` int(11)
,`nombre_categoria` varchar(50)
,`valoraciones` varbinary(328)
);

-- --------------------------------------------------------

--
-- Estructura de tabla para la tabla `categorias`
--

CREATE TABLE `categorias` (
  `id_categoria` int(11) NOT NULL,
  `nombre_categoria` varchar(50) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

-- --------------------------------------------------------

--
-- Estructura de tabla para la tabla `clientes`
--

CREATE TABLE `clientes` (
  `id_cliente` int(11) NOT NULL,
  `nombre_cliente` varchar(50) NOT NULL,
  `apellido_cliente` varchar(50) NOT NULL,
  `email_cliente` varchar(100) NOT NULL,
  `two_factor_auth` varchar(255) DEFAULT NULL,
  `id_usuario` int(11) DEFAULT NULL,
  `telefono` varchar(20) DEFAULT NULL,
  `direccion_entrega` longtext CHARACTER SET utf8mb4 COLLATE utf8mb4_bin DEFAULT NULL CHECK (json_valid(`direccion_entrega`)),
  `horario_atencion` text DEFAULT NULL,
  `puntos_fidelidad` int(11) DEFAULT 0
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

-- --------------------------------------------------------

--
-- Estructura de tabla para la tabla `detalle_pedido`
--

CREATE TABLE `detalle_pedido` (
  `id_detalle` int(11) NOT NULL,
  `id_pedido` int(11) NOT NULL,
  `id_producto` int(11) NOT NULL,
  `cantidad_producto` int(11) NOT NULL DEFAULT 1,
  `precio_unitario` decimal(10,2) NOT NULL,
  `subtotal` decimal(10,2) GENERATED ALWAYS AS (`cantidad_producto` * `precio_unitario`) STORED,
  `notas` text DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

-- --------------------------------------------------------

--
-- Estructura Stand-in para la vista `detalle_pedidos_con_valoracion`
-- (Véase abajo para la vista actual)
--
CREATE TABLE `detalle_pedidos_con_valoracion` (
`id_detalle` int(11)
,`id_pedido` int(11)
,`id_producto` int(11)
,`nombre_producto` varchar(100)
,`descripcion` text
,`precio_producto` decimal(10,2)
,`cantidad_producto` int(11)
,`precio_unitario` decimal(10,2)
,`subtotal` decimal(10,2)
,`stock_producto` int(11)
,`id_categoria` int(11)
,`nombre_categoria` varchar(50)
,`id_vendedor` int(11)
,`nombre_vendedor` varchar(100)
,`valoracion_promedio` double
,`total_valoraciones` bigint(21)
);

-- --------------------------------------------------------

--
-- Estructura Stand-in para la vista `historial_pedidos_cliente`
-- (Véase abajo para la vista actual)
--
CREATE TABLE `historial_pedidos_cliente` (
`id_pedido` int(11)
,`fecha_pedido` timestamp
,`total` decimal(10,2)
,`estado_pedido` longtext
,`nombre_vendedor` varchar(100)
,`nombre_categoria` varchar(50)
);

-- --------------------------------------------------------

--
-- Estructura Stand-in para la vista `historial_pedidos_repartidor`
-- (Véase abajo para la vista actual)
--
CREATE TABLE `historial_pedidos_repartidor` (
`id_pedido` int(11)
,`fecha_pedido` timestamp
,`total` decimal(10,2)
,`estado_pedido` longtext
);

-- --------------------------------------------------------

--
-- Estructura Stand-in para la vista `historial_pedidos_vendedor`
-- (Véase abajo para la vista actual)
--
CREATE TABLE `historial_pedidos_vendedor` (
`id_pedido` int(11)
,`fecha_pedido` timestamp
,`total` decimal(10,2)
,`estado_pedido` longtext
);

-- --------------------------------------------------------

--
-- Estructura de tabla para la tabla `negocios`
--

CREATE TABLE `negocios` (
  `id_negocio` int(11) NOT NULL,
  `direccion_negocio` longtext CHARACTER SET utf8mb4 COLLATE utf8mb4_bin NOT NULL CHECK (json_valid(`direccion_negocio`)),
  `nombre_negocio` varchar(100) NOT NULL,
  `img_negocio` text DEFAULT NULL,
  `telefono_negocio` varchar(20) DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

-- --------------------------------------------------------

--
-- Estructura de tabla para la tabla `pedidos`
--

CREATE TABLE `pedidos` (
  `id_pedido` int(11) NOT NULL,
  `fecha_pedido` timestamp NULL DEFAULT current_timestamp(),
  `estado_pedido` longtext CHARACTER SET utf8mb4 COLLATE utf8mb4_bin NOT NULL CHECK (json_valid(`estado_pedido`)),
  `two_factor_auth` varchar(255) DEFAULT NULL,
  `img_pedido` text DEFAULT NULL,
  `direccion_pedido` longtext CHARACTER SET utf8mb4 COLLATE utf8mb4_bin NOT NULL CHECK (json_valid(`direccion_pedido`)),
  `id_cliente` int(11) NOT NULL,
  `id_repartidor` int(11) DEFAULT NULL,
  `id_vendedor` int(11) NOT NULL,
  `total` decimal(10,2) NOT NULL,
  `metodo_pago` varchar(50) DEFAULT NULL,
  `instrucciones_entrega` text DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Disparadores `pedidos`
--
DELIMITER $$
CREATE TRIGGER `after_pedido_insert` AFTER INSERT ON `pedidos` FOR EACH ROW BEGIN
    UPDATE productos p
    JOIN detalle_pedido dp ON p.id_producto = dp.id_producto
    SET p.stock_producto = p.stock_producto - dp.cantidad_producto
    WHERE dp.id_pedido = NEW.id_pedido;
END
$$
DELIMITER ;

-- --------------------------------------------------------

--
-- Estructura Stand-in para la vista `pedidos_con_detalle_valoracion`
-- (Véase abajo para la vista actual)
--
CREATE TABLE `pedidos_con_detalle_valoracion` (
`id_pedido` int(11)
,`fecha_pedido` timestamp
,`total` decimal(10,2)
,`estado_pedido` longtext
,`metodo_pago` varchar(50)
,`id_cliente` int(11)
,`nombre_cliente` varchar(50)
,`id_repartidor` int(11)
,`nombre_repartidor` varchar(50)
,`id_vendedor` int(11)
,`nombre_vendedor` varchar(100)
,`total_items` decimal(32,0)
,`subtotal_pedido` decimal(32,2)
,`valoracion_promedio_pedido` double
,`total_valoraciones_pedido` bigint(21)
);

-- --------------------------------------------------------

--
-- Estructura de tabla para la tabla `productos`
--

CREATE TABLE `productos` (
  `id_producto` int(11) NOT NULL,
  `nombre_producto` varchar(100) NOT NULL,
  `id_vendedor` int(11) NOT NULL,
  `id_categoria` int(11) DEFAULT NULL,
  `img_producto` text DEFAULT NULL,
  `precio_producto` decimal(10,2) NOT NULL,
  `stock_producto` int(11) DEFAULT 0,
  `descripcion` text DEFAULT NULL,
  `fecha_creacion` timestamp NULL DEFAULT current_timestamp()
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

-- --------------------------------------------------------

--
-- Estructura Stand-in para la vista `productos_filtrables`
-- (Véase abajo para la vista actual)
--
CREATE TABLE `productos_filtrables` (
`id_producto` int(11)
,`nombre_producto` varchar(100)
,`descripcion` text
,`precio_producto` decimal(10,2)
,`stock_producto` int(11)
,`img_producto` text
,`id_categoria` int(11)
,`nombre_categoria` varchar(50)
,`id_vendedor` int(11)
,`nombre_vendedor` varchar(100)
,`valoracion_promedio` double
,`total_valoraciones` bigint(21)
);

-- --------------------------------------------------------

--
-- Estructura de tabla para la tabla `repartidores`
--

CREATE TABLE `repartidores` (
  `id_repartidor` int(11) NOT NULL,
  `nombre_repartidor` varchar(50) NOT NULL,
  `apellido_repartidor` varchar(50) NOT NULL,
  `email_repartidor` varchar(100) NOT NULL,
  `id_usuario` int(11) DEFAULT NULL,
  `telefono` varchar(20) DEFAULT NULL,
  `estado` tinyint(1) DEFAULT 1,
  `calificacion_promedio` decimal(3,2) DEFAULT 5.00
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

-- --------------------------------------------------------

--
-- Estructura de tabla para la tabla `universidades`
--

CREATE TABLE `universidades` (
  `id_universidad` int(11) NOT NULL,
  `id_negocio` int(11) NOT NULL,
  `nombre_universidad` varchar(100) NOT NULL,
  `direccion_universidad` longtext CHARACTER SET utf8mb4 COLLATE utf8mb4_bin NOT NULL CHECK (json_valid(`direccion_universidad`)),
  `img_universidad` text DEFAULT NULL,
  `telefono_contacto` varchar(20) DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

-- --------------------------------------------------------

--
-- Estructura de tabla para la tabla `usuarios`
--

CREATE TABLE `usuarios` (
  `id_usuario` int(11) NOT NULL,
  `nombre_usuario` varchar(50) NOT NULL,
  `apellido_usuario` varchar(50) NOT NULL,
  `img_usuario` text DEFAULT NULL,
  `id_auth` int(11) DEFAULT NULL,
  `email_usuario` varchar(100) NOT NULL,
  `fecha_registro` timestamp NULL DEFAULT current_timestamp(),
  `contrasena_usuario` varchar(255) NOT NULL,
  `rol_usuario` enum('cliente','repartidor','vendedor') NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

-- --------------------------------------------------------

--
-- Estructura de tabla para la tabla `valoracion_producto`
--

CREATE TABLE `valoracion_producto` (
  `id_valoracion` int(11) NOT NULL,
  `id_producto` int(11) NOT NULL,
  `id_vendedor` int(11) NOT NULL,
  `id_usuario` int(11) NOT NULL,
  `valoracion` longtext CHARACTER SET utf8mb4 COLLATE utf8mb4_bin NOT NULL CHECK (json_valid(`valoracion`)),
  `fecha_creacion` timestamp NULL DEFAULT current_timestamp()
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

-- --------------------------------------------------------

--
-- Estructura de tabla para la tabla `vendedor`
--

CREATE TABLE `vendedor` (
  `id_vendedor` int(11) NOT NULL,
  `nombre_vendedor` varchar(100) NOT NULL,
  `id_negocio` longtext CHARACTER SET utf8mb4 COLLATE utf8mb4_bin NOT NULL CHECK (json_valid(`id_negocio`)),
  `telefono_vendedor` varchar(20) DEFAULT NULL,
  `id_usuario` int(11) DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

-- --------------------------------------------------------

--
-- Estructura para la vista `catalogo_productos`
--
DROP TABLE IF EXISTS `catalogo_productos`;

CREATE ALGORITHM=UNDEFINED DEFINER=`root`@`localhost` SQL SECURITY DEFINER VIEW `catalogo_productos`  AS SELECT `p`.`id_producto` AS `id_producto`, `p`.`nombre_producto` AS `nombre_producto`, `p`.`descripcion` AS `descripcion`, `p`.`precio_producto` AS `precio_producto`, `p`.`stock_producto` AS `stock_producto`, `p`.`img_producto` AS `img_producto`, `v`.`id_vendedor` AS `id_vendedor`, `v`.`nombre_vendedor` AS `nombre_vendedor`, `c`.`id_categoria` AS `id_categoria`, `c`.`nombre_categoria` AS `nombre_categoria`, coalesce((select json_object('puntuacion',avg(json_extract(`vp`.`valoracion`,'$.estrellas')),'total_valoraciones',count(0)) from `valoracion_producto` `vp` where `vp`.`id_producto` = `p`.`id_producto` group by `vp`.`id_producto`),json_object('puntuacion',0,'total_valoraciones',0)) AS `valoraciones` FROM ((`productos` `p` left join `vendedor` `v` on(`p`.`id_vendedor` = `v`.`id_vendedor`)) left join `categorias` `c` on(`p`.`id_categoria` = `c`.`id_categoria`)) WHERE `p`.`stock_producto` > 0 ;

-- --------------------------------------------------------

--
-- Estructura para la vista `detalle_pedidos_con_valoracion`
--
DROP TABLE IF EXISTS `detalle_pedidos_con_valoracion`;

CREATE ALGORITHM=UNDEFINED DEFINER=`root`@`localhost` SQL SECURITY DEFINER VIEW `detalle_pedidos_con_valoracion`  AS SELECT `dp`.`id_detalle` AS `id_detalle`, `dp`.`id_pedido` AS `id_pedido`, `dp`.`id_producto` AS `id_producto`, `p`.`nombre_producto` AS `nombre_producto`, `p`.`descripcion` AS `descripcion`, `p`.`precio_producto` AS `precio_producto`, `dp`.`cantidad_producto` AS `cantidad_producto`, `dp`.`precio_unitario` AS `precio_unitario`, `dp`.`subtotal` AS `subtotal`, `p`.`stock_producto` AS `stock_producto`, `c`.`id_categoria` AS `id_categoria`, `c`.`nombre_categoria` AS `nombre_categoria`, `v`.`id_vendedor` AS `id_vendedor`, `v`.`nombre_vendedor` AS `nombre_vendedor`, coalesce((select avg(json_extract(`vp`.`valoracion`,'$.estrellas')) from `valoracion_producto` `vp` where `vp`.`id_producto` = `p`.`id_producto`),0) AS `valoracion_promedio`, (select count(0) from `valoracion_producto` `vp` where `vp`.`id_producto` = `p`.`id_producto`) AS `total_valoraciones` FROM (((`detalle_pedido` `dp` join `productos` `p` on(`dp`.`id_producto` = `p`.`id_producto`)) left join `categorias` `c` on(`p`.`id_categoria` = `c`.`id_categoria`)) left join `vendedor` `v` on(`p`.`id_vendedor` = `v`.`id_vendedor`)) ;

-- --------------------------------------------------------

--
-- Estructura para la vista `historial_pedidos_cliente`
--
DROP TABLE IF EXISTS `historial_pedidos_cliente`;

CREATE ALGORITHM=UNDEFINED DEFINER=`root`@`localhost` SQL SECURITY DEFINER VIEW `historial_pedidos_cliente`  AS SELECT `p`.`id_pedido` AS `id_pedido`, `p`.`fecha_pedido` AS `fecha_pedido`, `p`.`total` AS `total`, `p`.`estado_pedido` AS `estado_pedido`, `v`.`nombre_vendedor` AS `nombre_vendedor`, `c`.`nombre_categoria` AS `nombre_categoria` FROM ((`pedidos` `p` left join `vendedor` `v` on(`p`.`id_vendedor` = `v`.`id_vendedor`)) left join `categorias` `c` on(`c`.`id_categoria` = (select `pr`.`id_categoria` from `productos` `pr` where `pr`.`id_producto` = (select `dp`.`id_producto` from `detalle_pedido` `dp` where `dp`.`id_pedido` = `p`.`id_pedido` limit 1)))) WHERE `p`.`id_cliente` = (select `clientes`.`id_cliente` from `clientes` where `clientes`.`id_usuario` = (select `auth`.`id_usuario` from `auth` order by `auth`.`fecha_auth` desc limit 1)) ;

-- --------------------------------------------------------

--
-- Estructura para la vista `historial_pedidos_repartidor`
--
DROP TABLE IF EXISTS `historial_pedidos_repartidor`;

CREATE ALGORITHM=UNDEFINED DEFINER=`root`@`localhost` SQL SECURITY DEFINER VIEW `historial_pedidos_repartidor`  AS SELECT `p`.`id_pedido` AS `id_pedido`, `p`.`fecha_pedido` AS `fecha_pedido`, `p`.`total` AS `total`, `p`.`estado_pedido` AS `estado_pedido` FROM `pedidos` AS `p` WHERE `p`.`id_repartidor` = (select `repartidores`.`id_repartidor` from `repartidores` where `repartidores`.`id_usuario` = (select `auth`.`id_usuario` from `auth` order by `auth`.`fecha_auth` desc limit 1)) ;

-- --------------------------------------------------------

--
-- Estructura para la vista `historial_pedidos_vendedor`
--
DROP TABLE IF EXISTS `historial_pedidos_vendedor`;

CREATE ALGORITHM=UNDEFINED DEFINER=`root`@`localhost` SQL SECURITY DEFINER VIEW `historial_pedidos_vendedor`  AS SELECT `p`.`id_pedido` AS `id_pedido`, `p`.`fecha_pedido` AS `fecha_pedido`, `p`.`total` AS `total`, `p`.`estado_pedido` AS `estado_pedido` FROM `pedidos` AS `p` WHERE `p`.`id_vendedor` = (select `vendedor`.`id_vendedor` from `vendedor` where `vendedor`.`id_usuario` = (select `auth`.`id_usuario` from `auth` order by `auth`.`fecha_auth` desc limit 1)) ;

-- --------------------------------------------------------

--
-- Estructura para la vista `pedidos_con_detalle_valoracion`
--
DROP TABLE IF EXISTS `pedidos_con_detalle_valoracion`;

CREATE ALGORITHM=UNDEFINED DEFINER=`root`@`localhost` SQL SECURITY DEFINER VIEW `pedidos_con_detalle_valoracion`  AS SELECT `p`.`id_pedido` AS `id_pedido`, `p`.`fecha_pedido` AS `fecha_pedido`, `p`.`total` AS `total`, `p`.`estado_pedido` AS `estado_pedido`, `p`.`metodo_pago` AS `metodo_pago`, `c`.`id_cliente` AS `id_cliente`, `c`.`nombre_cliente` AS `nombre_cliente`, `r`.`id_repartidor` AS `id_repartidor`, `r`.`nombre_repartidor` AS `nombre_repartidor`, `v`.`id_vendedor` AS `id_vendedor`, `v`.`nombre_vendedor` AS `nombre_vendedor`, sum(`dp`.`cantidad_producto`) AS `total_items`, sum(`dp`.`subtotal`) AS `subtotal_pedido`, avg(coalesce((select avg(json_extract(`vp`.`valoracion`,'$.estrellas')) from `valoracion_producto` `vp` where `vp`.`id_producto` = `dp`.`id_producto`),0)) AS `valoracion_promedio_pedido`, (select count(distinct `vp`.`id_valoracion`) from (`detalle_pedido` `dp2` join `valoracion_producto` `vp` on(`dp2`.`id_producto` = `vp`.`id_producto`)) where `dp2`.`id_pedido` = `p`.`id_pedido`) AS `total_valoraciones_pedido` FROM ((((`pedidos` `p` join `clientes` `c` on(`p`.`id_cliente` = `c`.`id_cliente`)) left join `repartidores` `r` on(`p`.`id_repartidor` = `r`.`id_repartidor`)) left join `vendedor` `v` on(`p`.`id_vendedor` = `v`.`id_vendedor`)) join `detalle_pedido` `dp` on(`dp`.`id_pedido` = `p`.`id_pedido`)) GROUP BY `p`.`id_pedido`, `c`.`id_cliente`, `r`.`id_repartidor`, `v`.`id_vendedor` ;

-- --------------------------------------------------------

--
-- Estructura para la vista `productos_filtrables`
--
DROP TABLE IF EXISTS `productos_filtrables`;

CREATE ALGORITHM=UNDEFINED DEFINER=`root`@`localhost` SQL SECURITY DEFINER VIEW `productos_filtrables`  AS SELECT `p`.`id_producto` AS `id_producto`, `p`.`nombre_producto` AS `nombre_producto`, `p`.`descripcion` AS `descripcion`, `p`.`precio_producto` AS `precio_producto`, `p`.`stock_producto` AS `stock_producto`, `p`.`img_producto` AS `img_producto`, `c`.`id_categoria` AS `id_categoria`, `c`.`nombre_categoria` AS `nombre_categoria`, `v`.`id_vendedor` AS `id_vendedor`, `v`.`nombre_vendedor` AS `nombre_vendedor`, coalesce((select avg(json_extract(`vp`.`valoracion`,'$.estrellas')) from `valoracion_producto` `vp` where `vp`.`id_producto` = `p`.`id_producto`),0) AS `valoracion_promedio`, (select count(0) from `valoracion_producto` `vp` where `vp`.`id_producto` = `p`.`id_producto`) AS `total_valoraciones` FROM ((`productos` `p` left join `categorias` `c` on(`p`.`id_categoria` = `c`.`id_categoria`)) left join `vendedor` `v` on(`p`.`id_vendedor` = `v`.`id_vendedor`)) WHERE `p`.`stock_producto` > 0 ;

--
-- Índices para tablas volcadas
--

--
-- Indices de la tabla `auth`
--
ALTER TABLE `auth`
  ADD PRIMARY KEY (`id_auth`),
  ADD KEY `id_usuario` (`id_usuario`);

--
-- Indices de la tabla `categorias`
--
ALTER TABLE `categorias`
  ADD PRIMARY KEY (`id_categoria`),
  ADD UNIQUE KEY `nombre_categoria` (`nombre_categoria`),
  ADD KEY `idx_categorias_nombre` (`nombre_categoria`);

--
-- Indices de la tabla `clientes`
--
ALTER TABLE `clientes`
  ADD PRIMARY KEY (`id_cliente`),
  ADD UNIQUE KEY `email_cliente` (`email_cliente`),
  ADD KEY `id_usuario` (`id_usuario`);

--
-- Indices de la tabla `detalle_pedido`
--
ALTER TABLE `detalle_pedido`
  ADD PRIMARY KEY (`id_detalle`),
  ADD KEY `idx_detalle_pedido_pedido` (`id_pedido`),
  ADD KEY `idx_detalle_pedido_producto` (`id_producto`);

--
-- Indices de la tabla `negocios`
--
ALTER TABLE `negocios`
  ADD PRIMARY KEY (`id_negocio`);

--
-- Indices de la tabla `pedidos`
--
ALTER TABLE `pedidos`
  ADD PRIMARY KEY (`id_pedido`),
  ADD KEY `idx_pedidos_cliente` (`id_cliente`),
  ADD KEY `idx_pedidos_vendedor` (`id_vendedor`),
  ADD KEY `idx_pedidos_repartidor` (`id_repartidor`);

--
-- Indices de la tabla `productos`
--
ALTER TABLE `productos`
  ADD PRIMARY KEY (`id_producto`),
  ADD KEY `idx_productos_vendedor` (`id_vendedor`),
  ADD KEY `idx_productos_categoria` (`id_categoria`);

--
-- Indices de la tabla `repartidores`
--
ALTER TABLE `repartidores`
  ADD PRIMARY KEY (`id_repartidor`),
  ADD UNIQUE KEY `email_repartidor` (`email_repartidor`),
  ADD KEY `id_usuario` (`id_usuario`);

--
-- Indices de la tabla `universidades`
--
ALTER TABLE `universidades`
  ADD PRIMARY KEY (`id_universidad`),
  ADD KEY `id_negocio` (`id_negocio`);

--
-- Indices de la tabla `usuarios`
--
ALTER TABLE `usuarios`
  ADD PRIMARY KEY (`id_usuario`),
  ADD UNIQUE KEY `email_usuario` (`email_usuario`),
  ADD KEY `id_auth` (`id_auth`);

--
-- Indices de la tabla `valoracion_producto`
--
ALTER TABLE `valoracion_producto`
  ADD PRIMARY KEY (`id_valoracion`),
  ADD KEY `id_vendedor` (`id_vendedor`),
  ADD KEY `id_usuario` (`id_usuario`),
  ADD KEY `idx_valoracion_producto` (`id_producto`,`id_usuario`);

--
-- Indices de la tabla `vendedor`
--
ALTER TABLE `vendedor`
  ADD PRIMARY KEY (`id_vendedor`),
  ADD KEY `id_usuario` (`id_usuario`);

--
-- AUTO_INCREMENT de las tablas volcadas
--

--
-- AUTO_INCREMENT de la tabla `auth`
--
ALTER TABLE `auth`
  MODIFY `id_auth` int(11) NOT NULL AUTO_INCREMENT;

--
-- AUTO_INCREMENT de la tabla `categorias`
--
ALTER TABLE `categorias`
  MODIFY `id_categoria` int(11) NOT NULL AUTO_INCREMENT;

--
-- AUTO_INCREMENT de la tabla `clientes`
--
ALTER TABLE `clientes`
  MODIFY `id_cliente` int(11) NOT NULL AUTO_INCREMENT;

--
-- AUTO_INCREMENT de la tabla `detalle_pedido`
--
ALTER TABLE `detalle_pedido`
  MODIFY `id_detalle` int(11) NOT NULL AUTO_INCREMENT;

--
-- AUTO_INCREMENT de la tabla `negocios`
--
ALTER TABLE `negocios`
  MODIFY `id_negocio` int(11) NOT NULL AUTO_INCREMENT;

--
-- AUTO_INCREMENT de la tabla `pedidos`
--
ALTER TABLE `pedidos`
  MODIFY `id_pedido` int(11) NOT NULL AUTO_INCREMENT;

--
-- AUTO_INCREMENT de la tabla `productos`
--
ALTER TABLE `productos`
  MODIFY `id_producto` int(11) NOT NULL AUTO_INCREMENT;

--
-- AUTO_INCREMENT de la tabla `repartidores`
--
ALTER TABLE `repartidores`
  MODIFY `id_repartidor` int(11) NOT NULL AUTO_INCREMENT;

--
-- AUTO_INCREMENT de la tabla `universidades`
--
ALTER TABLE `universidades`
  MODIFY `id_universidad` int(11) NOT NULL AUTO_INCREMENT;

--
-- AUTO_INCREMENT de la tabla `usuarios`
--
ALTER TABLE `usuarios`
  MODIFY `id_usuario` int(11) NOT NULL AUTO_INCREMENT;

--
-- AUTO_INCREMENT de la tabla `valoracion_producto`
--
ALTER TABLE `valoracion_producto`
  MODIFY `id_valoracion` int(11) NOT NULL AUTO_INCREMENT;

--
-- AUTO_INCREMENT de la tabla `vendedor`
--
ALTER TABLE `vendedor`
  MODIFY `id_vendedor` int(11) NOT NULL AUTO_INCREMENT;

--
-- Restricciones para tablas volcadas
--

--
-- Filtros para la tabla `auth`
--
ALTER TABLE `auth`
  ADD CONSTRAINT `auth_ibfk_1` FOREIGN KEY (`id_usuario`) REFERENCES `usuarios` (`id_usuario`) ON DELETE CASCADE;

--
-- Filtros para la tabla `clientes`
--
ALTER TABLE `clientes`
  ADD CONSTRAINT `clientes_ibfk_1` FOREIGN KEY (`id_usuario`) REFERENCES `usuarios` (`id_usuario`) ON DELETE SET NULL;

--
-- Filtros para la tabla `detalle_pedido`
--
ALTER TABLE `detalle_pedido`
  ADD CONSTRAINT `detalle_pedido_ibfk_1` FOREIGN KEY (`id_pedido`) REFERENCES `pedidos` (`id_pedido`) ON DELETE CASCADE,
  ADD CONSTRAINT `detalle_pedido_ibfk_2` FOREIGN KEY (`id_producto`) REFERENCES `productos` (`id_producto`) ON DELETE CASCADE;

--
-- Filtros para la tabla `pedidos`
--
ALTER TABLE `pedidos`
  ADD CONSTRAINT `pedidos_ibfk_1` FOREIGN KEY (`id_cliente`) REFERENCES `clientes` (`id_cliente`) ON DELETE CASCADE,
  ADD CONSTRAINT `pedidos_ibfk_2` FOREIGN KEY (`id_repartidor`) REFERENCES `repartidores` (`id_repartidor`) ON DELETE SET NULL,
  ADD CONSTRAINT `pedidos_ibfk_3` FOREIGN KEY (`id_vendedor`) REFERENCES `vendedor` (`id_vendedor`) ON DELETE CASCADE;

--
-- Filtros para la tabla `productos`
--
ALTER TABLE `productos`
  ADD CONSTRAINT `productos_ibfk_1` FOREIGN KEY (`id_vendedor`) REFERENCES `vendedor` (`id_vendedor`) ON DELETE CASCADE,
  ADD CONSTRAINT `productos_ibfk_2` FOREIGN KEY (`id_categoria`) REFERENCES `categorias` (`id_categoria`) ON DELETE SET NULL;

--
-- Filtros para la tabla `repartidores`
--
ALTER TABLE `repartidores`
  ADD CONSTRAINT `repartidores_ibfk_1` FOREIGN KEY (`id_usuario`) REFERENCES `usuarios` (`id_usuario`) ON DELETE SET NULL;

--
-- Filtros para la tabla `universidades`
--
ALTER TABLE `universidades`
  ADD CONSTRAINT `universidades_ibfk_1` FOREIGN KEY (`id_negocio`) REFERENCES `negocios` (`id_negocio`) ON DELETE CASCADE;

--
-- Filtros para la tabla `usuarios`
--
ALTER TABLE `usuarios`
  ADD CONSTRAINT `usuarios_ibfk_1` FOREIGN KEY (`id_auth`) REFERENCES `auth` (`id_auth`) ON DELETE SET NULL;

--
-- Filtros para la tabla `valoracion_producto`
--
ALTER TABLE `valoracion_producto`
  ADD CONSTRAINT `valoracion_producto_ibfk_1` FOREIGN KEY (`id_producto`) REFERENCES `productos` (`id_producto`) ON DELETE CASCADE,
  ADD CONSTRAINT `valoracion_producto_ibfk_2` FOREIGN KEY (`id_vendedor`) REFERENCES `vendedor` (`id_vendedor`) ON DELETE CASCADE,
  ADD CONSTRAINT `valoracion_producto_ibfk_3` FOREIGN KEY (`id_usuario`) REFERENCES `usuarios` (`id_usuario`) ON DELETE CASCADE;

--
-- Filtros para la tabla `vendedor`
--
ALTER TABLE `vendedor`
  ADD CONSTRAINT `vendedor_ibfk_1` FOREIGN KEY (`id_usuario`) REFERENCES `usuarios` (`id_usuario`) ON DELETE SET NULL;
COMMIT;

/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
