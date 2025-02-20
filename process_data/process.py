import time
import datetime
import pandas as pd

import locale
import plotly.express as px
import matplotlib.ticker as mtick
import plotly.graph_objs as go
from plotly.offline import plot
import random
from .sql import *
pd.options.display.float_format = '{:,.2f}'.format


from django.db import connections



#$COLORS_ = ['#007bff', '#17a2b8', '#28a745', '#20c997', '#00bcd4', '#1e90ff', '#00fa9a', '#2e8b57', '#66cdaa', '#00ced1']
COLORS = ['#006994', '#87CEEB', '#20c997', '#00bcd4', '#004d66', '#1e90ff', '#00fa9a', '#2e8b57', '#66cdaa', '#3cb371']
#COLORS = [
#    '#006994',  # Azul profundo (océano)
#    '#87CEEB',  # Azul cielo (frescor)
#    '#20c997',  # Verde menta (marina)
#    '#00bcd4',  # Azul celeste (agua)
#    '#004d66',  # Azul oscuro (profundidad)
#    '#1e90ff',  # Azul brillante (frescura)
#    '#00fa9a',  # Verde aqua (fresco)
#    '#2e8b57',  # Verde marino (naturaleza)
#    '#66cdaa',  # Verde azulado claro (marino)
#    '#3cb371',  # Verde pasto (natural)
#    '#ff6347',  # Tomate (rojo cálido, contrastante)
#    '#f0ad4e',  # Amarillo dorado (cálido)
#    '#d9534f',  # Rojo coral (vibrante)
#    '#5bc0de',  # Azul claro (transparente)
#    '#ffc107',  # Amarillo intenso (energético)
#    '#6c757d',  # Gris oscuro (neutral)
#    '#28a745',  # Verde hierba (natural)
#    '#f8f9fa',  # Blanco suave (resaltado claro)
#    '#343a40',  # Gris oscuro (fondo oscuro)
#    '#17a2b8',  # Azul agua marina (relajante)
#]

MESES_ES = {
    1: "Enero", 2: "Febrero", 3: "Marzo", 4: "Abril",
    5: "Mayo", 6: "Junio", 7: "Julio", 8: "Agosto",
    9: "Septiembre", 10: "Octubre", 11: "Noviembre", 12: "Diciembre"
}

DIC_MESES = [(1, 'Enero'), (2, 'Febrero'), (3, 'Marzo'), (4, 'Abril'), 
             (5, 'Mayo'), (6, 'Junio'), (7, 'Julio'), (8, 'Agosto'), 
             (9, 'Septiembre'), (10, 'Octubre'), (11, 'Noviembre'), (12, 'Diciembre')]

MESES =  [x.upper() for x in ['Enero', 'Febrero', 'Marzo', 'Abril', 'Mayo', 'Junio', 'Julio', 'Agosto', 'Septiembre', 'Octubre', 'Noviembre', 'Diciembre']]
DIAS_SEMANA = [_.upper() for _ in ['Lunes', 'Martes', 'Miércoles', 'Jueves', 'Viernes', 'Sábado', 'Domingo']]

def obtener_lista_de_anos():
    # Año actual
    año_actual = datetime.now().year
    # Generar lista de años desde 2021 hasta el año actual
    return list(range(2021, año_actual + 1))

def add_columns_date_spanish(df):
  if 'fecha' in df.columns:
    df['fecha']      = pd.to_datetime(df['fecha'])
    df['year']       = df['fecha'].dt.year
    df['month']      = df['fecha'].dt.month
    df['month_name'] = df['fecha'].apply(lambda x: MESES[x.month - 1]).astype(str)
    df['day']        = df['fecha'].dt.day
    #df['dia']        = df['fecha'].dt.day
    
    #df['day_name']   = df['fecha'].apply(lambda x: DIAS_SEMANA[x.weekday()]).astype(str)
    #df['week']       = df['fecha'].dt.isocalendar().week
    #df['hour']       = df['fecha'].dt.hour

  else:
    raise ValueError("La columna 'fecha' no existe en el DataFrame.")

  return df


"""
====================================================
          CONSULTAS SQL
=====================================================
"""
def consulta_sql(sql=VENTAS(), db_alias='erp'):
    """
    Ejecuta una consulta SQL en una base de datos específica y retorna un DataFrame.
    
    Args:
        sql (str): La consulta SQL a ejecutar.
        db_alias (str): El alias de la base de datos en el diccionario DATABASES.
    
    Returns:
        pd.DataFrame: Los resultados de la consulta en formato DataFrame.
    """
    # Usar la conexión de la base de datos especificada
    with connections[db_alias].cursor() as cursor:
        cursor.execute(sql)
        columnas = [col[0] for col in cursor.description]
        resultados = cursor.fetchall()

    # Convertir los resultados a DataFrame
    df = pd.DataFrame(resultados, columns=columnas)
    return df


"""
====================================================
            VENTAS $ POR MES/AÑO
====================================================
"""

def ventas_mes_df(anio,mes):
    # Consultar datos de ventas, créditos y abonos
    df_ventas = consulta_sql(VENTAS(año=anio, mes=mes))
    df_creditos = consulta_sql(CREDITO(año=anio, mes=mes))
    df_abonos = consulta_sql(ABONO(año=anio, mes=mes))
    COLUMNA_GROUP = 'month'
    
    # Agregar columnas de fecha en español
    df_ventas = add_columns_date_spanish(df_ventas)
    df_creditos = add_columns_date_spanish(df_creditos)
    df_abonos = add_columns_date_spanish(df_abonos)
    
    plot_mes_dia = graficar_por_anio_mes_dia(df_ventas, df_creditos, df_abonos, anio, mes)
    # Filtrar datos para el año seleccionado y agrupar por mes
    df_ventas_filtro_anio = df_ventas[df_ventas['year'] == anio]
    data_ventas_mes = df_ventas_filtro_anio.groupby(COLUMNA_GROUP)['venta_total'].sum().reset_index()
    df_creditos_filtro_anio = df_creditos[df_creditos['year'] == anio]
    data_creditos_mes = df_creditos_filtro_anio.groupby(COLUMNA_GROUP)['monto'].sum().reset_index()
    df_abonos_filtro_anio = df_abonos[df_abonos['year'] == anio]
    data_abonos_mes = df_abonos_filtro_anio.groupby(COLUMNA_GROUP)['cantidad'].sum().reset_index()
    
    # Fusionar los datos mensuales de ventas, créditos y pagos
    data_mensual = data_ventas_mes.merge(data_creditos_mes, on=COLUMNA_GROUP, how='outer') \
                                  .merge(data_abonos_mes, on=COLUMNA_GROUP, how='outer')
    
    #data_mensual = data_mensual.fillna(0,inplace=True)                              
    data_mensual.columns = ['mes', 'ventas', 'creditos', 'pagos']
    #print(data_mensual)
    data_mensual = data_mensual.fillna(0)
    data_mensual['cre_ventas'] = data_mensual['ventas'].pct_change().fillna(0) * 100
    data_mensual['cre_creditos'] = data_mensual['creditos'].pct_change().fillna(0) * 100
    data_mensual['cre_pagos'] = data_mensual['pagos'].pct_change().fillna(0) * 100
    
    data_mensual['mes'] = data_mensual['mes'].apply(lambda x: MESES[x - 1])  # Convertir número de mes a nombre
    
    
    # Crear la gráfica con barras y líneas de tendencia
    list_columns_df = ['ventas', 'creditos', 'pagos']
    lis_columns_name = ['Ventas', 'C.P', 'Pagos']
    title =""# f'Ingresos Mensuales de {anio}'
    xlabel = 'Meses'
    ylabel = 'Monto Total en Pesos'
    grafica = grafica_plotly(data_mensual,list_columns_df,lis_columns_name,'mes',title,xlabel,ylabel,prefijo_before='$',add_trendline=False)
    list_columns_df = ['cre_ventas', 'cre_creditos', 'cre_pagos']
    lis_columns_name = ['crecimirnto en Ventas', 'crecimiento en Créditos', 'crecimiento en Créditos Pagos']
    title = ""# f"CRECIMIeNTO ANUAL EN COMPRAS, CREDITOS Y ABONOS en el año {anio}"
    
    #plot_crecimiento = grafica_plotly(data_mensual,list_columns_df,lis_columns_name,'mes',title,xlabel,ylabel,prefijo_after='%')
    
    
    # Cálculo de medidas de tendencia central para cada categoría
    INGRESOS = {}
    for columna in ['ventas', 'creditos', 'pagos']:
        total = data_mensual[columna].sum()
        promedio = data_mensual[columna].mean()
        std_dev = data_mensual[columna].std()
        INGRESOS[columna] = {
            'total': f"${total:,.0f}",
            'promedio': f"${promedio:,.0f}",
            'std': f"${std_dev:,.0f}"
        }

    # Agregar el gráfico a la salida de ingresos
    INGRESOS['plot'] = grafica
    INGRESOS['plot_crecimiento'] = plot_mes_dia['plot']
    
    
    # Retornar el diccionario con los ingresos y datos adicionales
    del plot_mes_dia['plot']
    return {
        'ingresos': INGRESOS,
        'anios': obtener_lista_de_anos(),
        'meses': DIC_MESES,
        'anio_seleccionado': anio,
        'mes_seleccionado': mes,
        'sumas': plot_mes_dia,
        'mes': DIC_MESES[mes - 1][1]
    }
 
    

# Función para graficar por año, mes y día con el día de la semana
def graficar_por_anio_mes_dia(df_ventas, df_creditos, df_abonos, ANIO, MES):
    # Filtrar y agrupar los datos para ventas, créditos y abonos por día en el mes específico
    df_ventas_filtro = df_ventas[(df_ventas['year'] == ANIO) & (df_ventas['month'] == MES)]
    data_ventas = df_ventas_filtro.groupby('day')['venta_total'].sum().reset_index()

    df_creditos_filtro = df_creditos[(df_creditos['year'] == ANIO) & (df_creditos['month'] == MES)]
    data_creditos = df_creditos_filtro.groupby('day')['monto'].sum().reset_index()

    df_abonos_filtro = df_abonos[(df_abonos['year'] == ANIO) & (df_abonos['month'] == MES)]
    data_abonos = df_abonos_filtro.groupby('day')['cantidad'].sum().reset_index()

    # Fusionar los datos para ventas, créditos y pagos por día
    data_diaria = data_ventas.merge(data_creditos, on='day', how='outer') \
                             .merge(data_abonos, on='day', how='outer')

    # Renombrar columnas y reemplazar valores nulos con 0
    data_diaria.columns = ['dia', 'ventas', 'creditos', 'pagos']
    data_diaria = data_diaria.fillna(0)

    # Agregar el día de la semana en formato de texto
   
    DIAS_SEMANA = [x.upper() for x in ['Lunes', 'Martes', 'Miércoles', 'Jueves', 'Viernes', 'Sábado', 'Domingo']]

    data_diaria['dia_semana'] = pd.to_datetime({'year': ANIO, 'month': MES, 'day': data_diaria['dia']}).dt.weekday
    data_diaria['dia_semana'] = data_diaria['dia_semana'].apply(lambda x: DIAS_SEMANA[x])
    
    sum_ventas = df_ventas_filtro['venta_total'].sum()
    sum_creditos = df_creditos_filtro['monto'].sum()
    sum_abonos = df_abonos_filtro['cantidad'].sum()

    # Crear la figura en Plotly
    fig = go.Figure()

    # Agregar barras de ventas, créditos y pagos
    fig.add_trace(go.Bar(
        x=data_diaria['dia'].astype(str) ,#+ ' (' + data_diaria['dia_semana'] + ')',  # Mostrar día y día de la semana
        y=data_diaria['ventas'],
        name='Ventas',
        marker_color=COLORS[2],
        text=data_diaria['ventas'].apply(lambda x: f"${x:,.0f}"),
        textposition='auto'
    ))

    fig.add_trace(go.Bar(
        x=data_diaria['dia'].astype(str),# + ' (' + data_diaria['dia_semana'] + ')',  # Mostrar día y día de la semana
        y=data_diaria['creditos'],
        name='Créditos',
        marker_color=COLORS[5],
        text=data_diaria['creditos'].apply(lambda x: f"${x:,.0f}"),
        textposition='auto'
    ))

    fig.add_trace(go.Bar(
        x=data_diaria['dia'].astype(str),# + ' (' + data_diaria['dia_semana'] + ')',  # Mostrar día y día de la semana
        y=data_diaria['pagos'],
        name='Pagos',
        marker_color=COLORS[1],
        text=data_diaria['pagos'].apply(lambda x: f"${x:,.0f}"),
        textposition='auto'
    ))
# Configurar el layout con colores complementarios
    # Configurar el layout con un estilo mejorado para la visibilidad del texto
    fig.update_layout(
        title= "",#f'Ventas, C.P y Pagos en {MESES[MES - 1]} {ANIO} por Día'.upper(),
        xaxis_title='DÍAS',
        yaxis_title='Monto Total en Pesos'.upper(),
        barmode='group',  # Agrupar las barras
        xaxis_tickmode='linear',  # Mostrar todos los días del mes
        xaxis_tickangle=-45,  # Rotación de etiquetas en el eje x
        template='plotly',  # Tema predeterminado de Plotly
        showlegend=True,
        margin=dict(l=40, r=40, t=60, b=60),
        font=dict(color='#004d66'),  # Color de texto en azul oscuro para mejor contraste
        plot_bgcolor='#f0f8ff',  # Fondo azul suave
        paper_bgcolor='#e1f1f6',  # Fondo azul pálido
        xaxis=dict(
            tickfont=dict(color='#004d66'),  # Color de las etiquetas del eje X
        ),
        yaxis=dict(
            tickfont=dict(color='#004d66'),  # Color de las etiquetas del eje Y
        )
    )

    # Configuración de la leyenda con colores adecuados
    fig.update_layout(legend=dict(
        font=dict(color='#004d66'),  # Texto de la leyenda en azul oscuro
        orientation="h",
        yanchor="top",
        y=1.1,
        xanchor="center",
        x=0.5
    ))


    return{
        'plot': plot(fig, include_plotlyjs=True, output_type='div'),
        'sum_ventas': f"${sum_ventas:,.0f}",
        'sum_creditos': f"${sum_creditos:,.0f}",
        'sum_abonos': f"${sum_abonos:,.0f}"
    }

    # Mostrar el gráfico interactivo
    #fig.show()    
    
"""
====================================================
            VENTAS $ GENERALES
====================================================
"""



def vetas_totales():
    # Obtener datos de ventas, créditos y abonos
    df_ventas = consulta_sql()
    df_creditos = consulta_sql(CREDITO())
    df_abonos = consulta_sql(ABONO())
    
    # Agregar columnas de fecha en español
    df_ventas = add_columns_date_spanish(df_ventas)
    df_creditos = add_columns_date_spanish(df_creditos)
    df_abonos = add_columns_date_spanish(df_abonos)
    
    # Agrupar y sumar por año
    ventas = df_ventas.groupby('year')['venta_total'].sum().reset_index()
    creditos = df_creditos.groupby('year')['monto'].sum().reset_index()
    abonos = df_abonos.groupby('year')['cantidad'].sum().reset_index()
    
    # Unir los DataFrames por la columna 'year'
    detalle_anual = ventas.merge(creditos, on='year', how='outer') \
                          .merge(abonos, on='year', how='outer')
    detalle_anual.columns = ['year', 'ventas', 'creditos', 'abonos']
    detalle_anual['crecimiento_ventas'] = detalle_anual['ventas'].pct_change() * 100
    detalle_anual['crecimiento_creditos'] = detalle_anual['creditos'].pct_change() * 100
    detalle_anual['crecimiento_abonos'] = detalle_anual['abonos'].pct_change() * 100
    detalle_anual.fillna(0, inplace=True)

    # Crear la gráfica de barras y líneas de tendencia
    fig = go.Figure()
    for i, (columna, color, nombre) in enumerate(zip(['ventas', 'creditos', 'abonos'], COLORS, ['VENTAS', 'CRÉDITOS', 'PAGOS'])):
        color = COLORS[random.randint(0, len(COLORS) - 1)]
        #color = COLORS[i+2]
        # Agregar barras
        fig.add_trace(go.Bar(
            x=detalle_anual['year'].astype(str),
            y=detalle_anual[columna],
            marker_color=color,
            name=nombre,
            text=detalle_anual[columna].apply(lambda x: f"${x:,.0f}"),
            textposition='auto'
        ))
        
        # Agregar línea de tendencia automática de Plotly
        #fig.add_trace(go.Scatter(
        #    x=detalle_anual['year'],
        #    y=detalle_anual[columna],
        #    mode='lines+markers',
        #    name='Tendencia',
        #    line=dict(color='#f8f9fa', width=2),
        #    marker=dict(size=8, color='#f8f9fa')
        #))

    # Configurar el layout
    fig.update_layout(
        #title='Ventas, Créditos y Pagos'.upper(),
        xaxis_title='Años',
        yaxis_title='Monto Total en Pesos'.upper(),
        barmode='group',
        xaxis_tickangle=-45,
        template='plotly_dark',
        showlegend=True,
        margin=dict(l=40, r=40, t=60, b=60),
        font=dict(color='#f8f9fa'),
        plot_bgcolor='#343a40',
        paper_bgcolor='#343a40',
    )
    
    # Configurar la leyenda
    fig.update_layout(legend=dict(
        font=dict(color='#f8f9fa'),
        orientation="h",
        yanchor="top",
        y=1.1,
        xanchor="center",
        x=0.5
    ))
    
    # Generar el gráfico HTML
    grafica = plot(fig, include_plotlyjs=True, output_type='div')
    
    
    #====================================================
    #          CRECIMIENTO
    #====================================================
    
    fig = go.Figure()
    for i, (columna, color, nombre) in enumerate(zip(['crecimiento_ventas', 'crecimiento_creditos', 'crecimiento_abonos'], COLORS, ['CRECIMIENTO EN VENTAS', 'CRECIMIENTO EN SOLICITUD DE CRÉDITOS', 'CRECIMIENTO EN  ABONOS'])):
        color = COLORS[random.randint(0, len(COLORS) - 1)]
        #color = COLORS[i+2]
        # Agregar barras
        fig.add_trace(go.Bar(
            x=detalle_anual['year'].astype(str),
            y=detalle_anual[columna],
            marker_color=color,
            name=nombre,
            text=detalle_anual[columna].apply(lambda x: f"{x:,.0f} %"),
            textposition='auto'
        ))
        
        # Agregar línea de tendencia automática de Plotly
        #fig.add_trace(go.Scatter(
        #    x=detalle_anual['year'],
        #    y=detalle_anual[columna],
        #    mode='lines+markers',
        #    name='Tendencia',
        #    line=dict(color='#f8f9fa', width=2),
        #    marker=dict(size=8, color='#f8f9fa')
        #))

    # Configurar el layout
    fig.update_layout(
        #title='Ventas, Créditos y Pagos'.upper(),
        xaxis_title='Años',
        yaxis_title='Monto Total en Pesos'.upper(),
        barmode='group',
        xaxis_tickangle=-45,
        template='plotly_dark',
        showlegend=True,
        margin=dict(l=40, r=40, t=60, b=60),
        font=dict(color='#f8f9fa'),
        plot_bgcolor='#343a40',
        paper_bgcolor='#343a40',
    )
    
    # Configurar la leyenda
    fig.update_layout(legend=dict(
        font=dict(color='#f8f9fa'),
        orientation="h",
        yanchor="top",
        y=1.1,
        xanchor="center",
        x=0.5
    ))
    
    # Generar el gráfico HTML
    grafica_cre = plot(fig, include_plotlyjs=True, output_type='div')

    # Cálculo de medidas de tendencia central para cada categoría
    INGRESOS = {}
    for columna in ['ventas', 'creditos', 'abonos']:
        total = detalle_anual[columna].sum()
        promedio = detalle_anual[columna].mean()
        std_dev = detalle_anual[columna].std()
        INGRESOS[columna] = {
            'total': f"${total:,.0f}",
            'promedio': f"${promedio:,.0f}",
            'std': f"${std_dev:,.0f}"
        }

    # Agregar el gráfico a la salida de ingresos
    INGRESOS['plot'] = grafica
    INGRESOS['plot_cre'] = grafica_cre
    
    return {'ingresos': INGRESOS}




"""

====================================================
        VENTAS POR PRODUCTO
====================================================
"""
def venta_detalle_producto(fecha_inicio=None, fecha_fin=None, cantidad=50,is_top=True):
    TOP = cantidad
    df_vD = consulta_sql(VENTA_DETALLE(fecha_inicio, fecha_fin))
    
    df_vD['fecha'] = pd.to_datetime(df_vD['fecha'])
    df_vD['año'] = df_vD['fecha'].dt.year
    df_vD['mes'] = df_vD['fecha'].dt.month

    # Identificar los productos más vendidos
    productos_mas_vendidos = df_vD.groupby('producto')['cantidad'].sum().sort_values(ascending=False)
    if is_top:
        TOP_PRODUCTO = productos_mas_vendidos.head(TOP).index.tolist()
    else:
        TOP_PRODUCTO = productos_mas_vendidos.tail(TOP).index.tolist()
    
    
    df_top = df_vD[df_vD['producto'].isin(TOP_PRODUCTO)]
    
    # Agrupar por año, mes y producto para calcular las ventas
    ventas_por_mes_producto = df_top.groupby(['año', 'mes', 'producto'])['cantidad'].sum().unstack(fill_value=0).reset_index()
    
    # Calcular medidas de tendencia central
    tendencia_central = df_top.groupby(['año', 'mes', 'producto'])['cantidad'].agg(
        total_vendido='sum',
        promedio='mean',
        desviacion_estandar='std'
    ).reset_index()

    # Redondear los resultados a 2 decimales
    tendencia_central = tendencia_central.round(2)
    
    # Convertir el número del mes en nombre
    meses_nombres = ['Enero', 'Febrero', 'Marzo', 'Abril', 'Mayo', 'Junio', 'Julio', 
                     'Agosto', 'Septiembre', 'Octubre', 'Noviembre', 'Diciembre']
    tendencia_central['mes'] = tendencia_central['mes'].apply(lambda x: meses_nombres[x - 1])
    
    # Ordenar el DataFrame por año y mes
    ventas_por_mes_producto = ventas_por_mes_producto.sort_values(['mes'],ascending=[True])
    # Crear una nueva columna con el nombre del mes
    ventas_por_mes_producto['mes'] = ventas_por_mes_producto['mes'].apply(lambda x: meses_nombres[x - 1])

    


    PLOT = crear_grafico_barras(
        data=ventas_por_mes_producto,
        x='mes',
        y=TOP_PRODUCTO,
        nombres=TOP_PRODUCTO,
        colores=COLORS if len(TOP_PRODUCTO) <= len(COLORS) else COLORS[:len(TOP_PRODUCTO)],
        titulo="",#f'Top {TOP} Productos Más Vendidos',
        x_titulo='Mes',
        y_titulo='Cantidad de Ventas',
        es_apilado=False
    )

    # Calcular total acumulado vendido por producto
    total_acumulado = df_vD.groupby('producto')['cantidad'].sum().reset_index()
    total_acumulado.columns = ['producto', 'total_acumulado']


    PLOT_PIE = crear_grafico_pie(
        labels=TOP_PRODUCTO,
        values=productos_mas_vendidos[TOP_PRODUCTO],
        colores=COLORS if len(TOP_PRODUCTO) <= len(COLORS) else COLORS[:len(TOP_PRODUCTO)],
        titulo=""#'Distribución de Ventas de los Productos Más Vendidos'
    )
    # Preparar los datos para el contexto, organizando por producto
    productos_data = {
        producto: tendencia_central[tendencia_central['producto'] == producto].to_dict('records')
        for producto in TOP_PRODUCTO
    }

    # Calcular el total vendido por producto y año
    total_vendido_por_año = df_top.groupby(['producto', 'año'])['cantidad'].sum().reset_index()

    # Calcular el total vendido general y el promedio total vendido por producto
    productos_estadisticas = total_vendido_por_año.groupby('producto')['cantidad'].agg(
        total_vendido='sum',         # Total vendido
        promedio='mean',             # Promedio total vendido
        desviacion_estandar='std'    # Desviación estándar
    ).reset_index()

    # Redondear resultados
    productos_estadisticas = productos_estadisticas.round(2)

    # Ordenar por total vendido
    productos_estadisticas = productos_estadisticas.sort_values(by='total_vendido', ascending=False)
    
    

    # Formatear números
    for col in ['total_vendido', 'promedio', 'desviacion_estandar']:
        productos_estadisticas[col] = productos_estadisticas[col].fillna(0)
        
        productos_estadisticas[col] = productos_estadisticas[col].apply(lambda x: f"{x:,.2f}")

  
    
    # Crear la tabla con la cantidad de productos vendidos por año de cada uno de los top productos
    cantidad_vendida_por_año = total_vendido_por_año.pivot(index='año', columns='producto', values='cantidad').fillna(0)

    # Redondear resultados
    cantidad_vendida_por_año = cantidad_vendida_por_año.round(2)

    # Convertir a DataFrame con un índice reset para que 'año' sea una columna
    cantidad_vendida_por_año.reset_index(inplace=True)

    # Mostrar la tabla de cantidad vendida por año en la consola para verificar
    #print(cantidad_vendida_por_año)

   
    
    
    # Preparar los datos para el contexto
    data = {
        'plot': PLOT,
        'top_productos': TOP_PRODUCTO,
        'plot_pie': PLOT_PIE,
        
        
        'productos_data': productos_data,
        'productos_estadisticas': productos_estadisticas.to_dict('records'),
        'cantidad_vendida_por_año': cantidad_vendida_por_año.to_dict('records')  # Agregar aquí la nueva tabla
    }

    return data

"""
====================================================
               COMPRAS
====================================================
"""

def compras_credito_abonos(anio,mes):
    df_compras   = consulta_sql(COMPRAS_PROVEDOR_C(anio,mes,dia_ini=1,dia_fin=31,año_fin=anio,mes_fin=mes))
    df_compras   = add_columns_date_spanish(df_compras)
    creditos     = consulta_sql(CREDITO_PROVEDOR(anio,mes,dia_ini=1,dia_fin=31,año_fin=anio,mes_fin=mes))
    creditos     = add_columns_date_spanish(creditos)
    abonos       = consulta_sql(ABONO_PROVEDOR(anio,mes,dia_ini=1,dia_fin=31,año_fin=anio,mes_fin=mes))
    abonos       = add_columns_date_spanish(abonos)
    
    
    #====================================================
    #                diario 
    #====================================================
    compras_day = df_compras[(df_compras['year'] == anio ) & (df_compras['month'] == mes)]
    compras_day_filtro = compras_day.groupby('day')['total_compra'].sum().reset_index()
    creditos_day = creditos[(creditos['year'] == anio )  & (creditos['month'] == mes)]
    creditos_day_filtro = creditos_day.groupby('day')['monto_credito'].sum().reset_index()
    abonos_day = abonos[(abonos['year'] == anio) & (abonos['month'] == mes)]
    abonos_day_filtro = abonos_day.groupby('day')['cantidad'].sum().reset_index()
    merge_day = compras_day_filtro.merge(creditos_day_filtro, on='day', how='outer') \
                                    .merge(abonos_day_filtro, on='day', how='outer')
    #print(compras_day.head(5))

    merge_day.columns = ['dia', 'compras', 'creditos', 'abonos']
    merge_day.fillna(0)    
    
    merge_day['dia_semana'] = pd.to_datetime({'year': anio, 'month': mes, 'day': merge_day['dia']}).dt.weekday
    merge_day['dia_semana'] = merge_day['dia_semana'].apply(lambda x: DIAS_SEMANA[x])
    sum_compras = compras_day['total_compra'].sum()
    sum_creditos = creditos_day['monto_credito'].sum()
    sum_abonos = abonos_day['cantidad'].sum()
    
     # Crear la figura en Plotly
    fig = go.Figure()

    # Agregar barras de ventas, créditos y pagos
    fig.add_trace(go.Bar(
        x=merge_day['dia'].astype(str),# + ' (' + merge_day['dia_semana'] + ')',  # Mostrar día y día de la semana
        y=merge_day['compras'],
        name='COMPRAS',
        marker_color=COLORS[0],
        text=merge_day['compras'].apply(lambda x: f"${x:,.0f}"),
        textposition='auto'
    ))

    fig.add_trace(go.Bar(
        x=merge_day['dia'].astype(str),# + ' (' + merge_day['dia_semana'] + ')',  # Mostrar día y día de la semana
        y=merge_day['creditos'],
        name='C.P',
        marker_color=COLORS[1],
        text=merge_day['creditos'].apply(lambda x: f"${x:,.0f}"),
        textposition='auto'
    ))

    fig.add_trace(go.Bar(
        x=merge_day['dia'].astype(str),# + ' (' + merge_day['dia_semana'] + ')',  # Mostrar día y día de la semana
        y=merge_day['abonos'],
        name='abonos',
        marker_color=COLORS[2],
        text=merge_day['abonos'].apply(lambda x: f"${x:,.0f}"),
        textposition='auto'
    ))

    # Configurar el layout
    fig.update_layout(
        title= "",#f'Ventas, C.P y ABONOS en {MESES[mes - 1]} {anio} por Día'.upper(),
        xaxis_title='DÍAS',
        yaxis_title='Monto Total en Pesos'.upper(),
        barmode='group',  # Agrupar las barras
        xaxis_tickmode='linear',  # Mostrar todos los días del mes
        xaxis_tickangle=-45,  # Rotación de etiquetas en el eje x
        template='plotly',
        showlegend=True,
        margin=dict(l=40, r=40, t=60, b=60),
        font=dict(color='#004d66'),  # Color de texto en azul oscuro para mejor contraste
        plot_bgcolor='#f0f8ff',  # Fondo azul suave
        paper_bgcolor='#e1f1f6',  # Fondo azul pálido
        xaxis=dict(
            tickfont=dict(color='#004d66'),  # Color de las etiquetas del eje X
        ),
        yaxis=dict(
            tickfont=dict(color='#004d66'),  # Color de las etiquetas del eje Y
        )
    )
    fig.update_layout(legend=dict(
        font=dict(color='#004d66'),
        orientation="h",
        yanchor="top",
        y=1.1,
        xanchor="center",
        x=0.5
    ))
    grafica_diario = plot(fig, include_plotlyjs=True, output_type='div')
    
    
    
    #====================================================
    #                      MENSUAL 
    #====================================================
    total_compras = df_compras.groupby('year')['total_compra'].sum().reset_index()
    total_creditos = creditos.groupby('year')['monto_credito'].sum().reset_index()
    total_abonos   = abonos.groupby('year')['cantidad'].sum().reset_index()
    
    # Unir los DataFrames por la columna 'year'
    detalle_anual = total_compras.merge(total_creditos, on='year', how='outer') \
                             .merge(total_abonos, on='year', how='outer')
              
    detalle_anual.columns = ['year', 'compras', 'creditos', 'abonos']
    #detalle_anual['crecimiento_compras'] = detalle_anual['compras'].pct_change() * 100
    #detalle_anual['crecimiento_creditos'] = detalle_anual['creditos'].pct_change() * 100
    #detalle_anual['crecimiento_abonos'] = detalle_anual['abonos'].pct_change() * 100
    detalle_anual.fillna(0, inplace=True)
    detalle_anual['year'] = detalle_anual['year'].astype(str)
    
    
    
    
    
    #====================================================
    #               TOTALES
    #====================================================
    # Crear la gráfica de barras y líneas de tendencia
    list_columns_df = ['compras', 'creditos', 'abonos']
    lis_columns_name = ['COMPRAS', 'C.P', 'PAGOS']
    title =""# f'Ingresos Mensuales de {anio}'
    xlabel = 'Años'
    ylabel = 'Monto Total en Pesos'
    grafica = grafica_plotly(detalle_anual,list_columns_df,lis_columns_name,'year',title,xlabel,ylabel,prefijo_before='$')
    
    
    ##/////////////////////CRECIMIRNTOS/////////////////////
    #list_columns_df = ['crecimiento_compras', 'crecimiento_creditos', 'crecimiento_abonos']
    #lis_columns_name = ['CRECIMIENTO EN COMPRAS', 'CRECIMIENTO ENCRÉDITOS', 'CRECIMIENTO EN PAGOS']
    #grafica_cre = grafica_plotly(detalle_anual,list_columns_df,lis_columns_name,'year',title,xlabel,ylabel,prefijo_after="%")
    
   
    #====================================================
    #               ANUALES
    #====================================================
    COLUMNA_GROUP = 'month'
    filtro_com = df_compras[df_compras['year'] == anio]
    compras_mes = filtro_com.groupby(COLUMNA_GROUP)['total_compra'].sum().reset_index()
    filtro_cre = creditos[creditos['year'] == anio]
    creditos_mes = filtro_cre.groupby(COLUMNA_GROUP)['monto_credito'].sum().reset_index()
    filtro_abo = abonos[abonos['year'] == anio]
    abonos_mes = filtro_abo.groupby(COLUMNA_GROUP)['cantidad'].sum().reset_index()
    
    #unir
    main_mes = compras_mes.merge(creditos_mes, on=COLUMNA_GROUP, how='outer') \
        .merge(abonos_mes, on=COLUMNA_GROUP, how='outer')
    main_mes.columns = ['mes', 'compras', 'creditos', 'abonos']
    main_mes = main_mes.fillna(0)
    main_mes['mes'] = main_mes['mes'].apply(lambda x: MESES[x - 1])  # Convertir número de mes a nombre

    list_columns_df = ['compras', 'creditos', 'abonos']
    lis_columns_name = ['COMPRAS', 'C.P', 'PAGOS']
    title =""# f'Ingresos Mensuales de {anio}'
    xlabel = 'MESES'
    # Generar el gráfico HTML
    grafica_mes = grafica_plotly(main_mes,list_columns_df,lis_columns_name,'mes',title,xlabel,ylabel,prefijo_before='$')
    
    
    
    INGRESOS = {'anios': obtener_lista_de_anos(),
        'anio_seleccionado': anio,
         'plot_diario': grafica_diario,
        'sum_compras': f"${sum_compras:,.0f}",
        'sum_creditos': f"${sum_creditos:,.0f}",
        'sum_abonos': f"${sum_abonos:,.0f}",
        'meses': DIC_MESES,
        'mes_seleccionado': mes,
        }
    INGRESOS['plot_total'] = grafica
    INGRESOS['plot_mes'] = grafica_mes
    #INGRESOS['plot_total_cre'] = grafica_cre
    
    
    
    return INGRESOS
    
    


def compras_proveedor_pro(proveedor_name,date_ini,date_fin):
    
    
    df_cp = consulta_sql(COMPRAS_PROVEDOR)
     # Convertir las fechas a objetos datetime para obtener el año, mes y día
    date_ini = datetime.strptime(date_ini, '%Y-%m-%d')  # Asumiendo el formato 'YYYY-MM-DD'
    date_fin = datetime.strptime(date_fin, '%Y-%m-%d')  # Asumiendo el formato 'YYYY-MM-DD'
    
    # Obtener el año, mes y día de las fechas de inicio y fin
    año_ini = date_ini.year
    mes_ini = date_ini.month
    dia_ini = date_ini.day
    
    año_fin = date_fin.year
    mes_fin = date_fin.month
    dia_fin = date_fin.day
    
    # Pasar las fechas a las funciones correspondientes
    dc_ab = consulta_sql(ABONO_PROVEDOR(año_ini, mes_ini, dia_ini, año_fin, mes_fin, dia_fin))
    dc_cr = consulta_sql(CREDITO_PROVEDOR(año_ini, mes_ini, dia_ini, año_fin, mes_fin, dia_fin))
    dc_cpr  = consulta_sql(COMPRAS_PROVEDOR_C(año_ini, mes_ini, dia_ini, año_fin, mes_fin, dia_fin))
    
    
    
    dc_ab['proveedor']  = dc_ab['proveedor'].str.upper().str.strip().str.replace('_', ' ')
    dc_cr['proveedor']  = dc_cr['proveedor'].str.upper().str.strip().str.replace('_', ' ')
    dc_cpr['proveedor'] = dc_cpr['proveedor'].str.upper().str.strip().str.replace('_', ' ')
    
    dc_ab['fecha'] = pd.to_datetime(dc_ab['fecha'])
    dc_cr['fecha'] = pd.to_datetime(dc_cr['fecha'])
    dc_cpr['fecha'] = pd.to_datetime(dc_cpr['fecha'])
    #print(dc_ab.head(5))
    
    try:
        #FILTROS
        #ABONOS
        abonos_gen_fil = dc_ab[
            (dc_ab['proveedor'] == proveedor_name) 
            #&  # Filtrar por nombre del proveedor
            #(dc_ab['fecha'] >= date_ini) &          # Filtrar desde la fecha de inicio
            #(dc_ab['fecha'] <= date_fin)               # Filtrar hasta la fecha de fin
        ]
        
        #print(abonos_gen_fil.head(5))
        #creditos
        credits_gen_fil = dc_cr[
            (dc_cr['proveedor'] == proveedor_name) 
            #&  # Filtrar por nombre del proveedor
            #(dc_cr['fecha'] >= date_ini) &          # Filtrar desde la fecha de inicio
            #(dc_cr['fecha'] <= date_fin)               # Filtrar hasta la fecha de fin
        ]
        #COMPRAS 
        compra_gen_fil = dc_cpr[
            (dc_cpr['proveedor'] == proveedor_name) 
            #&  # Filtrar por nombre del proveedor
            #(dc_cpr['fecha'] >= date_ini) &          # Filtrar desde la fecha de inicio
            #(dc_cpr['fecha'] <= date_fin)               # Filtrar hasta la fecha de fin
        ]
        
    
        

       # Generar resúmenes con nombres de columnas específicos
        resumen_abono = abonos_gen_fil.groupby('proveedor')['cantidad'].sum().reset_index().rename(columns={'cantidad': 'abonos'})
        #print(resumen_abono)
        resumen_compras = compra_gen_fil.groupby('proveedor')['total_compra'].sum().reset_index().rename(columns={'total_compra': 'compras'})
        resumen_creditos = credits_gen_fil.groupby('proveedor')['monto_credito'].sum().reset_index().rename(columns={'monto_credito': 'creditos'})

        # Realizar el merge
        merge = (
            resumen_abono.merge(resumen_compras, on='proveedor', how='outer')
                         .merge(resumen_creditos, on='proveedor', how='outer')
                         .fillna(0)
        )

      

        # Verificar el resultado
        #print(merge)
        xlabel = 'indicador'
        ylabel = 'monto'
        #print(merge)
        
        plot_totales_filtro = grafica_plotly(merge,['compras','creditos','abonos'],['COMPRAS','CRÉDITOS','abonos'],'proveedor',f'Resumen de {proveedor_name}',xlabel,ylabel,prefijo_before='$',add_trendline=False)
    except IOError as e:
        plot_totales_filtro = None
    except ValueError as e:
        plot_totales_filtro = None
    except Exception as e:
        plot_totales_filtro = None
    except:
        plot_totales_filtro = None
        
    
    
    df_cp.fillna(20, inplace=True)
    df_cp['tipo_medida_product'] = df_cp['tipo_medida_product'].astype(int)
    df_cp['nombre_product'] = df_cp['nombre_product'].str.upper().str.strip().str.replace('_', ' ')
    df_cp['proveedor'] = df_cp['proveedor'].str.upper().str.strip().str.replace('_', ' ')
    # Aplicamos la concatenación condicional
    df_cp['nombre_product'] = df_cp.apply(
        lambda row: f"{row['nombre_product']} KG" if row['tipo_medida_product'] == 20 else f"{row['nombre_product']} PZS",
        axis=1
    )   
    del df_cp['tipo_medida_product']
    # Asegúrate de que la columna de fecha esté en formato datetime
    df_cp['fecha'] = pd.to_datetime(df_cp['fecha'])
    

    # Filtrar las filas que coincidan con el proveedor y el rango de fechas
    compras_filtradas = df_cp[
        (df_cp['proveedor'] == proveedor_name) &  # Filtrar por nombre del proveedor
        (df_cp['fecha'] >= date_ini) &          # Filtrar desde la fecha de inicio
        (df_cp['fecha'] <= date_fin)               # Filtrar hasta la fecha de fin
    ]
    
    resumen_productos = compras_filtradas.groupby('nombre_product').agg(
    cantidad_total=('cantidad_compra', 'sum'),
    #costo_total=('costo_compra', 'sum')
    ).sort_values(by='cantidad_total', ascending=False).reset_index()
    #resumen_productos = resumen_productos.sort_values(by='cantidad_total', ascending=False)
    
    fig = go.Figure()
    # Agregar barras para la cantidad total de productos comprados
    colores_aleatorios = random.choices(COLORS, k=resumen_productos.shape[0])
    fig.add_trace(go.Bar(
        x=resumen_productos['nombre_product'],
        y=resumen_productos['cantidad_total'],
        name='Cantidad Total comprada en kg/pzs',
        marker=dict(color=colores_aleatorios),
        text=[f'{v} kg/pzs' for v in resumen_productos['cantidad_total']],
        #marker_color= COLORS[random.randint(0, len(COLORS) - 1)],
        textposition='auto',
       
    ))

    

    # Configurar el diseño del gráfico
    fig.update_layout(
        title=f"Compras al proveedor: {proveedor_name}",
        xaxis_title="Producto",
        yaxis_title="Cantidad",
       yaxis_tickformat=",", 
        barmode='group',
        xaxis_tickangle=-45,
        template='plotly_dark',
        showlegend=True,
        margin=dict(l=40, r=40, t=60, b=60),
        font=dict(color='#004d66'),  # Color de texto en azul oscuro para mejor contraste
        plot_bgcolor='#f0f8ff',  # Fondo azul suave
        paper_bgcolor='#e1f1f6',  # Fondo azul pálido
        xaxis=dict(
            tickfont=dict(color='#004d66'),  # Color de las etiquetas del eje X
        ),
        yaxis=dict(
            tickfont=dict(color='#004d66'),  # Color de las etiquetas del eje Y
        )
    )
    # Configurar la leyenda
    fig.update_layout(legend=dict(
        font=dict(color='#004d66'),
        orientation="h",
        yanchor="top",
        y=1.1,
        xanchor="center",
        x=0.5
    ))
    plot_productos = plot(fig, include_plotlyjs=True, output_type='div')
    
    
    
    
    #=?==========================================
    #      TOTALES PROVEEDOR
    #?==========================================
    df_pr_ = consulta_sql(TOTALES_PROVEEDORES)
    df_pr_['proveedor'] = df_pr_['proveedor'].str.upper().str.strip().str.replace('_', ' ')
    filtro = df_pr_[ df_pr_['proveedor'] == proveedor_name ]
    valores = [
        filtro['sum_total_compras'].values[0],
        filtro['monto_credito'].values[0],
        filtro['monto_abono'].values[0],
        filtro['por_pagar'].values[0]
    ]
    
    categorias = ['Total en Compras', 'POR PAGAR', 'Monto en Abono', 'Por Pagar']
    fig = go.Figure()
    fig.add_trace(go.Bar(
        x=categorias,
        y=valores,
        text=[f"${v:,.2f}" for v in valores],  # Mostrar valores formateados en texto
        textposition='auto',
        marker=dict(color=COLORS),  # Colores para cada barra
        name="Indicadores"
    ))

    # Configurar el diseño del gráfico
    fig.update_layout(
        title=f"Indicadores del Proveedor: {proveedor_name}",
        xaxis_title="Indicador",
        yaxis_title="Monto (MXN)",
        yaxis_tickformat=",",  # Formato para miles
        barmode='group',
        xaxis_tickangle=-45,
        template='plotly',
        showlegend=True,
        margin=dict(l=40, r=40, t=60, b=60),
        font=dict(color='#004d66'),  # Color de texto en azul oscuro para mejor contraste
        plot_bgcolor='#f0f8ff',  # Fondo azul suave
        paper_bgcolor='#e1f1f6',  # Fondo azul pálido
        xaxis=dict(
            tickfont=dict(color='#004d66'),  # Color de las etiquetas del eje X
        ),
        yaxis=dict(
            tickfont=dict(color='#004d66'),  # Color de las etiquetas del eje Y
        )
    )
    # Configurar la leyenda
    fig.update_layout(legend=dict(
        font=dict(color='#004d66'),
        orientation="h",
        yanchor="top",
        y=1.1,
        xanchor="center",
        x=0.5
    ))
    
    
    plot_totales =  plot(fig, include_plotlyjs=True, output_type='div')

    data = {
        'totales': {
            'plot': plot_totales,
            'plot_totales': plot_totales_filtro
        },
        'productos': {
            'plot': plot_productos
        }	
    }
    
    return data




"""
====================================================
            CREDITOS Y ABONOS POR CLIENTE
====================================================
"""


def get_creditos_abonos_by_cliente(cliente_id, fecha_inicio, fecha_fin, tipo_grafica='pastel'):
    """
    Calcula los totales de créditos, abonos y monto por pagar de un cliente
    en un rango de fechas específico. Además, genera una gráfica de montos.
    
    Args:
        cliente_id (int): ID del cliente.
        fecha_inicio (str): Fecha de inicio en formato 'YYYY-MM-DD'.
        fecha_fin (str): Fecha de fin en formato 'YYYY-MM-DD'.
        tipo_grafica (str): Tipo de gráfica ('pastel', 'lineas', 'barras').
    
    Returns:
        dict: Totales de créditos, abonos, monto por pagar en formato monetario,
              y una gráfica en HTML.
    """
    try:
        ## Cargar datos
        #DF_CREDITOS = consulta_sql(CREDITOS_CLIENTE(cliente_id=cliente_id, date_inicio=fecha_inicio, date_fin=fecha_fin))
        #DF_ABONOS = consulta_sql(CREDITO_ABONO_CLIENTE(cliente_id=cliente_id, date_inicio=fecha_inicio, date_fin=fecha_fin))
        
        QUERY = CREDITOS_CLIENTE_ERP(cliente_id=cliente_id, date_inicio=fecha_inicio, date_fin=fecha_fin)
        #print(QUERY)
        DF = consulta_sql(QUERY)
        
        DF = DF.fillna(0)
        #print(DF)
        
        DF['monto'] = DF['monto'].astype(float)
        DF['monto_pagado'] = DF['monto_pagado'].astype(float)
        
        sum_creditos = DF['monto'].sum()
        sum_abonos = DF['monto_pagado'].sum()
        por_pagar = sum_creditos - sum_abonos
        
        #if DF_CREDITOS.empty and DF_ABONOS.empty:
        #    return {'creditos': "$0.00", 'abonos': "$0.00", 'por_pagar': "$0.00", 'grafica': None}
        #
        ## Procesar datos
        #DF_CREDITOS = add_columns_date_spanish(DF_CREDITOS)
        #DF_ABONOS = add_columns_date_spanish(DF_ABONOS)
        #
        #sum_creditos = DF_CREDITOS['monto'].sum()
        #sum_abonos = DF_ABONOS['cantidad'].sum()
        #por_pagar = sum_creditos - sum_abonos
        
        # Crear gráfico de pastel
        fig = go.Figure()

        # Agregar créditos como parte del pastel
        fig.add_trace(go.Pie(
            labels=["Créditos", "Abonos", "Por Pagar"],
            values=[sum_creditos, sum_abonos, por_pagar],
            name="Distribución de Montos",
            marker=dict(colors=COLORS),
            textinfo='label+percent',  # Muestra la etiqueta y porcentaje
            hole=0.3  # Hueco en el centro para un gráfico de dona (opcional)
        ))

        # Personalizar diseño
        fig.update_layout(
            title="Distribución de Créditos, Abonos y Monto por Pagar",
            template='plotly',
            margin=dict(l=40, r=40, t=60, b=60),
            font=dict(color='#004d66'),  # Color de texto en azul oscuro para mejor contraste
            plot_bgcolor='#f0f8ff',  # Fondo azul suave
            paper_bgcolor='#e1f1f6',  # Fondo azul pálido
            xaxis=dict(
                tickfont=dict(color='#004d66'),  # Color de las etiquetas del eje X
            ),
            yaxis=dict(
                tickfont=dict(color='#004d66'),  # Color de las etiquetas del eje Y
            )
        )
        fig.update_layout(legend=dict(
        font=dict(color='#004d66'),  # Texto de la leyenda en azul oscuro
       
        ))
        
        # Convertir gráfica a HTML
        grafica_html = fig.to_html(full_html=False)

        # Retornar resultados
        return {
            'creditos': f"${sum_creditos:,.2f}",
            'abonos': f"${sum_abonos:,.2f}",
            'por_pagar': f"${por_pagar:,.2f}",
            'grafica': grafica_html
        }

    except Exception as e:
        return {'error': str(e)}

"""
==========================================
        GRAFICAR
==========================================
"""

def grafica_plotly(df,list_columns_df,list_name_columns,xColumnName,title,xLabel,yLabel,add_trendline=True,prefijo_before="",prefijo_after=""):
    fig = go.Figure()
    for i, (columna, color, nombre) in enumerate(zip(list_columns_df, COLORS, list_name_columns)):
        # Agregar barras
        fig.add_trace(go.Bar(
            x=df[xColumnName],
            y=df[columna],
            marker_color=color,
            name=nombre.upper(),
                       text = df[columna].apply(
                lambda x: f"{prefijo_before}{float(x):,.0f}{prefijo_after}"
                if isinstance(x, (int, float)) or (isinstance(x, str) and x.replace(',', '').replace('.', '').isdigit())
                else f"{prefijo_before}{x}{prefijo_after}"
            ),
            textposition='auto'
        ))
        if add_trendline:
            # Agregar línea de tendencia para cada serie
            fig.add_trace(go.Scatter(
                x=df[xColumnName],
                y=df[columna],
                mode='lines+markers',
                line=dict(color=color, dash='dash', width=2),
                name=f"Tendencia {nombre.lower()}",
            ))
    # Configurar el layout de la gráfica
    fig.update_layout(
        title=title.upper(),
        xaxis_title=xLabel.upper(),
        yaxis_title=yLabel.upper(),
        barmode='group',
        xaxis_tickangle=-45,
        template='plotly',
        showlegend=True,
        margin=dict(l=40, r=40, t=60, b=60),
        font=dict(color='#004d66'),  # Color de texto en azul oscuro para mejor contraste
        plot_bgcolor='#f0f8ff',  # Fondo azul suave
        paper_bgcolor='#e1f1f6',  # Fondo azul pálido
        xaxis=dict(
            tickfont=dict(color='#004d66'),  # Color de las etiquetas del eje X
        ),
        yaxis=dict(
            tickfont=dict(color='#004d66'),  # Color de las etiquetas del eje Y
        )
    )
    
    # Configurar la leyenda
    fig.update_layout(legend=dict(
        font=dict(color='#004d66'),
        orientation="h",
        yanchor="top",
        y=1.1,
        xanchor="center",
        x=0.5
    ))
    
    return plot(fig, include_plotlyjs=True, output_type='div')



def draw_plot(x, y, title,xlabel='Año', ylabel='Cantidad',add_trendline=True,cant=3):
    title= title.upper()
    xlabel=xlabel.upper()
    ylabel=ylabel.upper()
    fig = go.Figure()
    # Colores para las barras
    if len(x) > len(COLORS):
        # Si hay más barras que colores, repetir los colores
        bar_colors = [COLORS[i % len(COLORS)] for i in range(len(x))]
    else:
        # Si hay suficientes colores, usar una muestra aleatoria
        bar_colors = random.sample(COLORS, len(x))
        
    fig.add_trace(go.Bar(
        x=x,
        y=y,
        marker_color=bar_colors,
        name=title,
        text=[f'{int(val):,}' for val in y],
        textposition='auto'
    ))
    
    if add_trendline:
        # Añadir una línea de tendencia
        fig.add_trace(go.Scatter(
            x=x,
            y=y,
            mode='lines+markers',
            name='Tendencia',
            line=dict(color='#f8f9fa', width=2),
            marker=dict(size=8, color='#f8f9fa')
        ))
        
    #Configurar el diseño de la gráfica
    fig.update_layout(
        title=title,
        xaxis_title=xlabel,
        yaxis_title=ylabel,
        template='plotly_dark',
        showlegend=True,
        margin=dict(l=40, r=40, t=40, b=40),
        font=dict(color='#f8f9fa'),
        plot_bgcolor='#343a40',
        paper_bgcolor='#343a40',
    )
    
    # Configurar el eje X
    fig.update_xaxes(
        tickvals=list(x),
        ticktext=list(map(str, x)),
        title_font=dict(color='#f8f9fa'),
        tickfont=dict(color='#f8f9fa')
    )
    
     # Configurar el eje Y
    fig.update_yaxes(
        title_font=dict(color='#f8f9fa'),
        tickfont=dict(color='#f8f9fa')
    )
    
    
    # Configurar la leyenda
    fig.update_layout(legend=dict(font=dict(color='#f8f9fa')))
    
    # Renderizar la gráfica y retornar el HTML
    return  plot(fig, include_plotlyjs=True, output_type='div')


def crear_grafico_barras(data, x, y, nombres, colores, titulo, x_titulo, y_titulo, es_apilado=False):
    """
    Crea un gráfico de barras reutilizable.
    :param data: Datos para la gráfica.
    :param x: Datos del eje X.
    :param y: Lista de nombres de las series para el eje Y.
    :param nombres: Lista de nombres de las series.
    :param colores: Lista de colores para las series.
    :param titulo: Título del gráfico.
    :param x_titulo: Título del eje X.
    :param y_titulo: Título del eje Y.
    :param es_apilado: Booleano para apilar las barras.
    """
    fig = go.Figure()
    for i, nombre in enumerate(nombres):
        fig.add_trace(go.Bar(
            x=data[x],
            y=data[nombre],
            name=nombre,
            marker_color=colores[i % len(colores)]
        ))

    fig.update_layout(
        title=titulo,
        xaxis_title=x_titulo,
        yaxis_title=y_titulo,
        
        barmode='stack' if es_apilado else 'group',
        template='plotly',
        showlegend=True,
        margin=dict(l=40, r=40, t=40, b=40),
        font=dict(color='#004d66'),  # Color de texto en azul oscuro para mejor contraste
        plot_bgcolor='#f0f8ff',  # Fondo azul suave
        paper_bgcolor='#e1f1f6',  # Fondo azul pálido
        xaxis=dict(
            tickfont=dict(color='#004d66'),  # Color de las etiquetas del eje X
        ),
        yaxis=dict(
            tickfont=dict(color='#004d66'),  # Color de las etiquetas del eje Y
        )
    )

    fig.update_xaxes(title_font=dict(color='#004d66'), tickfont=dict(color='#004d66'))
    fig.update_yaxes(title_font=dict(color='#004d66'), tickfont=dict(color='#004d66'))
    
    return plot(fig, include_plotlyjs=True, output_type='div')

def crear_grafico_pie(labels, values, colores, titulo):
    """
    Crea un gráfico de pastel reutilizable.
    :param labels: Etiquetas para las porciones del gráfico.
    :param values: Valores para cada porción.
    :param colores: Lista de colores para las porciones.
    :param titulo: Título del gráfico.
    """
    fig = go.Figure()
    fig.add_trace(go.Pie(
        labels=labels,
        values=values,
        hole=.3,
        marker=dict(colors=colores),
        textinfo='percent+label',
        insidetextorientation='radial'
    ))

    fig.update_layout(
        title=titulo,
        template='plotly',
        font=dict(color='#004d66'),  # Color de texto en azul oscuro para mejor contraste
        plot_bgcolor='#f0f8ff',  # Fondo azul suave
        paper_bgcolor='#e1f1f6',  # Fondo azul pálido
        xaxis=dict(
            tickfont=dict(color='#004d66'),  # Color de las etiquetas del eje X
        ),
        yaxis=dict(
            tickfont=dict(color='#004d66'),  # Color de las etiquetas del eje Y
        )
    )
    
    fig.update_layout(legend=dict(
        font=dict(color='#004d66'),  # Texto de la leyenda en azul oscuro
        #orientation="h",
        #yanchor="top",
        #y=1.1,
        #xanchor="center",
        #x=0.5
    ))

    return plot(fig, include_plotlyjs=True, output_type='div')

def crear_grafico_barras_acumuladas(data, x, y, color, titulo, x_titulo, y_titulo):
    """
    Crea un gráfico de barras acumuladas reutilizable.
    :param data: Datos para la gráfica.
    :param x: Datos del eje X.
    :param y: Datos del eje Y.
    :param color: Color de las barras.
    :param titulo: Título del gráfico.
    :param x_titulo: Título del eje X.
    :param y_titulo: Título del eje Y.
    """
    fig = go.Figure()
    fig.add_trace(go.Bar(
        x=data[x],
        y=data[y],
        marker_color=color
    ))

    fig.update_layout(
        title=titulo,
        xaxis_title=x_titulo,
        yaxis_title=y_titulo,
        template='plotly_dark',
        font=dict(color='#f8f9fa'),
        plot_bgcolor='#343a40',
        paper_bgcolor='#343a40'
    )
    
    return plot(fig, include_plotlyjs=True, output_type='div')
