from django import template
import os
from django.conf import settings

register = template.Library()

@register.filter
def file_exists(filepath):
    """Verifica si un archivo existe en la carpeta media"""
    full_path = os.path.join(settings.MEDIA_ROOT, filepath)
    print(f"Verificando existencia del archivo: {full_path}")
    exists = os.path.exists(full_path)
    print(f"¿El archivo existe? {exists}")
    return exists 