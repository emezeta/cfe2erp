
=======
cfe2erp
=======


pyecee
''''''

Líneas para un script python que levante uno o varios cfe de una carpta, los deserialize y almacene un formato estándar de modo que su importación al ERP o el sistema de gestión de la empresa resulte una tarea significativamente más sencilla.

::

    prueba de concepto - pyecee.py
    ==================

    Estructura simplificada de un sobre xml "EnvioCFE_entreEmpresas"

    Sobre = {
                Encabezado,
                CFE_Adenda( CFE, Adenda ),
                CFE_Adenda( CFE, Adenda ),
                ...
            }

    Ocurrencia de elemetos del sobre:

        Encabezado  : mínimo = 1, máximo = 1
        CFE_Adenda  : mínimo = 1, máximo = 250
        CFE         : mínimo = 1, máximo = 1
        Adenda      : mínimo = 1, máximo = 1


    `pyecee.py` Levanta los sobres xml de una carpeta y los parsea uno a uno a árboles lxml (lxml.de)

    Por cada árbol analizado, se creará una lista de dos elementos:
        ["Encabezado", "lista de CFE_Adenda"]

    Ejecutar:
        $> python ./pyecee.py /carpeta_xmls/

    TODO::

        Cargar estructuras simples
        Serializar y almacenar
        Manejo de errores
        Documentar, agregar comentarios, pepochizar
        Crear un módulo/clase(s) importable(s)
        etc.

****



aplanador
'''''''''

Este otro pasa de un xml a un json. Y eso es todo lo que piensa hacer.

::

    Esta es la idea de Fermín o sea pasar de un ojeto en complejo a uno
    simple ... ¿? que podría ser útil para ir del xml cfe a un texto
    plano tipo csv, etc.

    *aplanador.py* - Convierte un archivo de datos xml del tipo
    "EnvioCFE_entreEmpresas" en un objeto JSON y lo guarda en un archivo.

    Recibe un nombre de archivo como parámentro de entrada.

    La `expresión regular` '^{.*}' matchea cualquier cosa que encuentre
    entre '{' y '}'. Retorna la string sin eso y se usó para stripear
    los namespaces

    Al final, este viene a ser la primera pre-release de pyefuy ;)
