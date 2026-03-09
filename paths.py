import os
import sys

# La función que calcula la ruta base para PyInstaller o Desarrollo
def get_base_path():
    """Retorna la ruta raíz del paquete PyInstaller o del proyecto."""
    try:
        # Modo PyInstaller
        base_path = sys._MEIPASS
    except Exception:
        # Modo de desarrollo normal
        base_path = os.path.abspath(".")
    
    return base_path

# Función universal para Assets (Imagen de Fondo)
def resource_path(relative_path):
    """Genera la ruta absoluta a un asset."""
    return os.path.join(get_base_path(), relative_path)

# Función universal para Archivos de Datos (JSON que se guardan)
def data_path(file_name):
    return os.path.join(os.path.abspath(os.path.dirname(sys.executable)), file_name)