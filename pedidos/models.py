from django.db import models
from django.conf import settings
from menu.models import Producto
from django.utils.translation import gettext_lazy as _
from decimal import Decimal

class Pedido(models.Model):
    ESTADO_PENDIENTE = 'pendiente'
    ESTADO_EN_PROCESO = 'en_proceso'
    ESTADO_LISTO_RECOGER = 'listo_recoger' # Nuevo estado
    ESTADO_EN_REPARTO = 'en_reparto' # Nuevo estado
    ESTADO_COMPLETADO = 'completado'
    ESTADO_CANCELADO = 'cancelado'

    ESTADOS_PEDIDO = [
        (ESTADO_PENDIENTE, _('Pendiente')),
        (ESTADO_EN_PROCESO, _('En Proceso')),
        (ESTADO_LISTO_RECOGER, _('Listo para Recoger')),
        (ESTADO_EN_REPARTO, _('En Reparto')),
        (ESTADO_COMPLETADO, _('Completado')),
        (ESTADO_CANCELADO, _('Cancelado')),
    ]

    # Información del cliente (puede ser anónimo)
    nombre_cliente = models.CharField(max_length=100, verbose_name=_("Nombre del Cliente"))
    email_cliente = models.EmailField(verbose_name=_("Email del Cliente"), blank=True) # Email opcional
    telefono_cliente = models.CharField(max_length=20, verbose_name=_("Teléfono del Cliente")) # Teléfono obligatorio

    # Si se implementa sistema de usuarios registrados:
    # usuario = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True, related_name='pedidos', verbose_name=_("Usuario Registrado"))

    fecha_creacion = models.DateTimeField(auto_now_add=True, verbose_name=_("Fecha de Creación"))
    fecha_actualizacion = models.DateTimeField(auto_now=True, verbose_name=_("Última Actualización"))

    pagado = models.BooleanField(default=False, verbose_name=_("Pagado"))
    # stripe_id = models.CharField(max_length=250, blank=True) # Para integración con Stripe u otro PSP

    estado = models.CharField(
        max_length=20,
        choices=ESTADOS_PEDIDO,
        default=ESTADO_PENDIENTE,
        verbose_name=_("Estado del Pedido")
    )

    # El total se calculará dinámicamente o se puede guardar si hay descuentos complejos
    # total_pedido_calculado = property(lambda self: self.get_total_cost())

    notas_adicionales_cliente = models.TextField(blank=True, verbose_name=_("Notas del Cliente"))
    notas_adicionales_personal = models.TextField(blank=True, verbose_name=_("Notas Internas (Personal)"))


    class Meta:
        ordering = ['-fecha_creacion']
        verbose_name = _("Pedido")
        verbose_name_plural = _("Pedidos")
        indexes = [
            models.Index(fields=['-fecha_creacion']),
            models.Index(fields=['nombre_cliente']),
            models.Index(fields=['email_cliente']),
        ]

    def __str__(self):
        return f"{_('Pedido')} #{self.id} - {self.nombre_cliente} ({self.get_estado_display()})"

    def get_total_cost(self):
        total = sum(item.get_cost() for item in self.items.all())
        return total if total is not None else Decimal('0.00')

    # URL para ver el detalle del pedido en el admin (o una vista de gestión)
    # from django.urls import reverse
    # def get_admin_url(self):
    #     return reverse('admin:pedidos_pedido_change', args=[self.id])


class DetallePedido(models.Model):
    pedido = models.ForeignKey(Pedido, related_name='items', on_delete=models.CASCADE, verbose_name=_("Pedido"))
    producto = models.ForeignKey(Producto, related_name='items_pedido', on_delete=models.PROTECT, verbose_name=_("Producto"))
    precio_unitario = models.DecimalField(max_digits=10, decimal_places=2, verbose_name=_("Precio Unitario ($) (al momento del pedido)"))
    cantidad = models.PositiveIntegerField(default=1, verbose_name=_("Cantidad"))

    class Meta:
        verbose_name = _("Detalle de Pedido")
        verbose_name_plural = _("Detalles de Pedido")
        unique_together = ('pedido', 'producto') # No permitir el mismo producto dos veces en el mismo pedido; se actualiza cantidad.
        ordering = ['id']

    def __str__(self):
        return f"{self.cantidad} x {self.producto.nombre}"

    def get_cost(self):
        cost = self.precio_unitario * self.cantidad
        return cost if cost is not None else Decimal('0.00')
