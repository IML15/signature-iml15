# firma-iml15

Firma animada de **IML15** para la terminal: un agujero negro en ASCII que se escribe y se anima al ejecutar tus programas.

## Instalación

```bash
pip install https://github.com/IML15/signature-iml15/archive/refs/heads/main.zip
```

No necesita tener `git` instalado (por eso funciona también en imágenes Docker como `python:3.11-slim`).
Si tienes `git`, también vale:

```bash
pip install git+https://github.com/IML15/signature-iml15.git
```

En un `requirements.txt`:

```text
signature-iml15 @ https://github.com/IML15/signature-iml15/archive/refs/heads/main.zip
```

## Uso

```python
from firma_iml15 import mostrar_firma

mostrar_firma(version="v1.0")
```

También desde la terminal:

```bash
firma-iml15
# o
signature-iml15
# o
python -m firma_iml15
```

Si el programa se lanza sin consola (por ejemplo con `pythonw`), la firma simplemente no se muestra.

## Actualizar

```bash
pip install --upgrade --force-reinstall https://github.com/IML15/signature-iml15/archive/refs/heads/main.zip
```
