# C:\Users\PC1\Cafeteria\cafeteria_project\context_processors.py

from django.conf import settings

def custom_settings(request):
    """
    Expone configuraciones específicas de Django a los templates.
    """
    return {
        'TIME_ZONE': settings.TIME_ZONE,
        # Puedes añadir más configuraciones de settings.py aquí si las necesitas en tus plantillas.
        # Por ejemplo: 'DEBUG': settings.DEBUG,
        # 'MEDIA_URL': settings.MEDIA_URL,
    }