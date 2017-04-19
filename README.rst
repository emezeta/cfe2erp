
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


Salida CSV
''''''''''


Para `csv` existen los tipos de registro: Cabezales y Líneas.

*Campos del Cabezal*
::

    'id_cabezal'          : Identificador de registro "C" = cabezal
    'cant_lin'            : Cantidad de líneas del docuemnto relativas a este cabezal.
    'fecha_emis'          :
    'fecha_firma'         : Fecha de firma del CFE
    'tipo_cfe'            : Número CFE '111', '101', '112', etc.      (relaciona al campo siguiente)
    'tipo_documento'      : Nombre del CFE 'eFactura', 'eTicket', etc.(relaciona al campo anterior)
    'serie'               :
    'numero'              :
    'proveedor_nombre'    :
    'proveedor_rsocial'   : Razón Social
    'proveedor_rut'       :
    'moneda'              :
    'tipo_cambio'         : (si la Moneda es 'UYU' el 'Tipo de Cambio' es 1.00)
    'monto_exp_asim'      : Monto para exportación o asimilados.
    'monto_imp_percibido' : Monto de impuestos percibidos
    'monto_no_gravado'    :
    'monto_no_facturable' :
    'neto_tminima'        : Neto tasa mínima
    'neto_tbasica'        : Neto tasa básica
    'neto_otra'           : Neto otras tasas
    'monto_iva_min'       : Monto iva mínimo
    'monto_iva_bas'       : Monto iva básico
    'monto_iva_otr'       : Monto iva otras tasas
    'monto_iva_suspenso'  : Monto iva en suspenso
    'monto_total'         :
    'monto_tot_retenido'  : Monto total retenido
    'monto_pagar'         : Monto a pagar
    'dr0_glosa'           : Nombre del ítem           [1]
    'dr0_valor'           : Valor del dto. o rec.     [1]
    'dr0_deta'            : Detalles del dto. o rec.  [1]
    'adenda'              : Adenda

[1]
*Descuentos o recagros globales.*

Este elemento puede aparecer de 0 a 5 veces. Condicional: si no está presente en el CFE no se genera.
Por cada "Descuento o recaglo global" se generarán 3 campos adicionales.
Si el CFE contiene uno de estos elementos, el cabezal tendrá 3 campos adicionales, si contiene 2, serán 6 adicionales.
En el extremo, 5 elementos "Descuento o recaglo global" en el CFE, dara lugar a un cabezal con 15 columnas adicionales.

Ejemplo:
    Cabezal de CFE con 2 elementos "Descuento o Recago Global"

    `id_cabezal; ... monto_pagar; dr0_glosa; dr0_valor; dr0_deta; dr1_glosa; dr1_valor; dr1_deta`


Se asinga el valor `None` a campos vacíos o inexistentes en el CFE analizado, excepto en "Descuentos o Recargo Global",
Los CSV generados no admiten separadores de camp adyacentes.



*Campos de líneas*
::

    'id_linea'            : Identificador de registro "L": el registro es una línea del docuemnto.
    'nrolindet'           : Secuencia numeradora de línea.
    'indfact'             : Indica en tipo de Iva u otra calidad del campo en el documento.
    'nomitem'             : Nombre
    'cantidad'            :
    'unimed'              : Unidad de medida
    'descitem'            :
    'preciounitario'      :
    'montoitem'           :
    'descuentomonto'      : Monto del descuento
    'dtoporcentaje'       : Porcentaje del descuento
    'cod1'                : Codigo del ítem (hasta 5 códigos diferentes)
    'cod2'                :
    'cod3'                :
    'cod4'                :
    'cod5'                :
    'dto1_tip'            : Tipo del descuento "$" por valor, "%" por tasa. (hasta 5 diferentes)
    'dto1_val'            : Valor del descuento  (hasta 5 diferentes)
    'dto2_tip'            :
    'dto2_val'            :
    'dto3_tip'            :
    'dto3_val'            :
    'dto4_tip'            :
    'dto4_val'            :
    'dto5_tip'            :
    'dto5_val'            :


Se asinga el valor `None` a los campos vacíos o que no existan en el CFE analizado.
Los CSV generados no admiten separadores de camp adyacentes.



Salida JSON
'''''''''''

La salida en formato `json` usa los mismos nombres que que csv pero se estructuran
formas "llave:valor" con las siguientes diferencias sobre los elementos csv:

_ No existen los campos  'id_cabezal' e 'id_linea'.

_ Los descuentos o recargos globales, elementos `dr0_xxx` en los csv, son un a lista de `drg_items` de la siguiente forma:
::

    [
        {
            "TpoDR": "%",
            "TpoMovDR": "D",
            "ValorDR": 917.5,
            "GlosaDR": "Dto.Gral. 10%",
            "IndFactDR": "Gravado a Tasa B\u00e1sica"
        },
        {
            "TpoDR": "%",
            "TpoMovDR": "D",
            "ValorDR": 0.15,
            "GlosaDR": "Redondeo",
            "IndFactDR": "Prod/Serv no facturable negativo"
        }
    ]

_ Se sustituyen los campos `dtoN_tip`, dtoN_val` y `codN` por las listas  listas `docitem` y `subdescuento`
::

    `docitem`
        [ { "TipCod": "EAN",
            "Cod": 1234567890123
        } ]


    `subdescuento`
        [ { "DescTipo": "%",
            "DescVal": 20
        } ]




Aún puede que falten algunos campos de interés... Por el momento es `a solicitud de parte interesada`.



**TODO:**

- Mejorar manejo de errores
- Documentar, agregar comentarios


