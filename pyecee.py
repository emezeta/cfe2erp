# -*- encoding:UTF-8 -*-
#!/usr/bin/env python

import json
import subprocess
import sys
from lxml import etree, objectify
from time import strftime

import lib.EnvioCFE_entreEmpresas as ecee

#from IPython import embed

"""
    **pyecee.py EnvioCFE_entreEmpresas - prueba de concepto**

    Estructura simplificada de un sobre xml "EnvioCFE_entreEmpresas"
    ''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''
    Sobre = {
                Encabezado,
                CFE_Adenda( CFE, Adenda ),
                CFE_Adenda( CFE, Adenda ),
                ...
            }
    Ocurrencia de elemetos del sobre:
    '''''''''''''''''''''''''''''''''
        Encabezado  : mínimo = 1, máximo = 1
        CFE_Adenda  : mínimo = 1, máximo = 250
        CFE         : mínimo = 1, máximo = 1
        Adenda      : mínimo = 1, máximo = 1

    Levanta los sobres xml de una carpeta y los parsea uno a uno
    para crear árboles lxml (lxml.de)

    Por cada árbol analizado, se creará una lista de dos elementos:
        ["Encabezado", "lista de CFE_Adenda(s)"]

    Cargar estructuras simples:
    '''''''''''''''''''''''''''
    	Dos alternativas
    	1. Usa un `template` de estructura completa inicializada a None.
    	   Los los tipos de CFE descritos en EnvioCFE_entreEmpresas.xsd son
    	   seis: 'eTck', 'eFact', 'eFact_Exp', 'eRem', 'eRem_Exp' y 'eResg'

    	   Recorrer el dom cargando los elementos que corresponda.
    	   Eliminar todos los elementos 'None' del template.

    	2. Sin usar tmplt recorrer el dom, cargar `element.tag = valor`.
    	   Recomponer la estrucutra.

    	Finalmente, armar cabezal/líneas de documentos a importar.
    	Serializar y almacenar.

    TODO::
        Deserializar (emezamos por json) y almacenar
        Documentar, agregar comentarios, pepochizar
        Crear módulo(s) importable(s)

"""


def write_json(out_path, jtags, out_name="eTags"):

    if jtags:
            dt = strftime('%0d%0m%0H%M%0S')
            json_file = '%s%s%s%s' % (out_path, out_name, dt, '.json')
            print("Json          : %s" % (json_file,))

            with open(json_file, 'w') as fp:
                json.dump(jtags, fp, indent=4, sort_keys=True, separators=(',', ':'))
            res = True
    else:
        res = False
    return res



if __name__ == "__main__":
    # import ipdb; ipdb.set_trace()
    entrada = sys.argv[-1:][0]
    files = subprocess.check_output('ls -1 %s/*.xml' % (entrada,),
                                    shell=True).split()
    sobres = list()
    for _file in files:

        xml_str = ecee.parse_file(_file)

        # documentos: todos los CFE_Adenda del Sobre
        caratula, documentos = parse_str(xml_str)

        # instancia la clase Caratula
        Caratula = objectify.fromstring( etree.tostring( caratula ) )

        print("CFEs en el sobre: %s" % (Caratula.CantCFE,))
        print("CFES %s:" % (_file,))

        if not (len(documentos) == Caratula.CantCFE):
            msg = "ERROR: La cantidad de CFE <%s> en el sobre no coincide " \
                  "con la cantidad indicada en la carátula <%s>" \
                  % ( len(documentos), Caratula.CantCFE)
            print(msg)
            sys.exit()

        for i in documentos:
            tag = applib.tag_ns(i)
            if tag == 'CFE':
                if   tag == 'eTck':
                    pass
                elif tag == 'eFact':
                    eDoc = objectify.fromstring(etree.tostring(i))
                    encabezado = efact_tmpl(eDoc)['Encabezado']
                elif tag == 'eFact_Exp':
                    pass
                elif tag == 'eRem':
                    pass
                elif tag == 'eRem_Exp':
                    pass
                elif tag == 'eResg':
                    pass
                else:
                    print("Cancela: Elemento desconocido" % (tag,))
            elif tag == 'Adenda':
                pass






























































