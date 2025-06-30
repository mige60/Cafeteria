from django.contrib import admin
from .models import Categoria, Producto

@admin.register(Categoria)
class CategoriaAdmin(admin.ModelAdmin):
    list_display = ['nombre', 'slug']
    prepopulated_fields = {'slug': ('nombre',)} # Ayuda a generar el slug automáticamente en el admin
    search_fields = ['nombre']
    ordering = ['nombre']

@admin.register(Producto)
class ProductoAdmin(admin.ModelAdmin):
    list_display = ['nombre', 'categoria', 'precio', 'disponible', 'creado', 'actualizado', 'imagen']
    list_filter = ['disponible', 'categoria', 'creado', 'actualizado']
    list_editable = ['precio', 'disponible'] # Campos editables directamente en la lista
    prepopulated_fields = {'slug': ('nombre',)}
    search_fields = ['nombre', 'descripcion']
    date_hierarchy = 'creado' # Navegación jerárquica por fechas
    ordering = ['-actualizado'] # Orden por defecto

    fieldsets = (
        (None, {
            'fields': ('nombre', 'slug', 'descripcion')
        }),
        ('Detalles del Producto', {
            'fields': ('categoria', 'precio', 'imagen')
        }),
        ('Estado', {
            'fields': ('disponible',)
        }),
    )

    # Opcional: si quieres mostrar la imagen en la lista (puede ser pesado si son muchas)
    # def imagen_tag(self, obj):
    #     from django.utils.html import format_html
    #     if obj.imagen:
    #         return format_html('<img src="{}" style="max-height: 50px; max-width: 50px;" />'.format(obj.imagen.url))
    #     return "-"
    # imagen_tag.short_description = 'Imagen'
    # # Añadir 'imagen_tag' a list_display si se descomenta lo anterior

# Para probar, necesitarás crear un superusuario: python manage.py createsuperuser
