from decimal import Decimal
from django.conf import settings
from menu.models import Producto # Importar el modelo Producto de la app 'menu'
from django.utils.translation import gettext_lazy as _


class Cart:
    def __init__(self, request):
        """
        Inicializa el carrito.
        El carrito se guarda en la sesión como un diccionario:
        {
            'product_id_1': {'quantity': Q, 'price': 'P.PP'},
            'product_id_2': {'quantity': Q, 'price': 'P.PP'},
        }
        """
        self.session = request.session
        cart = self.session.get(settings.CART_SESSION_ID)
        if not cart:
            cart = self.session[settings.CART_SESSION_ID] = {}
        self.cart = cart

    def add(self, product, quantity=1, update_quantity=False):
        """
        Añade un producto al carrito o actualiza su cantidad.
        'product' es una instancia del modelo Producto.
        """
        product_id = str(product.id)
        if not isinstance(product, Producto):
            raise TypeError(_("Se esperaba una instancia de Producto para añadir al carrito."))

        if product_id not in self.cart:
            self.cart[product_id] = {'quantity': 0, 'price': str(product.precio)}

        if update_quantity:
            self.cart[product_id]['quantity'] = int(quantity)
        else:
            self.cart[product_id]['quantity'] += int(quantity)

        if self.cart[product_id]['quantity'] <= 0:
            self.remove(product) # Eliminar si la cantidad es 0 o negativa
        else:
            self.save()

    def save(self):
        self.session.modified = True

    def remove(self, product):
        """
        Elimina un producto del carrito.
        'product' es una instancia del modelo Producto.
        """
        product_id = str(product.id)
        if product_id in self.cart:
            del self.cart[product_id]
            self.save()

    def remove_by_id(self, product_id_str):
        """
        Elimina un producto del carrito usando su ID como string.
        """
        if product_id_str in self.cart:
            del self.cart[product_id_str]
            self.save()


    def __iter__(self):
        """
        Itera sobre los artículos en el carrito y obtiene los productos de la base de datos.
        Esto es crucial para tener acceso a los objetos Producto en las plantillas y vistas.
        """
        product_ids = self.cart.keys()
        # Obtener los objetos producto de la base de datos
        productos = Producto.objects.filter(id__in=[int(pid) for pid in product_ids if pid.isdigit()])

        cart = self.cart.copy() # Trabajar con una copia para evitar modificar el original durante la iteración

        for producto_obj in productos:
            product_id_str = str(producto_obj.id)
            if product_id_str in cart: # Asegurarse que el producto de la BD todavía está en el carrito de sesión
                cart[product_id_str]['product_obj'] = producto_obj # Añadir el objeto producto al item del carrito

        # Ahora iterar sobre la copia del carrito que tiene los 'product_obj'
        for product_id_str, item_data in cart.items():
            if 'product_obj' in item_data: # Solo procesar items que tienen el objeto producto cargado
                item_data['price'] = Decimal(item_data['price']) # Convertir precio a Decimal
                item_data['total_price'] = item_data['price'] * item_data['quantity']
                # Devolver una copia del item_data para evitar modificaciones accidentales fuera del iterador
                # que afecten a la sesión directamente si 'item_data' fuera una referencia directa.
                yield item_data.copy()
            # else:
                # Opcional: manejar el caso donde un ID en self.cart no corresponde a un Producto existente.
                # Esto podría pasar si un producto se elimina de la BD mientras está en carritos de sesión.
                # self.remove_by_id(product_id_str) # Autolimpieza
                # messages.warning(request, _("Un producto en tu carrito ya no existe y ha sido eliminado."))


    def __len__(self):
        """
        Cuenta la cantidad total de artículos (sumando cantidades de cada producto) en el carrito.
        """
        return sum(item['quantity'] for item in self.cart.values())

    def get_total_price(self):
        """
        Calcula el precio total de todos los artículos en el carrito.
        """
        # Usar el iterador para asegurar que se usan los precios y cantidades correctos
        # y que los productos existen.
        # total = Decimal('0.00')
        # for item in self: # self.__iter__()
        #     total += item['price'] * item['quantity']
        # return total
        # O, si se confía en los datos de self.cart directamente (más rápido si no se necesita el objeto producto):
        return sum(Decimal(item['price']) * item['quantity'] for item in self.cart.values())


    def clear(self):
        # Elimina el carrito de la sesión
        if settings.CART_SESSION_ID in self.session:
            del self.session[settings.CART_SESSION_ID]
            self.save()

    def get_item_count(self):
        """
        Devuelve el número de tipos de productos diferentes en el carrito.
        """
        return len(self.cart)
