from .cart import Cart

def cart_total_amount(request):
    cart = Cart(request)
    total = sum(item['price'] * item['quantity'] for item in cart)
    return {'cart_total_amount': total, 'cart_items_count': len(cart)}
