SELECT
    -- COMPRA
    cm.id AS id,
    cm.lat,
    cm.lng,
    cm.total AS total_compra,
    cm.`status`,
    -- PROVVEEDOR
    pr.nombre AS proveedor,
    pr.id AS proveedor_id,
    -- FECHA 
    FROM_UNIXTIME(cm.created_at) AS fecha,
    FROM_UNIXTIME(cm.fecha_salida) AS fecha_salida
FROM
    compra AS cm
    JOIN proveedor AS pr ON pr.id = cm.proveedor_id
WHERE
    cm.`status` = 40
ORDER BY
    id DESC;

select
    `compra`.`id` AS `id`,
    `compra`.`sucursal_id` AS `sucursal_id`,
    `sucursal`.`nombre` AS `sucursal`,
    `compra`.`is_especial` AS `is_especial`,
    `compra`.`proveedor_id` AS `proveedor_id`,
    `proveedor`.`nombre` AS `proveedor`,
(
        select
            sum(`compra_detalle`.`cantidad`)
        from
            `compra_detalle`
        where
            (`compra_detalle`.`compra_id` = `compra`.`id`)
    ) AS `count_detalle`,
(
        select
            sum(`operacion_detalle`.`cantidad`)
        from
            (
                `operacion_detalle`
                join `operacion` on(
                    (
                        `operacion_detalle`.`operacion_id` = `operacion`.`id`
                    )
                )
            )
        where
            (`operacion`.`compra_id` = `compra`.`id`)
    ) AS `count_entrada_detalle`,
    `compra`.`tiempo_recorrido` AS `tiempo_recorrido`,
    `compra`.`fecha_salida` AS `fecha_salida`,
    `compra`.`total` AS `total`,
    `compra`.`status` AS `status`,
    `compra`.`created_by` AS `created_by`,
    `compra`.`created_at` AS `created_at`,
    concat_ws(' ', `created`.`nombre`, `created`.`apellidos`) AS `created_by_user`,
    `compra`.`updated_by` AS `updated_by`,
    `compra`.`updated_at` AS `updated_at`,
    concat_ws(' ', `updated`.`nombre`, `updated`.`apellidos`) AS `updated_by_user`
from
    (
        (
            (
                (
                    `compra`
                    left join `sucursal` on((`compra`.`sucursal_id` = `sucursal`.`id`))
                )
                left join `proveedor` on((`compra`.`proveedor_id` = `proveedor`.`id`))
            )
            left join `user` `created` on((`compra`.`created_by` = `created`.`id`))
        )
        left join `user` `updated` on((`compra`.`updated_by` = `updated`.`id`))
    )