from django import forms
from .models import Producto, Categoria

class ProductoForm(forms.ModelForm):
    class Meta:
        model = Producto
        fields = ['nombre', 'categoria', 'descripcion', 'precio', 'imagen', 'disponible']
        widgets = {
            'nombre': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Nombre del producto'}),
            'categoria': forms.Select(attrs={'class': 'form-control'}),
            'descripcion': forms.Textarea(attrs={'class': 'form-control', 'rows': 3, 'placeholder': 'Descripción detallada del producto'}),
            'precio': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'Precio en USD'}),
            'imagen': forms.ClearableFileInput(attrs={'class': 'form-control-file'}),
            'disponible': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }
        labels = {
            'nombre': 'Nombre del Producto',
            'categoria': 'Categoría',
            'descripcion': 'Descripción',
            'precio': 'Precio ($)',
            'imagen': 'Imagen del Producto',
            'disponible': 'Disponible para la venta',
        }
        help_texts = {
            'imagen': 'Sube una imagen representativa del producto.',
            'disponible': 'Marca esta casilla si el producto está actualmente disponible.',
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['categoria'].queryset = Categoria.objects.all()
        self.fields['categoria'].empty_label = "Seleccione una categoría"


class CategoriaForm(forms.ModelForm):
    class Meta:
        model = Categoria
        fields = ['nombre']
        widgets = {
            'nombre': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Nombre de la categoría'}),
        }
        labels = {
            'nombre': 'Nombre de la Categoría',
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Podrías añadir validaciones personalizadas aquí si es necesario
        # Por ejemplo, asegurar que el nombre de la categoría no sea demasiado corto.
        pass
