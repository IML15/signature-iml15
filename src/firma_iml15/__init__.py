"""Firma animada de IML15 para la terminal."""
import sys

from . import firma as _firma

__all__ = ["mostrar_firma"]
__version__ = "1.0.1"


def mostrar_firma(version="v1.0", animar=True):
    """Muestra la firma. Si el programa no tiene consola (p. ej. pythonw), no hace nada."""
    if sys.stdout is None:
        return
    _firma.mostrar_firma(version=version, animar=animar)
