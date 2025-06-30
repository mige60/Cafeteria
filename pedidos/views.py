from django.shortcuts import render, redirect, get_object_or_404
from django.views.decorators.http import require_POST
from django.urls import reverse_lazy, reverse
from django.contrib import messages
from django.contrib.admin.views.decorators import staff_member_required
from django.utils.translation import gettext_lazy as _
from django.db import transaction # Para atomicidad en la creación del pedido

from menu.models import Producto
from .models import Pedido, DetallePedido
from .cart import Cart # Asegúrate que Cart está bien implementado
from .forms import PedidoCreateForm, PedidoUpdateEstadoForm
from decimal import Decimal

@require_POST
def cart_add(request, product_id):
    cart = Cart(request)
    producto = get_object_or_404(Producto, id=product_id)

    try:
        quantity = int(request.POST.get('quantity', 1))
        if quantity < 1:
            quantity = 1 # Asegurar cantidad mínima
    except ValueError:
        quantity = 1

    update = request.POST.get('update', 'false').lower() == 'true'

    if producto.disponible:
        cart.add(product=producto, quantity=quantity, update_quantity=update)
        if update:
            messages.success(request, _(f"Cantidad de '{producto.nombre}' actualizada en el carrito."))
        else:
            messages.success(request, _(f"'{producto.nombre}' añadido al carrito."))
    else:
        messages.error(request, _(f"'{producto.nombre}' no está disponible actualmente."))

    return redirect(request.POST.get('next', reverse('pedidos:cart_detail')))

@require_POST
def cart_remove(request, product_id):
    cart = Cart(request)
    producto = get_object_or_404(Producto, id=product_id)
    cart.remove(producto) # El método remove en Cart debería tomar el objeto producto o su ID
    messages.info(request, _(f"'{producto.nombre}' eliminado del carrito."))
    return redirect('pedidos:cart_detail')

def cart_detail(request):
    cart = Cart(request)
    # La clase Cart en __iter__ debería preparar los items con toda la info necesaria
    # incluyendo el objeto producto y el subtotal por ítem.
    # Si no, tendríamos que enriquecerlo aquí.
    # Ejemplo de enriquecimiento si Cart.__iter__ solo da IDs:
    # items_enriquecidos = []
    # for item_id_str, item_data in cart.cart.items():
    #     try:
    #         producto = Producto.objects.get(id=int(item_id_str))
    #         items_enriquecidos.append({
    #             'product_obj': producto,
    #             'quantity': item_data['quantity'],
    #             'price': Decimal(item_data['price']),
    #             'total_price': Decimal(item_data['price']) * item_data['quantity'],
    #             'id': producto.id # Para los botones de eliminar/actualizar
    #         })
    #     except Producto.DoesNotExist:
    #         cart.remove_by_id(item_id_str) # Si el producto ya no existe, eliminarlo del carrito
    #         messages.warning(request, _("Un producto en tu carrito ya no estaba disponible y fue eliminado."))

    # Asumimos que Cart.__iter__ ya devuelve items listos para la plantilla
    return render(request, 'pedidos/cart_detail.html', {
        'cart': cart, # cart debe ser iterable y cada item contener 'product_obj', 'quantity', 'price', 'total_price'
        'titulo_pagina': _("Tu Carrito de Compras")
    })


@transaction.atomic # Asegura que todas las operaciones de BD se completen o ninguna
def pedido_create(request):
    cart = Cart(request)
    if not cart:
        messages.warning(request, _("Tu carrito está vacío."))
        return redirect(reverse('menu:menu_publico'))

    if request.method == 'POST':
        form = PedidoCreateForm(request.POST)
        if form.is_valid():
            try:
                pedido = form.save(commit=False)
                # if request.user.is_authenticated:
                #     pedido.usuario = request.user
                # No guardamos el total en el modelo Pedido, se calcula.
                pedido.save() # Guardar Pedido para obtener ID

                productos_para_detalle = []
                for item_cart in cart: # Asumiendo que Cart.__iter__ devuelve product_obj, quantity, price
                    producto_obj = item_cart.get('product_obj') # Esta es la clave, que Cart.__iter__ lo provea

                    if not producto_obj or not isinstance(producto_obj, Producto):
                        # Esto indica un problema con la implementación de Cart.__iter__
                        # Intentar cargar el producto si tenemos un ID (como fallback MUY TEMPORAL)
                        # Esto es una señal de que Cart.py necesita ser robusto.
                        # Por ahora, si 'product_obj' no está, intentaremos obtenerlo de una forma
                        # que DEBERÍA SER PROPORCIONADA POR CART.PY
                        # Ejemplo: product_id = item_cart.get('product_id')
                        # if product_id:
                        #    producto_obj = Producto.objects.get(id=product_id)
                        # else:
                        #    raise ValueError(f"El item del carrito no tiene 'product_obj' o 'product_id': {item_cart}")
                        # Para la entrega actual, asumiré que Cart.py está modificado para proveer 'product_obj'.
                        # Si no, esta parte fallará o será insegura.
                         messages.error(request, _("Hubo un error procesando tu carrito. Falta información del producto."))
                         raise ValueError("Error en datos del carrito: falta product_obj.")


                    productos_para_detalle.append(
                        DetallePedido(
                            pedido=pedido,
                            producto=producto_obj,
                            precio_unitario=Decimal(item_cart['price']), # Precio al momento de la compra
                            cantidad=item_cart['quantity']
                        )
                    )

                if not productos_para_detalle:
                    # Esto no debería pasar si el carrito no estaba vacío.
                    messages.error(request, _("No hay productos válidos en el carrito para crear el pedido."))
                    pedido.delete() # Eliminar el pedido vacío creado
                    return redirect('pedidos:cart_detail')

                DetallePedido.objects.bulk_create(productos_para_detalle)

                cart.clear()
                messages.success(request, _(f"¡Gracias! Tu pedido #{pedido.id} ha sido recibido."))

                # Enviar email de confirmación (requiere configurar email en Django)
                # send_order_confirmation_email(pedido)

                return redirect(reverse('pedidos:order_confirmation', args=[pedido.id]))
            except ValueError as ve: # Errores específicos de datos
                 messages.error(request, _(f"Error al procesar el pedido: {ve}"))
            except Exception as e: # Otros errores inesperados
                messages.error(request, _(f"Ocurrió un error inesperado al crear tu pedido: {e}. Por favor, intenta de nuevo o contacta a soporte."))
                # Considerar si el pedido parcialmente creado debe eliminarse o marcarse como erróneo.
                # if 'pedido' in locals() and pedido.pk:
                #    pedido.estado = Pedido.ESTADO_CANCELADO # O un nuevo estado 'error'
                #    pedido.notas_adicionales_personal = f"Error en creación: {e}"
                #    pedido.save()
        else:
            messages.error(request, _("Por favor corrige los errores en el formulario."))
    else:
        form = PedidoCreateForm()

    return render(request, 'pedidos/pedido_create_form.html', {
        'cart': cart,
        'form': form,
        'titulo_pagina': _("Confirmar y Realizar Pedido")
    })

def order_confirmation(request, pedido_id):
    pedido = get_object_or_404(Pedido.objects.prefetch_related('items__producto'), id=pedido_id)
    # Lógica de permisos: ¿quién puede ver esta confirmación?
    # if pedido.usuario != request.user and not (hasattr(pedido, 'email_cliente') and pedido.email_cliente == request.session.get('pedido_email_confirmacion')) and not request.user.is_staff:
    #     raise Http404 # O redirigir a login/home con mensaje

    # Guardar algo en sesión para permitir ver la confirmación si no es usuario logueado
    # request.session['last_pedido_id'] = pedido.id (se haría en pedido_create)
    # Y aquí se comprobaría ese ID.

    return render(request, 'pedidos/order_confirmation.html', {
        'pedido': pedido,
        'titulo_pagina': _(f"Confirmación del Pedido #{pedido.id}")
    })


# --- Vistas para el Personal ---

@staff_member_required
def order_list_staff(request):
    estado_filtro = request.GET.get('estado', None)
    pedidos_qs = Pedido.objects.all().order_by('-fecha_creacion')

    if estado_filtro and estado_filtro in [choice[0] for choice in Pedido.ESTADOS_PEDIDO]:
        pedidos_qs = pedidos_qs.filter(estado=estado_filtro)

    # Ejemplo de paginación
    # from django.core.paginator import Paginator
    # paginator = Paginator(pedidos_qs, 20) # 20 pedidos por página
    # page_number = request.GET.get('page')
    # pedidos_list = paginator.get_page(page_number)

    return render(request, 'pedidos/staff/order_list_staff.html', {
        'pedidos': pedidos_qs, # o pedidos_list si se usa paginación
        'estados_pedido': Pedido.ESTADOS_PEDIDO,
        'estado_actual_filtro': estado_filtro,
        'titulo_pagina': _("Gestión de Pedidos")
    })

@staff_member_required
def order_detail_staff(request, pedido_id):
    pedido = get_object_or_404(Pedido.objects.prefetch_related('items__producto__categoria'), id=pedido_id)

    if request.method == 'POST':
        form_estado = PedidoUpdateEstadoForm(request.POST, instance=pedido)
        if form_estado.is_valid():
            form_estado.save()
            messages.success(request, _(f"El estado del pedido #{pedido.id} ha sido actualizado a '{pedido.get_estado_display()}'."))
            # Aquí se podrían disparar notificaciones (ej. email al cliente si el pedido está listo)
            # if pedido.estado == Pedido.ESTADO_LISTO_RECOGER:
            #    send_pedido_listo_email(pedido)
            return redirect('pedidos:order_detail_staff', pedido_id=pedido.id)
        else:
            messages.error(request, _("Error al actualizar el estado del pedido. Revisa el formulario."))
    else:
        form_estado = PedidoUpdateEstadoForm(instance=pedido)

    return render(request, 'pedidos/staff/order_detail_staff.html', {
        'pedido': pedido,
        'form_estado': form_estado,
        'titulo_pagina': _(f"Detalle del Pedido #{pedido.id} (Gestión)")
    })
