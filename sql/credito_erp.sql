SELECT
    `credito`.monto,
    `credito`.monto_pagado
FROM
    `credito`
    LEFT JOIN `venta` ON credito.venta_id = venta.id
WHERE
    (`credito`.`tipo` = 10)
    AND (
        (`venta`.`cliente_id` = 295)
        OR (`credito`.`cliente_id` = 295)
    )
    AND (
        (`credito`.`status` = 10)
        OR (`credito`.`status` = 40)
    )
    AND FROM_UNIXTIME(`credito`.created_at) BETWEEN '2023-10-01'
    AND '2025-02-17';

---------------------------
SELECT
    c.id AS credito_id,
    -- c.venta_id,
    c.cliente_id,
    c.monto,
    -- c.`status`, c.tipo,
    UPPER(cl.nombre) AS cliente,
    FROM_UNIXTIME(c.created_at) AS fecha
FROM
    credito AS c
    JOIN cliente AS cl ON cl.id = c.cliente_id
WHERE
    c.tipo = 10
    AND c.cliente_id is NOT NULL
    AND cl.id = 295
    AND FROM_UNIXTIME(c.created_at) BETWEEN '2023-10-01'
    AND '2025-02-17';