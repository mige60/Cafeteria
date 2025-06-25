from django.shortcuts import render, get_object_or_404
from django.urls import reverse_lazy
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView
from django.contrib.messages.views import SuccessMessageMixin
from django.contrib import messages
from .models import Producto, Categoria
from .forms import ProductoForm, CategoriaForm
from django.utils.translation import gettext_lazy as _ # Para traducciones

# Vistas para Productos (CRUD)

class ProductoListView(ListView):
    model = Producto
    template_name = 'menu/producto_list.html'
    context_object_name = 'productos'
    paginate_by = 10

    def get_queryset(self):
        # Muestra primero los disponibles, luego por nombre
        return Producto.objects.select_related('categoria').order_by('-disponible', 'nombre')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['titulo_pagina'] = _("Listado de Productos")
        # Si se quisiera filtrar por categoría desde la URL:
        # categoria_slug = self.kwargs.get('categoria_slug')
        # if categoria_slug:
        #     context['categoria_actual'] = get_object_or_404(Categoria, slug=categoria_slug)
        #     context['productos'] = context['productos'].filter(categoria=context['categoria_actual'])
        return context

class ProductoDetailView(DetailView):
    model = Producto
    template_name = 'menu/producto_detail.html'
    context_object_name = 'producto'
    # slug_field y slug_url_kwarg son 'slug' por defecto si el campo en el modelo es 'slug'
    # pk_url_kwarg es 'pk' por defecto

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['titulo_pagina'] = self.object.nombre
        return context

class ProductoCreateView(SuccessMessageMixin, CreateView):
    model = Producto
    form_class = ProductoForm
    template_name = 'menu/producto_form.html'
    success_url = reverse_lazy('menu:producto_list')
    success_message = _("Producto '%(nombre)s' creado exitosamente.")

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['titulo_pagina'] = _("Crear Nuevo Producto")
        context['nombre_boton'] = _("Crear Producto")
        return context

    # El mensaje de éxito ya está manejado por SuccessMessageMixin si el form es válido.

class ProductoUpdateView(SuccessMessageMixin, UpdateView):
    model = Producto
    form_class = ProductoForm
    template_name = 'menu/producto_form.html'
    success_url = reverse_lazy('menu:producto_list')
    success_message = _("Producto '%(nombre)s' actualizado exitosamente.")

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['titulo_pagina'] = _("Actualizar Producto: ") + self.object.nombre
        context['nombre_boton'] = _("Guardar Cambios")
        return context

class ProductoDeleteView(DeleteView): # SuccessMessageMixin no es tan directo para DeleteView
    model = Producto
    template_name = 'menu/producto_confirm_delete.html'
    success_url = reverse_lazy('menu:producto_list')
    context_object_name = 'producto'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['titulo_pagina'] = _("Confirmar Eliminación del Producto: ") + self.object.nombre
        return context

    def form_valid(self, form):
        # Es mejor usar form_valid para personalizar la lógica de eliminación si es necesario
        # y para añadir el mensaje de éxito de forma más controlada.
        messages.success(self.request, _(f"Producto '{self.object.nombre}' eliminado exitosamente."))
        return super().form_valid(form)


# Vistas para Categorías (CRUD)

class CategoriaListView(ListView):
    model = Categoria
    template_name = 'menu/categoria_list.html'
    context_object_name = 'categorias'
    paginate_by = 10

    def get_queryset(self):
        return Categoria.objects.all().order_by('nombre')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['titulo_pagina'] = _("Listado de Categorías")
        return context


class CategoriaDetailView(DetailView): # Para ver productos de una categoría
    model = Categoria
    template_name = 'menu/categoria_detail.html' # productos_por_categoria.html
    context_object_name = 'categoria'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # Obtener productos asociados a esta categoría
        # Asegúrate de que el related_name en el ForeignKey de Producto a Categoria sea 'productos'
        context['productos'] = Producto.objects.filter(categoria=self.object, disponible=True)
        context['titulo_pagina'] = _("Productos en la Categoría: ") + self.object.nombre
        return context


class CategoriaCreateView(SuccessMessageMixin, CreateView):
    model = Categoria
    form_class = CategoriaForm
    template_name = 'menu/categoria_form.html'
    success_url = reverse_lazy('menu:categoria_list')
    success_message = _("Categoría '%(nombre)s' creada exitosamente.")

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['titulo_pagina'] = _("Crear Nueva Categoría")
        context['nombre_boton'] = _("Crear Categoría")
        return context

class CategoriaUpdateView(SuccessMessageMixin, UpdateView):
    model = Categoria
    form_class = CategoriaForm
    template_name = 'menu/categoria_form.html'
    success_url = reverse_lazy('menu:categoria_list')
    success_message = _("Categoría '%(nombre)s' actualizada exitosamente.")

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['titulo_pagina'] = _("Actualizar Categoría: ") + self.object.nombre
        context['nombre_boton'] = _("Guardar Cambios")
        return context

class CategoriaDeleteView(DeleteView):
    model = Categoria
    template_name = 'menu/categoria_confirm_delete.html'
    success_url = reverse_lazy('menu:categoria_list')
    context_object_name = 'categoria'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['titulo_pagina'] = _("Confirmar Eliminación de Categoría: ") + self.object.nombre
        return context

    def form_valid(self, form):
        # Verificar si hay productos asociados antes de eliminar
        if self.object.productos.exists():
            messages.error(self.request, _(f"No se puede eliminar la categoría '{self.object.nombre}' porque tiene productos asociados. Por favor, reasigna o elimina esos productos primero."))
            # No se llama a super().form_valid(form) para evitar la eliminación
            # Es necesario redirigir o renderizar de nuevo el template de confirmación
            # Para simplificar, vamos a redirigir a la lista de categorías.
            # Si quisieras mostrar el error en la misma página de confirmación,
            # tendrías que sobreescribir el método post o delete.
            return render(self.request, self.template_name, self.get_context_data(form=form, error_message=True))

        messages.success(self.request, _(f"Categoría '{self.object.nombre}' eliminada exitosamente."))
        return super().form_valid(form)


# Vista para la página del menú completo (público)
def menu_publico_list(request):
    productos_list = Producto.objects.filter(disponible=True).select_related('categoria').order_by('categoria__nombre', 'nombre')
    categorias = Categoria.objects.filter(productos__disponible=True).distinct().prefetch_related(
        models.Prefetch('productos', queryset=Producto.objects.filter(disponible=True).order_by('nombre'))
    )

    context = {
        'productos_list': productos_list, # Para un listado simple si se prefiere
        'categorias_con_productos': categorias, # Para agrupar por categoría
        'titulo_pagina': _("Nuestro Menú")
    }
    return render(request, 'menu/menu_publico_list.html', context)


# Vista para la Página de Inicio
def pagina_inicio(request):
    # Obtener algunos productos destacados (ej. los 3 más recientes o aleatorios)
    # Para aleatorios: productos_destacados = Producto.objects.filter(disponible=True, imagen__isnull=False).order_by('?')[:3]
    # Para los más recientes con imagen:
    productos_destacados = Producto.objects.filter(disponible=True, imagen__isnull=False).order_by('-creado')[:3]

    # También podríamos querer mostrar algunas categorías
    categorias_principales = Categoria.objects.all()[:4] # Ejemplo: las primeras 4 categorías

    # Promociones (esto sería más complejo, quizás un modelo propio para Promocion)
    # Por ahora, un placeholder:
    promociones = [
        # {'titulo': _("Café del Día + Croissant"), 'descripcion': _("Empieza tu mañana con energía. ¡Precio especial!"), 'imagen_url': 'url_a_imagen_promo_1.jpg'},
        # {'titulo': _("Tardes Dulces"), 'descripcion': _("2x1 en nuestros postres seleccionados de 3 PM a 5 PM."), 'imagen_url': 'url_a_imagen_promo_2.jpg'}
    ]

    context = {
        'productos_destacados': productos_destacados,
        'categorias_principales': categorias_principales,
        'promociones': promociones,
        'titulo_pagina': _("Bienvenido a Cafetería Delicia")
    }
    return render(request, 'menu/pagina_inicio.html', context)
