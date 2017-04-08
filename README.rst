
=======
cfe2erp
=======

Cargar uno o varios cfe .xml de una carpta, deserializar y almacenar en un formato estándar, de modo que su importación al ERP o el sistema de gestión de la empresa resulte significativamente más sencilla.

Sobre xml "EnvioCFE_entreEmpresas"
==================================

**Estructura simplificada**


::

    Sobre = {
                Encabezado,
                CFE_Adenda( CFE, Adenda ),
                CFE_Adenda( CFE, Adenda ),
                ...
            }

Ocurrencia de elemetos en el sobre
''''''''''''''''''''''''''''''''''
::

        Encabezado  : mínimo = 1, máximo = 1
        CFE_Adenda  : mínimo = 1, máximo = 250
        CFE         : mínimo = 1, máximo = 1
        Adenda      : mínimo = 0, máximo = 1


El script `pyecee.py` lee los sobres xml de una carpeta, los parsea uno a uno creando árboles lxml (lxml.de)
Del sobre analizado, se crearán:

- `Caratula`
- `Lista de documentos`

`Caratula` es un objeto python con un método por cada elemento de la carátula:

    >>> Caratula.RUCEmisor
    ... 160010030018

Los elementos de la `Lista de documentos` son a su vez, listas de la forma:

    ["Encabezado", lista de "CFE_Adenda"]

`Encabezado` es un objeto al estilo de `Caratula`, en tanto `CFE_Adenda` contiene un `CFE` y eventualmente su `Adenda`


Configuración
'''''''''''''
Ubicación: `libpyefuy/config.py`. Modificar a gusto y piacere.

::
    delimiter = '|'
    lineterminator = '\r\n'
    out_path = '/tmp/'
    encoding="utf-8"



Como se usa
'''''''''''

::

    Ejecutar:
        `$> python ./pyecee.py /carpeta_xmls/`


**TODO:**

- Mejorar manejo de errores
- Documentar, agregar comentarios, pepochizar


