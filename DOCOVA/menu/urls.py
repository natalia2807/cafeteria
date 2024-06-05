from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from .views import login_view, index_view, agregar_producto, obtener_bebidas, actualizar_bebida, eliminar_bebida, agregar_estudiante, confirmar_correo, register_view, pagina_estudiante, formulario_alergias, guardar_alergias, obtener_fritos, obtener_empaque, actualizar_frito, eliminar_frito, actualizar_empaque, eliminar_empaque, obtener_desayuno, actualizar_desayuno, eliminar_desayuno, obtener_postre, actualizar_postre, eliminar_postre, obtener_almuerzo, actualizar_almuerzo, eliminar_almuerzo, agregar_productoC, eliminar_productoC, restar_productoC, limpiar_carritoC, comprar, verificar_pedidos,ver_pedidos,eliminar_pedido,buscar_pedidos,reporte_ventas,buscar_ventas,obtener_productos_por_categoria,guardar_alergias

urlpatterns = [
    path('admin/', admin.site.urls),
    path('login/', login_view, name='login'),

    path('index/', index_view, name='index_view'),
    path('agregar_producto/', agregar_producto, name='agregar_producto'),
    path('obtener_bebidas/', obtener_bebidas, name='obtener_bebidas'),
    path('actualizar_bebida/<int:bebida_id>/', actualizar_bebida, name='actualizar_bebida'),
    path('eliminar_bebida/<int:bebida_id>/', eliminar_bebida, name='eliminar_bebida'),
    path('agregar_estudiante/', agregar_estudiante, name='agregar_estudiante'),
    path('confirmar_correo/<int:estudiante_id>/', confirmar_correo, name='confirmar_correo'),
    path('register/', register_view, name='register'),
    path('pagina-estudiante/', pagina_estudiante, name='pagina_estudiante'),
    path('formulario_alergias/', formulario_alergias, name='formulario_alergias'),
    path('guardar_alergias/', guardar_alergias, name='guardar_alergias'), 
    path('obtener_fritos/', obtener_fritos, name='obtener_fritos'),
    path('obtener_empaque/', obtener_empaque, name='obtener_empaque'),
    path('actualizar_frito/', actualizar_frito, name='actualizar_frito'),
    path('eliminar_frito/<int:frito_id>/', eliminar_frito, name='eliminar_frito'),
    path('actualizar_empaque/<int:empaque_id>/', actualizar_empaque, name='actualizar_empaque'),
    path('eliminar_empaque/<int:empaque_id>/', eliminar_empaque, name='eliminar_empaque'),
    path('obtener_desayuno/', obtener_desayuno, name='obtener_desayuno'),
    path('actualizar_desayuno/<int:desayuno_id>/', actualizar_desayuno, name='actualizar_desayuno'),
    path('eliminar_desayuno/<int:desayuno_id>/', eliminar_desayuno, name='eliminar_desayuno'),
    path('obtener_postre/', obtener_postre, name='obtener_postre'),
    path('actualizar_postre/<int:postre_id>/', actualizar_postre, name='actualizar_postre'),
    path('eliminar_postre/<int:postre_id>/', eliminar_postre, name='eliminar_postre'),
    path('obtener_almuerzo/', obtener_almuerzo, name='obtener_almuerzo'),
    path('actualizar_almuerzo/<int:almuerzo_id>/', actualizar_almuerzo, name='actualizar_almuerzo'),
    path('eliminar_almuerzo/<int:almuerzo_id>/', eliminar_almuerzo, name='eliminar_almuerzo'),
    path('agregar/<int:producto_id>/', agregar_productoC, name="Add"),
    path('eliminar/<int:producto_id>/', eliminar_productoC, name="Del"),
    path('restar/<int:producto_id>/', restar_productoC, name="Sub"),
    path('limpiar/', limpiar_carritoC, name="CLS"),
    path('comprar/', comprar, name='comprar'),
    path('verificar_pedidos/', verificar_pedidos, name='verificar_pedidos'),
    path('ver-pedidos/', ver_pedidos, name='ver_pedidos'),
    path('eliminar-pedido/<str:codigo_pedido>/', eliminar_pedido, name='eliminar_pedido'),
    path('buscar-pedidos/', buscar_pedidos, name='buscar_pedidos'),
    path('reporte_ventas/', reporte_ventas, name='reporte_ventas'),
    path('buscar-ventas/', buscar_ventas, name='buscar_ventas'),
    path('obtener_productos_por_categoria/', obtener_productos_por_categoria, name='obtener_productos_por_categoria'),
    path('guardar_alergias/', guardar_alergias, name='guardar_alergias'),
]


