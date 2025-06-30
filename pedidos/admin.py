from django.contrib import admin
from .models import Pedido, DetallePedido
from django.utils.translation import gettext_lazy as _
from django.urls import reverse
from django.utils.html import format_html

class DetallePedidoInline(admin.TabularInline):
    model = DetallePedido
    # raw_id_fields = ['producto'] # Descomentar si la lista de productos es muy larga
    fields = ('producto', 'precio_unitario', 'cantidad', 'get_cost_display')
    readonly_fields = ('get_cost_display',)
    extra = 1 # Mostrar un formulario extra para añadir ítem por defecto. Cambiar a 0 si se prefiere.
    can_delete = True # Permitir eliminar ítems desde el inline

    def get_cost_display(self, instance):
        return f"${instance.get_cost()}"
    get_cost_display.short_description = _("Subtotal")

    # Opcional: para evitar que se pueda modificar el precio una vez creado el pedido
    # def get_readonly_fields(self, request, obj=None):
    #     if obj and obj.pk: # obj es la instancia de Pedido
    #         # Si el pedido ya existe (obj.pk), hacer que los campos del inline sean de solo lectura
    #         # Esto es para evitar modificar detalles de un pedido ya cerrado, por ejemplo.
    #         # Podrías añadir lógica más compleja aquí basada en el estado del pedido.
    #         # if obj.estado == Pedido.ESTADO_COMPLETADO or obj.estado == Pedido.ESTADO_CANCELADO:
    #         #    return self.readonly_fields + ('producto', 'precio_unitario', 'cantidad')
    #         return self.readonly_fields + ('precio_unitario',) # Solo el precio unitario no se cambia
    #     return self.readonly_fields


@admin.register(Pedido)
class PedidoAdmin(admin.ModelAdmin):
    list_display = (
        'id',
        'nombre_cliente',
        'telefono_cliente',
        'fecha_creacion_format',
        'estado',
        'pagado',
        'get_total_cost_display'
    )
    list_filter = ('estado', 'pagado', 'fecha_creacion')
    search_fields = ('id', 'nombre_cliente', 'email_cliente', 'telefono_cliente', 'items__producto__nombre')
    date_hierarchy = 'fecha_creacion'
    ordering = ('-fecha_creacion',)

    fieldsets = (
        (_("Información del Cliente"), {
            'fields': ('nombre_cliente', 'email_cliente', 'telefono_cliente')
        }),
        (_("Estado y Pago"), {
            'fields': ('estado', 'pagado')
        }),
        (_("Fechas Importantes"), {
            'fields': ('fecha_creacion', 'fecha_actualizacion'),
        }),
        (_("Notas"), {
            'fields': ('notas_adicionales_cliente', 'notas_adicionales_personal')
        }),
    )
    readonly_fields = ('fecha_creacion', 'fecha_actualizacion', 'get_total_cost_display') # 'get_total_cost_display' no es un campo de modelo

    inlines = [DetallePedidoInline]

    def get_total_cost_display(self, obj):
        return f"${obj.get_total_cost()}"
    get_total_cost_display.short_description = _("Total Pedido ($)")

    def fecha_creacion_format(self, obj):
        return obj.fecha_creacion.strftime("%d %b %Y, %H:%M")
    fecha_creacion_format.admin_order_field = 'fecha_creacion'
    fecha_creacion_format.short_description = _('Fecha de Creación')


# No es estrictamente necesario registrar DetallePedido por separado si se maneja bien con inlines,
# pero puede ser útil para auditoría o vistas directas.
@admin.register(DetallePedido)
class DetallePedidoAdmin(admin.ModelAdmin):
    list_display = ('id', 'pedido_info', 'producto_info', 'precio_unitario_display', 'cantidad', 'get_cost_display')
    list_filter = ('producto__categoria', 'producto__nombre')
    search_fields = ('pedido__id', 'pedido__nombre_cliente', 'producto__nombre')
    # Generalmente los detalles no se editan directamente aquí si se usan inlines en PedidoAdmin.
    # Si se permite, quitar los campos de readonly_fields.
    readonly_fields = ('pedido', 'producto') # 'precio_unitario', 'cantidad' podrían ser editables si es necesario

    def pedido_info(self, obj):
        link = reverse("admin:pedidos_pedido_change", args=[obj.pedido.id])
        return format_html('<a href="{}">{} #{} ({})</a>', link, _("Pedido"), obj.pedido.id, obj.pedido.nombre_cliente)
    pedido_info.short_description = _("Pedido")
    pedido_info.admin_order_field = 'pedido__id'

    def producto_info(self, obj):
        # Asumiendo que tienes una URL de detalle para Producto en el admin de 'menu' o una vista pública
        # Si no, simplemente mostrar el nombre.
        # link_producto = reverse("admin:menu_producto_change", args=[obj.producto.id]) # Ejemplo
        # return format_html('<a href="{}">{}</a>', link_producto, obj.producto.nombre)
        return obj.producto.nombre
    producto_info.short_description = _("Producto")
    producto_info.admin_order_field = 'producto__nombre'

    def precio_unitario_display(self,obj):
        return f"${obj.precio_unitario}"
    precio_unitario_display.short_description = _("Precio Unitario ($)")

    def get_cost_display(self, obj):
        return f"${obj.get_cost()}"
    get_cost_display.short_description = _("Subtotal ($)")

    # Para evitar que se creen Detalles de Pedido sueltos desde el admin.
    def has_add_permission(self, request):
        return False

    # Podrías permitir cambiar ciertos aspectos si es necesario, pero generalmente se hace vía el Pedido.
    # def has_change_permission(self, request, obj=None):
    #    return True

    # Permitir eliminar es importante si un ítem fue añadido por error y necesita ser removido
    # def has_delete_permission(self, request, obj=None):
    #    return True
