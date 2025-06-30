from django.db import models
from django.urls import reverse
from django.utils.text import slugify

class Categoria(models.Model):
    nombre = models.CharField(max_length=100, unique=True, verbose_name="Nombre de la categoría")
    slug = models.SlugField(max_length=100, unique=True, blank=True, help_text="Versión amigable para URL, se genera automáticamente.")

    class Meta:
        verbose_name = "Categoría"
        verbose_name_plural = "Categorías"
        ordering = ['nombre']

    def __str__(self):
        return self.nombre

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.nombre)
        super().save(*args, **kwargs)

class Producto(models.Model):
    categoria = models.ForeignKey(Categoria, related_name='productos', on_delete=models.SET_NULL, null=True, verbose_name="Categoría")
    nombre = models.CharField(max_length=200, verbose_name="Nombre del producto")
    slug = models.SlugField(max_length=200, unique=True, blank=True, help_text="Versión amigable para URL, se genera automáticamente.")
    descripcion = models.TextField(blank=True, verbose_name="Descripción")
    precio = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="Precio ($)")
    imagen = models.ImageField(upload_to='productos/%Y/%m/%d/', blank=True, null=True, verbose_name="Imagen del producto")
    disponible = models.BooleanField(default=True, verbose_name="Disponible")
    creado = models.DateTimeField(auto_now_add=True, verbose_name="Fecha de creación")
    actualizado = models.DateTimeField(auto_now=True, verbose_name="Fecha de actualización")

    class Meta:
        verbose_name = "Producto"
        verbose_name_plural = "Productos"
        ordering = ['nombre']
        indexes = [
            models.Index(fields=['id', 'slug']),
            models.Index(fields=['nombre']),
            models.Index(fields=['-creado']),
        ]

    def __str__(self):
        return self.nombre

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.nombre)
            # Asegurar unicidad del slug si se genera automáticamente
            counter = 1
            original_slug = self.slug
            # Excluir el propio objeto si se está actualizando
            queryset = Producto.objects.filter(slug=self.slug)
            if self.pk:
                queryset = queryset.exclude(pk=self.pk)

            while queryset.exists():
                self.slug = f"{original_slug}-{counter}"
                counter += 1
                queryset = Producto.objects.filter(slug=self.slug)
                if self.pk:
                    queryset = queryset.exclude(pk=self.pk)
        super().save(*args, **kwargs)

    def get_absolute_url(self):
        # Asumiendo que tendrás una vista de detalle de producto llamada 'product_detail'
        # en tus urls de la app 'menu'.
        return reverse('menu:product_detail', args=[self.id, self.slug])

    # Las funciones get_add_to_cart_url y get_remove_from_cart_url
    # se definirán más adelante cuando se implemente el carrito,
    # ya que dependen de las URLs de la app 'pedidos'.
    # Por ahora, las comentamos para evitar errores de ReverseMatch.
    # def get_add_to_cart_url(self):
    #     return reverse('pedidos:cart_add', kwargs={'product_id': self.id})

    # def get_remove_from_cart_url(self):
    #     return reverse('pedidos:cart_remove', kwargs={'product_id': self.id})
