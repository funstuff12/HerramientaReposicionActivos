from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='index'),
        
    path('maquinaria/', views.vista_maquinaria, name='maquinaria'),
    path('tesoreria/', views.vista_tesoreria, name='tesoreria'),
    
    path('crear_maquinaria/', views.vista_crear_maquinaria, name='crear_maquinaria'),
    path('maquinaria/editar/<uuid:id>/', views.editar_maquina, name='editar_maquina'),
    path('maquinaria/analisis-financiero/', views.comparar_maquina, name='analisis_financiero'),
    path('maquinaria/eliminar/<uuid:maquina_id>/', views.maquinaria_eliminar, name='maquinaria_eliminar'),
    
    path('analisis/confirmar-eliminacion/<uuid:analisis_id>/', views.confirmar_eliminacion, name='confirmar_eliminacion'),
    
    path('analisis/eliminar/<uuid:analisis_id>/', views.eliminar_analisis, name='eliminar_analisis'),
    
    path('api/maquinas/tipo/<str:tipo>/', views.api_maquinas_por_tipo, name='api_maquinas_tipo'),
    path('api/maquina/<uuid:id>/', views.api_maquina_detalle, name='api_maquina_detalle'),
    path('api/guardar-analisis/', views.guardar_analisis, name='api_guardar_analisis'),
    path('api/analisis-guardados/', views.api_analisis_guardados, name='api_analisis_guardados'),
    path('api/analisis/<uuid:analisis_id>/', views.api_analisis_detalle, name='api_analisis_detalle'),

    path('dashboard-amortizacion/', views.dashboard_amortizacion, name='dashboard_amortizacion'),
    
    path('analisis-lista/', views.analisis_lista, name='analisis_lista'),
    path('analisis-detalle/<str:analisis_id>/', views.analisis_detalle, name='analisis_detalle'),

    # URLs de Clientes
    path('clientes/', views.clientes_list, name='clientes_list'),
    path('clientes/crear/', views.clientes_crear, name='clientes_crear'),
    path('clientes/<str:cliente_id>/editar/', views.clientes_editar, name='clientes_editar'),
    path('clientes/<str:cliente_id>/eliminar/', views.clientes_eliminar, name='clientes_eliminar'),

    
    path('proveedores/<str:pk>/eliminar/', views.proveedores_eliminar, name='proveedores_eliminar'),

    
    # URLs de Proveedores
    path('proveedores/', views.proveedores_list, name='proveedores_list'),
    path('proveedores/crear/', views.proveedores_crear, name='proveedores_crear'),
    path('proveedores/editar/<str:pk>/', views.proveedores_editar, name='proveedores_editar'),

    
    # URLs de Registros
    path('registros/', views.registros_list, name='registros_list'),
    path('registros/crear/', views.registros_crear, name='registros_crear'),
    # urls.py
    path('registros/<str:id>/editar/', views.registros_editar, name='registros_editar'),

    # En urls.py
    path('registros/<str:registro_id>/eliminar/', views.registros_eliminar, name='registros_eliminar'),


    path('registros/validar-id/', views.validar_id_registro, name='validar_id_registro'),
    path('clientes/<int:cliente_id>/terminos/', views.obtener_terminos_cliente, name='obtener_terminos_cliente'),
    path('proveedores/<int:proveedor_id>/terminos/', views.obtener_terminos_proveedor, name='obtener_terminos_proveedor'),
    
    path('registros/<str:registro_id>/flujo/', views.flujo_caja_view, name='flujo_caja'),
    path('calcular-flujo/', views.calcular_flujo_caja, name='calcular_flujo'),
    path('dashboard-datos/<int:registro_id>/', views.obtener_datos_dashboard, name='dashboard_datos'),
    path('exportar-reporte/<int:registro_id>/', views.exportar_reporte_flujo, name='exportar_reporte'),
    
    path('registro/importar/', views.cargar_excel_completo, name='cargar_excel_completo'),

    # URLs de Cuentas por Cobrar y Pagar
    path('cxc/', views.cuentas_por_cobrar, name='cuentas_por_cobrar'),
    path('api/cuentas-por-cobrar/', views.cuentas_por_cobrar_api, name='api_cuentas_por_cobrar'),
    # URLs para Cuentas por Pagar (CXP)
    path('cxp/', views.cuentas_por_pagar, name='cuentas_por_pagar'),
    path('api/cuentas-por-pagar/', views.cuentas_por_pagar_api, name='api_cuentas_por_pagar'),


    
    
]