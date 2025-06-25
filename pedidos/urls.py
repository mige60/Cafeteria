from django.urls import path
from . import views

app_name = 'pedidos'

urlpatterns = [
    # URLs del Carrito
    path('carrito/', views.cart_detail, name='cart_detail'),
    path('carrito/add/<int:product_id>/', views.cart_add, name='cart_add'),
    path('carrito/remove/<int:product_id>/', views.cart_remove, name='cart_remove'),

    # URL para crear el pedido (checkout)
    path('crear/', views.pedido_create, name='pedido_create'),
    path('confirmacion/<int:pedido_id>/', views.order_confirmation, name='order_confirmation'),

    # URLs para la gestión de pedidos por el personal
    path('staff/ordenes/', views.order_list_staff, name='order_list_staff'), # Lista de todos los pedidos
    path('staff/ordenes/<int:pedido_id>/', views.order_detail_staff, name='order_detail_staff'), # Detalle y actualización de un pedido
    # La actualización de estado se maneja dentro de order_detail_staff via POST,
    # por lo que no se necesita una URL separada a menos que se quiera un endpoint específico.
    # path('staff/ordenes/<int:pedido_id>/actualizar-estado/', views.order_update_status_staff, name='order_update_status_staff'),
]
