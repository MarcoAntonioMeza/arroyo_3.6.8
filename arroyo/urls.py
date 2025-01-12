from django.urls import path
import arroyo.views as v
from django.contrib.auth.decorators import login_required


urlpatterns = [
     path('',                           login_required(v.index), name='ventas_index'),
     path('mes/',                       login_required(v.ventas_mes), name='ventas_mes'),
     path('productos/',                 login_required(v.productos), name='producto_detalle'),
     path('productos/mesnos-vendidos/', login_required(v.productos_menos_vendidos), name='producto_menos_vendidos'),
     path('productos/venta-compra',     login_required(v.producto_compra_ventas), name='producto_venta_compra'),
     
     
     path('compras/',                    login_required(v.compras), name='compras'),
     path('compras/proveedor/',        login_required(v.compras_proveedor), name='compras_proveedor'),
     path('creditos/cliente/',        login_required(v.creditos_by_cliente), name='creditos_cliente'),
     
     
     path('login/',v.login_user, name='login'),
     path('logout/', v.logout_view, name='logout'),
     
]