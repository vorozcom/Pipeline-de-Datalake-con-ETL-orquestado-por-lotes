/*
    PROYECTO: Pipeline de Data Lake con ETL Orquestado
    ARCHIVO: consultas_athena.sql
    DESCRIPCIÓN: Script de validación y análisis de datos de Ventas (Parquet).
    TABLA: processed
*/

-------------------------------------------------------------
-- 1. VALIDACIÓN INICIAL (Sanity Check)
-- Objetivo: Verificar que las columnas clave se leen correctamente 
-- y que el formato de fecha y números es coherente.
-------------------------------------------------------------
SELECT 
    date,
    product_id,
    category,
    city,
    quantity,
    discount
FROM processed
LIMIT 10;


-------------------------------------------------------------
-- 2. CALIDAD DE DATOS (Data Quality)
-- Objetivo: Contar el volumen total de ventas procesadas y 
-- verificar cuántos productos únicos se han vendido en este lote.
-------------------------------------------------------------
SELECT 
    COUNT(*) AS total_transacciones,
    COUNT(DISTINCT product_id) AS productos_unicos,
    COUNT(DISTINCT city) AS ciudades_activas
FROM processed;


-------------------------------------------------------------
-- 3. ANÁLISIS DE NEGOCIO: TOP CATEGORÍAS (BI Readiness)
-- Objetivo: Identificar qué categorías mueven más volumen de producto.
-- Esta consulta alimenta directamente el Dashboard de QuickSight.
-------------------------------------------------------------
SELECT 
    category, 
    SUM(quantity) AS total_unidades_vendidas,
    AVG(discount) AS descuento_promedio
FROM processed
GROUP BY category
ORDER BY total_unidades_vendidas DESC
LIMIT 5;


-------------------------------------------------------------
-- 4. ANÁLISIS GEOGRÁFICO (Opcional)
-- Objetivo: Ver qué ciudades tienen el mayor volumen de ventas.
-------------------------------------------------------------
SELECT 
    city,
    SUM(quantity) AS total_unidades
FROM processed
GROUP BY city
ORDER BY total_unidades DESC
LIMIT 5;
