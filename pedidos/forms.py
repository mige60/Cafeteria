from django import forms
from .models import Pedido
from django.utils.translation import gettext_lazy as _

class PedidoCreateForm(forms.ModelForm):
    class Meta:
        model = Pedido
        fields = ['nombre_cliente', 'email_cliente', 'telefono_cliente', 'notas_adicionales_cliente']
        widgets = {
            'nombre_cliente': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': _('Nombre completo')
            }),
            'email_cliente': forms.EmailInput(attrs={
                'class': 'form-control',
                'placeholder': _('correo@ejemplo.com (opcional)')
            }),
            'telefono_cliente': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': _('Tu número de teléfono para contacto')
            }),
            'notas_adicionales_cliente': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': _('¿Alguna instrucción especial para tu pedido? (Ej: sin azúcar, extra servilletas, etc.)')
            }),
        }
        labels = {
            'nombre_cliente': _('Nombre Completo'),
            'email_cliente': _('Correo Electrónico (Opcional)'),
            'telefono_cliente': _('Número de Teléfono'),
            'notas_adicionales_cliente': _('Notas Adicionales para tu Pedido'),
        }
        help_texts = {
            'email_cliente': _('Te enviaremos una confirmación a este correo si lo proporcionas.'),
            'telefono_cliente': _('Necesario para contactarte sobre tu pedido si es necesario.'),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Marcar campos como no requeridos si blank=True en el modelo y no se desea que sean requeridos en el form
        self.fields['email_cliente'].required = False
        # Podrías añadir validaciones específicas aquí si es necesario
        # Ejemplo: self.fields['telefono_cliente'].validators.append(MiValidadorDeTelefono())


# Formulario para actualizar el estado de un pedido (para el personal)
class PedidoUpdateEstadoForm(forms.ModelForm):
    class Meta:
        model = Pedido
        fields = ['estado', 'pagado', 'notas_adicionales_personal']
        widgets = {
            'estado': forms.Select(attrs={'class': 'form-control'}),
            'pagado': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'notas_adicionales_personal': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': _('Notas internas sobre el procesamiento o entrega del pedido.')
            }),
        }
        labels = {
            'estado': _('Nuevo Estado del Pedido'),
            'pagado': _('¿Pedido Pagado?'),
            'notas_adicionales_personal': _('Notas Internas del Personal'),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Puedes restringir las opciones de estado si es necesario,
        # por ejemplo, no permitir volver a 'pendiente' desde 'completado'.
        # instance = kwargs.get('instance')
        # if instance and instance.estado == Pedido.ESTADO_COMPLETADO:
        #     self.fields['estado'].choices = [
        #         (Pedido.ESTADO_COMPLETADO, _('Completado')),
        #         (Pedido.ESTADO_CANCELADO, _('Cancelado')), # Solo se puede cancelar
        #     ]
        #     self.fields['estado'].widget.attrs['disabled'] = True # O deshabilitar
        pass
