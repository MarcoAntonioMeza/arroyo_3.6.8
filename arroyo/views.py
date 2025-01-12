import locale
from django.utils import timezone
from datetime import timedelta
from datetime import date
from django.shortcuts import render,redirect
from process_data.process import *
import datetime as dt
from dateutil.relativedelta import relativedelta
from django.contrib.auth import authenticate, login,logout
from django.contrib import messages 




def index(request):
    data = vetas_totales()
    return render(request, 'ventas/index.html',data)

def ventas_mes(request):
    year = int(request.GET.get('year',date.today().year))
    month = int(request.GET.get('month',date.today().month))
    data = ventas_mes_df(year,month)
    return render(request, 'ventas/mes.html',data)



def productos(request):
    fecha_fin = request.GET.get('fecha_fin',None)
    fecha_inicio = request.GET.get('fecha_inicio',None)
    cantidad = request.GET.get('cantidad',5)
    cantidad = int(cantidad)
     # Si ambas fechas están presentes, convertirlas a objetos datetime
    
    
    if not fecha_inicio or not fecha_fin:
        fecha_actual = datetime.now()
        fecha_inicio = (fecha_actual - timedelta(days=365)).strftime('%Y-%m-%d')
        fecha_fin = fecha_actual.strftime('%Y-%m-%d')
    
    data = venta_detalle_producto(fecha_inicio=fecha_inicio,fecha_fin=fecha_fin,cantidad=cantidad)
    
    # Convertir las fechas y formatearlas
    fecha_inicio_str = dt.datetime.strptime(fecha_inicio, '%Y-%m-%d').strftime('%d de %b de %Y')
    fecha_fin_str = dt.datetime.strptime(fecha_fin, '%Y-%m-%d').strftime('%d de %b de %Y')
    
    
    
    data['fecha_inicio'] = fecha_inicio
    data['fecha_fin'] = fecha_fin
    data['fecha_inicio_str'] = fecha_inicio_str
    data['fecha_fin_str'] = fecha_fin_str
    data['cantidad'] = cantidad
    return render(request, 'productos/index.html',data)


def productos_menos_vendidos(request):
    fecha_fin = request.GET.get('fecha_fin',None)
    fecha_inicio = request.GET.get('fecha_inicio',None)
    cantidad = request.GET.get('cantidad',5)
    cantidad = int(cantidad)
     # Si ambas fechas están presentes, convertirlas a objetos datetime
    
    
    if not fecha_inicio or not fecha_fin:
        fecha_actual = datetime.now()
        fecha_inicio = (fecha_actual - timedelta(days=365)).strftime('%Y-%m-%d')
        fecha_fin = fecha_actual.strftime('%Y-%m-%d')
    
    data = venta_detalle_producto(fecha_inicio=fecha_inicio,fecha_fin=fecha_fin,cantidad=cantidad,is_top=False)
    
    # Convertir las fechas y formatearlas
    fecha_inicio_str = dt.datetime.strptime(fecha_inicio, '%Y-%m-%d').strftime('%d de %b de %Y')
    fecha_fin_str = dt.datetime.strptime(fecha_fin, '%Y-%m-%d').strftime('%d de %b de %Y')
    
    
    
    data['fecha_inicio'] = fecha_inicio
    data['fecha_fin'] = fecha_fin
    data['fecha_inicio_str'] = fecha_inicio_str
    data['fecha_fin_str'] = fecha_fin_str
    data['cantidad'] = cantidad
    return render(request, 'productos/menos_vendidos.html',data)



def producto_compra_ventas(request):
    producto = request.GET.get('producto')
    data = None #producto_compra_ventas(producto)
    return render(request, 'productos/producto.html',data)

#================================================================
#                                   COMPRAS 
#================================================================
def compras(request):
    year = int(request.GET.get('year',date.today().year))
    month = int(request.GET.get('month',date.today().month))
    data = compras_credito_abonos(year,month)
    return render(request, 'compras/index.html',data)



def compras_proveedor(request):
    COUNT_PROV = 200
    df_pr = consulta_sql(PROOVEDORES_LIST)
    df_pr['proveedor'] = df_pr['proveedor'].str.upper().str.strip().str.replace('_', ' ')
    lista_pro = df_pr['proveedor'].unique()[:COUNT_PROV].tolist()
    select_pro = request.GET.get('proveedor',lista_pro[0])
   
    
    fecha_actual = timezone.now().date()
    fecha_inicio_default = fecha_actual - timedelta(days=30)
    
    fecha_fin = request.GET.get('fecha_fin',fecha_actual.strftime('%Y-%m-%d'))
    fecha_inicio = request.GET.get('fecha_inicio',fecha_inicio_default.strftime('%Y-%m-%d'))
    
    locale.setlocale(locale.LC_TIME, 'es_MX.UTF-8')  # En algunos entornos podría ser 'es_MX'

    # Convertir las fechas y formatearlas
    fecha_inicio_str = dt.datetime.strptime(fecha_inicio, '%Y-%m-%d').strftime('%d de %b de %Y')
    fecha_fin_str = dt.datetime.strptime(fecha_fin, '%Y-%m-%d').strftime('%d de %b de %Y')
    
    
    
    compras_pro = compras_proveedor_pro(select_pro,fecha_inicio,fecha_fin)
    
    
    
    
    data = {
        'provedores_list':{
            'lista':lista_pro,
            'select':select_pro
        },
        'compras':compras_pro,
        
        'fecha_fin': fecha_fin,
        'fecha_inicio': fecha_inicio,
        'fecha_inicio_str': fecha_inicio_str,
        'fecha_fin_str': fecha_fin_str,
    }
    #print(data)
    
    return render(request, 'compras/proveedor.html',data)




def creditos_by_cliente(request):
    # Ejecuta la consulta y convierte los resultados a un formato manejable
    DF_LIST_CLIENT = consulta_sql(SQL_ALL_CLIENTS)  # Asumiendo que esta función devuelve un DataFrame
    del DF_LIST_CLIENT['creditos_sum']  # Si no necesitas esta columna
    # Convierte el DataFrame a una lista de tuplas
    client_list = DF_LIST_CLIENT[['id', 'name']].to_records(index=False)
    client_choices = [(row.id, row.name) for row in client_list]
    
    fecha_actual = timezone.now().date()
    #fecha_inicio_default = fecha_actual - timedelta(days=2)
    fecha_inicio_default = datetime(2023, 10, 1)
    
    fecha_fin = request.GET.get('fecha_fin',fecha_actual.strftime('%Y-%m-%d'))
    fecha_inicio = request.GET.get('fecha_inicio',fecha_inicio_default.strftime('%Y-%m-%d'))
    
    locale.setlocale(locale.LC_TIME, 'es_MX.UTF-8')  # En algunos entornos podría ser 'es_MX'
    
    
    #CLIENTE SELET 
    select_client = request.GET.get('cliente',client_choices[0][0])
    select_client = int(select_client)
    #print(select_client,'cliente seleccionado')
    
    
    # Convertir las fechas y formatearlas
    fecha_inicio_str = dt.datetime.strptime(fecha_inicio, '%Y-%m-%d').strftime('%d de %b de %Y')
    fecha_fin_str = dt.datetime.strptime(fecha_fin, '%Y-%m-%d').strftime('%d de %b de %Y')
    
    info = get_creditos_abonos_by_cliente(select_client,fecha_inicio,fecha_fin)
    
    
    context = {
        'client_choices': client_choices,
        'select_client':select_client,
        'fecha_fin': fecha_fin,
        'fecha_inicio': fecha_inicio,
        'fecha_inicio_str': fecha_inicio_str,
        'fecha_fin_str': fecha_fin_str,
        'info':info
    }
    
    return render(request, 'creditos/cliente.html', context)



def login_user(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            return redirect('ventas_mes')  # Redirige a la página principal o dashboard
        else:
            messages.error(request, 'Nombre de usuario o contraseña incorrectos.')
    return render(request, 'login/index.html')

def logout_view(request):
    logout(request)  # Cerrar la sesión del usuario
    return redirect('login') 