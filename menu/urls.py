from django.urls import path
from . import views

app_name = 'menu'

urlpatterns = [
    # URLs para Productos
    path('productos/', views.ProductoListView.as_view(), name='producto_list'),
    path('productos/crear/', views.ProductoCreateView.as_view(), name='producto_create'),
    path('productos/<int:pk>/', views.ProductoDetailView.as_view(), name='producto_detail_pk'), # Por si se accede solo con PK
    path('productos/<int:pk>/<slug:slug>/', views.ProductoDetailView.as_view(), name='product_detail'), # URL semántica
    path('productos/<int:pk>/actualizar/', views.ProductoUpdateView.as_view(), name='producto_update'),
    path('productos/<int:pk>/eliminar/', views.ProductoDeleteView.as_view(), name='producto_delete'),

    # URLs para Categorías
    path('categorias/', views.CategoriaListView.as_view(), name='categoria_list'),
    path('categorias/crear/', views.CategoriaCreateView.as_view(), name='categoria_create'),
    path('categorias/<int:pk>/<slug:slug>/', views.CategoriaDetailView.as_view(), name='categoria_detail'),
    path('categorias/<int:pk>/actualizar/', views.CategoriaUpdateView.as_view(), name='categoria_update'),
    path('categorias/<int:pk>/eliminar/', views.CategoriaDeleteView.as_view(), name='categoria_delete'),

    # URL para el menú público
    path('', views.menu_publico_list, name='menu_publico'),
]
