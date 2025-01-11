from datetime import datetime, timedelta

def VENTAS(año=None, mes=None):
    # Si no se pasa un año, se usa el año actual
    if not año:
        año = datetime.now().year
    
    # Si no se pasa un mes, se usa el mes actual
    if not mes:
        mes = datetime.now().month

    # Formatear las fechas de inicio y fin del mes
    fecha_inicio = f"{año}-{mes:02d}-01"  # Primer día del mes
    fecha_fin = f"{año}-{mes:02d}-{(datetime(año, mes, 1) - timedelta(days=1)).day}"  # Último día del mes


    return f"""
    SELECT
        v.id AS venta_id, v.total AS venta_total, v.tipo AS venta_tipo,
        v.cliente_id AS venta_cliente, FROM_UNIXTIME(v.created_at) AS fecha
    FROM venta AS v
    WHERE FROM_UNIXTIME(v.created_at) >= '{fecha_inicio}' AND FROM_UNIXTIME(v.created_at) <= '{fecha_fin}';
    """

def CREDITO(año=None, mes=None):
    # Si no se pasa un año, se usa el año actual
    if not año:
        año = datetime.now().year
    
    # Si no se pasa un mes, se usa el mes actual
    if not mes:
        mes = datetime.now().month

    # Formatear las fechas de inicio y fin del mes
    fecha_inicio = f"{año}-{mes:02d}-01"  # Primer día del mes
    fecha_fin = f"{año}-{mes:02d}-{(datetime(año, mes, 1) - timedelta(days=1)).day}"  # Último día del mes
    
    return f"""
    SELECT c.id AS credito_id, c.venta_id, c.cliente_id, c.monto,
        c.status, c.tipo, FROM_UNIXTIME(c.created_at) AS fecha
    FROM credito AS c
    WHERE c.tipo = 10 AND FROM_UNIXTIME(c.created_at) BETWEEN '{fecha_inicio}' AND '{fecha_fin}';
    """

def ABONO(año=None, mes=None):
    # Si no se pasa un año, se usa el año actual
    if not año:
        año = datetime.now().year
    
    # Si no se pasa un mes, se usa el mes actual
    if not mes:
        mes = datetime.now().month

    # Formatear las fechas de inicio y fin del mes
    fecha_inicio = f"{año}-{mes:02d}-01"  # Primer día del mes
    fecha_fin = f"{año}-{mes:02d}-{(datetime(año, mes, 1) - timedelta(days=1)).day}"  # Último día del mes
    return  f"""
    SELECT
        ca.id AS credito_abono_id, ca.credito_id, ca.cantidad, ca.status, ca.token_pay,
        c.venta_id, c.cliente_id, FROM_UNIXTIME(ca.created_at) AS fecha
    FROM credito_abono AS ca
    JOIN credito AS c ON c.id = ca.credito_id
    WHERE c.tipo = 10 AND FROM_UNIXTIME(ca.created_at) BETWEEN '{fecha_inicio}' AND '{fecha_fin}';
    """



def VENTA_DETALLE(fecha_inicio=None, fecha_fin=None):
    """
    Genera una consulta SQL completa con las fechas ya incrustadas.
    Si no se especifican fechas, usa el rango desde un año atrás hasta la fecha actual.

    :param fecha_inicio: Fecha de inicio en formato 'YYYY-MM-DD' (opcional).
    :param fecha_fin: Fecha de fin en formato 'YYYY-MM-DD' (opcional).
    :return: Consulta SQL como cadena con las fechas ya aplicadas.
    """
    # Si no se especifican fechas, usa un rango de un año
    if not fecha_inicio or not fecha_fin:
        fecha_actual = datetime.now()
        fecha_inicio = (fecha_actual - timedelta(days=365)).strftime('%Y-%m-%d')
        fecha_fin = fecha_actual.strftime('%Y-%m-%d')

    consulta_sql = f"""
    SELECT
        vd.id,
        p.nombre AS producto,
        p.costo,
        vd.cantidad,
        p.tipo_medida,
        CASE
            WHEN p.tipo_medida = 20 THEN 'Kilos'
            WHEN p.tipo_medida = 10 THEN 'Piezas'
            ELSE '--'
        END AS unidad_medida,
        DATE(FROM_UNIXTIME(vd.created_at)) AS fecha,
        TIME(FROM_UNIXTIME(vd.created_at)) AS hora
    FROM
        venta_detalle AS vd
    INNER JOIN
        producto AS p ON p.id = vd.producto_id
    INNER JOIN
        user AS u ON u.id = vd.created_by
    LEFT JOIN
        venta AS v ON vd.venta_id = v.id
    LEFT JOIN
        cliente AS c ON c.id = v.cliente_id
    LEFT JOIN
        sucursal AS suc ON v.ruta_sucursal_id = suc.id
    LEFT JOIN
        sucursal AS pertenece ON v.sucursal_id = pertenece.id
    WHERE
        DATE(FROM_UNIXTIME(vd.created_at)) BETWEEN '{fecha_inicio}' AND '{fecha_fin}'
    """
    #print( consulta_sql.strip())
    return consulta_sql.strip()


""""
====================================================
    COMPRAS
====================================================
"""
def COMPRAS_PROVEDOR_C(año_ini, mes_ini, dia_ini, año_fin, mes_fin, dia_fin):
    fecha_inicio = f"{año_ini}-{mes_ini:02d}-{dia_ini:02d}"
    fecha_fin = f"{año_fin}-{mes_fin:02d}-{dia_fin:02d}"
    
    sql = f"""
    SELECT 
        cm.id AS id,
        cm.total AS total_compra,
        cm.`status`,
        pr.nombre AS proveedor,
        pr.id AS proveedor_id,
        FROM_UNIXTIME(cm.created_at) AS fecha,
        FROM_UNIXTIME(cm.fecha_salida) AS fecha_salida
    FROM compra AS cm   
    JOIN proveedor AS pr ON pr.id = cm.proveedor_id
    WHERE cm.`status` = 40
    AND FROM_UNIXTIME(cm.created_at) BETWEEN '{fecha_inicio}' AND '{fecha_fin}'
    ORDER BY id DESC;
    """
    return sql

def CREDITO_PROVEDOR(año_ini, mes_ini, dia_ini, año_fin, mes_fin, dia_fin):
    fecha_inicio = f"{año_ini}-{mes_ini:02d}-{dia_ini:02d}"
    fecha_fin = f"{año_fin}-{mes_fin:02d}-{dia_fin:02d}"
    
    sql = f"""
    SELECT
        c.id AS credito_id,
        round(c.monto, 2) AS monto_credito,
        c.compra_id,
        cm.total AS moto_compra,
        pr.nombre AS proveedor,
        pr.id AS id_proveedor,
        c.`status`, c.tipo,
        FROM_UNIXTIME(c.created_at) AS fecha
    FROM credito AS c
    INNER JOIN compra AS cm ON cm.id = c.compra_id
    INNER JOIN proveedor AS pr ON pr.id = cm.proveedor_id
    WHERE c.`status` != 20
    AND FROM_UNIXTIME(c.created_at) BETWEEN '{fecha_inicio}' AND '{fecha_fin}'
    """
    return sql


def ABONO_PROVEDOR(año_ini, mes_ini, dia_ini, año_fin, mes_fin, dia_fin):
    fecha_inicio = f"{año_ini}-{mes_ini:02d}-{dia_ini:02d}"
    fecha_fin = f"{año_fin}-{mes_fin:02d}-{dia_fin:02d}"
    
    sql = f"""
    SELECT
        ca.id AS credito_abono_id, 
        ca.credito_id,
        ca.cantidad,
        upper(pr.nombre) AS proveedor,
        FROM_UNIXTIME(ca.created_at) AS fecha
    FROM credito_abono AS ca
    JOIN credito AS c ON c.id = ca.credito_id
    JOIN compra AS cm ON cm.id = c.compra_id
    JOIN proveedor AS pr ON pr.id = cm.proveedor_id
    WHERE ca.`status` = 10
    AND FROM_UNIXTIME(ca.created_at) BETWEEN '{fecha_inicio}' AND '{fecha_fin}'
    """
    return sql


PROOVEDORES_LIST = """
SELECT 
pr.id,
UPPER(pr.nombre) AS proveedor,
COUNT(cm.proveedor_id) AS total_compras
FROM compra AS cm
JOIN proveedor AS pr ON pr.id = cm.proveedor_id
WHERE cm.`status` = 40
GROUP BY cm.proveedor_id
ORDER BY total_compras DESC 
"""


COMPRAS_PROVEDOR = """
SELECT 
    cd.id,
    -- COMPRA 
    cd.compra_id AS id_compra,
    -- cm.`status`,
    
    
    -- PRODUCTO 
    p.id AS id_product, 
    p.nombre AS nombre_product,
    -- p.tipo AS tipo_product, 
    p.tipo_medida AS tipo_medida_product,
    -- p.costo AS costo_product, 

    -- COMPRA DETALLE
    cd.cantidad AS cantidad_compra, 
    cd.costo AS costo_compra,
    cm.total,
    
    -- FECHA 
    FROM_UNIXTIME(cd.created_at) AS fecha,
    -- PROOVEDOR 
    pr.id AS id_proveedor,
    UPPER(pr.nombre) AS proveedor
    

FROM compra_detalle AS cd
INNER JOIN producto AS p ON p.id = cd.producto_id
INNER  JOIN compra AS cm ON cd.compra_id = cm.id 
LEFT JOIN proveedor pr ON cm.proveedor_id = pr.id
WHERE cm.`status` = 40
 ORDER BY cd.id DESC;
"""



PROOVEDORES_LIST = """
SELECT 
pr.id,
UPPER(pr.nombre) AS proveedor,
-- COUNT(cm.proveedor_id) AS total_compras,
ROUND(SUM(cm.total),2) AS total_money
FROM compra AS cm
JOIN proveedor AS pr ON pr.id = cm.proveedor_id
WHERE cm.`status` = 40
GROUP BY cm.proveedor_id
ORDER BY total_money DESC 
"""


TOTALES_PROVEEDORES = """
SELECT
    pr.id AS id_proveedor,
    UPPER(pr.nombre) AS proveedor,
    COUNT(cm.proveedor_id) AS total_compras,
    ROUND(SUM(cm.total), 2) AS sum_total_compras,
    COALESCE(credito_data.monto_credito, 0) AS monto_credito,
    -- Si no hay crédito, muestra 0
    COALESCE(abono_data.total_abono, 0) AS monto_abono,
    COALESCE(credito_data.monto_credito, 0) - COALESCE(abono_data.total_abono, 0) AS por_pagar
FROM
    compra AS cm
    JOIN proveedor AS pr ON pr.id = cm.proveedor_id
    LEFT JOIN (
        SELECT
            pr.id AS id_proveedor,
            ROUND(SUM(c.monto), 2) AS monto_credito
        FROM
            credito AS c
            INNER JOIN compra AS cm ON cm.id = c.compra_id
            INNER JOIN proveedor AS pr ON pr.id = cm.proveedor_id
        WHERE
            c.`status` != 20
        GROUP BY
            pr.id
    ) AS credito_data ON pr.id = credito_data.id_proveedor
    LEFT JOIN (
        SELECT
            cm.proveedor_id AS pr_id,
            ROUND(SUM(ca.cantidad), 2) AS total_abono
        FROM
            credito_abono AS ca
            JOIN credito AS c ON c.id = ca.credito_id
            JOIN compra AS cm ON cm.id = c.compra_id
            JOIN proveedor AS pr ON pr.id = cm.proveedor_id
        WHERE
            ca.`status` = 10
        GROUP BY
            pr.id
    ) AS abono_data ON pr.id = abono_data.pr_id
WHERE
    cm.`status` = 40
GROUP BY
    cm.proveedor_id
ORDER BY
    sum_total_compras DESC;

"""


#================================================================
#                               CREDITTOS
#================================================================
def CREDITOS_CLIENTE(cliente_id=295,days=60,date_inicio=None,date_fin=None):
  # Get today's date
    today = datetime.today()
    # Calculate the date one month ago
    one_month_ago = today - timedelta(days=days) 

    # Format the dates as strings for the SQL query
    date_ini = one_month_ago.strftime('%Y-%m-%d')
    date_fin = today.strftime('%Y-%m-%d')
    if date_inicio and date_fin:
        date_ini = date_inicio
        date_fin = date_fin
    sql = f"""
      SELECT c.id AS credito_id, 
      -- c.venta_id,
      c.cliente_id, c.monto,
      -- c.`status`, c.tipo,
      UPPER(cl.nombre) AS cliente,
      FROM_UNIXTIME(c.created_at) AS fecha
      FROM credito AS c
      JOIN  cliente AS cl ON cl.id = c.cliente_id
      WHERE c.tipo = 10 AND c.cliente_id is NOT NULL  
      AND cl.id = {cliente_id}
      AND FROM_UNIXTIME(c.created_at) BETWEEN '{date_ini}' AND '{date_fin}';
    """

    return sql





def CREDITO_ABONO_CLIENTE(cliente_id=295,days=60,date_inicio=None,date_fin=None):
    # Get today's date
    today = datetime.today()
    # Calculate the date one month ago
    one_month_ago = today - timedelta(days=days) 

    # Format the dates as strings for the SQL query
    date_ini = one_month_ago.strftime('%Y-%m-%d')
    date_fin = today.strftime('%Y-%m-%d')

    if date_inicio and date_fin:
        date_ini = date_inicio
        date_fin = date_fin
    
    query = f"""
    SELECT
        ca.id AS credito_abono_id, 
        ca.cantidad, 
        c.cliente_id,
        UPPER(cl.nombre) AS cliente,
        FROM_UNIXTIME(ca.created_at) AS fecha
    FROM credito_abono AS ca
    JOIN credito AS c ON c.id = ca.credito_id
    JOIN cliente AS cl ON cl.id = c.cliente_id
    WHERE c.tipo = 10
     AND c.cliente_id = {cliente_id}
    AND FROM_UNIXTIME(ca.created_at) BETWEEN '{date_ini}' AND '{date_fin}'; 
    """  

    return query


SQL_ALL_CLIENTS = """
SELECT 
    cl.id AS id, 
    UPPER(cl.nombre) AS name ,
    SUM(c.id) AS creditos_sum
FROM credito AS c
JOIN cliente AS cl ON cl.id = c.cliente_id
GROUP BY cl.id, cl.nombre
ORDER BY creditos_sum DESC;
"""