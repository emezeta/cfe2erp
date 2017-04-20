# coding: utf-8
#!/usr/bin/env python3

from __future__ import print_function


import subprocess
import sys
import json
from bson import ObjectId

from libpyefuy import config, ecfeee, ecfeee_json


OUT_DIR = config.out_path
INDENT  = config.indent=4,
SORT_K  = config.sort_keys=True,
SEPS    = config.separators=(',', ':')

"""
    **pyecee.py EnvioCFE_entreEmpresas**

    Envio de CFE entre Empresas es parte del `esquema xml` usado en el sistema
    eFactura por DGI (dgi.gub.uy) para el sistema eFactura. La estructura
    completa de un Sobre XML está descrita en "EnvioCFE_entreEmpresas.xsd"

    Estructura simplificada del sobre "EnvioCFE_entreEmpresas"
    ''''''''''''''''''''''''''''''''''''''''''''''''''''''''''

    Sobre = {
                Encabezado,
                CFE_Adenda = { CFE, Adenda },
                CFE_Adenda = { CFE, Adenda },
                ...
                CFE_Adenda = { CFE, Adenda }
            }

    Ocurrencia de elemetos del sobre:
    '''''''''''''''''''''''''''''''''
        Encabezado  : mínimo = 1, máximo = 1
        CFE_Adenda  : mínimo = 1, máximo = 250
            CFE         : mínimo = 1, máximo = 1
            Adenda      : mínimo = 0, máximo = 1


    Pyecee leerá los `sobres` xml a ser ptocrsados desde de una carpeta dada.
    Cada `sobre` será un arbol lxml (lxml.de). Cada uno de los CFE contenidos en
    el sobre dará lugar a un documento (factura, nota de crédito, etc.)
    expresado en un formato estandar (csv, json, xml, ...) que permita ser
    importado a diversas aplicaciones.

    A partir de las listas predefinidas de atributos o campos de interés se
    recorre el arbol resumiendo su contenido en dos elementos compuestos:
    el "Encabezado" y una "lista de CFE_Adendas", respectivamente un diccionario
    y una lista.

    Cargar estructuras simples:
    '''''''''''''''''''''''''''

    Se captura todos los valores de los atributos predefinidos presentes en el
    CFE en curso en objetos de la forma `elemento = valor`, asignando el valor
    'None' a los restantes atributos predefinidos.

    Finalmente se serializará y almacenará, según el caso, en el formato
    correpondiente.

"""


def sobre_consitency_chk(lista_cfe_adenda, caratula):
    """
    Verifica consistencia interna del sobre.
    ========================================
    Los `CFE_Adenda` indicados en la `Caratula`
    de coincidir con la cantidad de `CFE_Adenda` que contiene el Sobre.
    :param lista_cfe_adenda: lista de elementos `CFE_Adenda`.
    :param caratula: objeto py Caratula
    """
    if not (len(lista_cfe_adenda) == caratula):
        msg = 'ERROR: La cantidad de CFE <%s> en el sobre no coincide ' \
              'con la cantidad indicada en la carátula <%s>' \
              % ( len(lista_cfe_adenda), caratula)
        print(msg)
        sys.exit()


class jEncoder(json.JSONEncoder):
    """
        >>> import json
        >>> json.dumps(set([1,2,3,4,5]), cls=jEncoder)
        '[1, 2, 3, 4, 5]'
    """
    def default(self, obj):
        import ipdb; ipdb.set_trace()
        if isinstance(obj, (set,list,int,long,float)):
            return list(obj)
        return json.JSONEncoder.default(self, obj)



if __name__ == "__main__":

    dir_entrada = sys.argv[-1:][0]
    cmd = 'ls -1 %s/*.xml' % (dir_entrada,)
    files = subprocess.check_output(cmd, shell=True).split()

    nroxml = 0

    # se procesa un xml
    for _file in files:
        nroxml += 1

        tag_ctula = "{http://cfe.dgi.gub.uy}Caratula"
        tag_cfead = "{http://cfe.dgi.gub.uy}CFE_Adenda"

        sobre     = ecfeee.XmlLoad(_file)
        caratula  = ecfeee.Caratula( sobre.xml_doc.find(tag_ctula) )

        # Lista de los `CFE_Adenda` del sobre. mín. 1, máx. 250 elementos.
        cfea_list = sobre.xml_doc.findall(tag_cfead)

        sobre_consitency_chk(cfea_list, caratula.CantCFE)

        # prepara el manejo de la salida `csv`
        _json_fname  = _file.split('/')[-1:][0][:-4]

        # Se itera sobre la lista de CFE_Adenda del Sobre. de 1 a 250
        ncfe = 0
        for cfead in cfea_list:

            fecha_caratula = caratula.Fecha.strftime('%Y-%m-%d %H:%M:%S')

            # instancia elemento cfe_adenda
            cfe_adenda = ecfeee.CFE_Adenda(cfead)

            # formatea el objeto json
            json_doc = ecfeee_json.json_Doc(cfe_adenda, fecha_caratula)

            # nombre de archivo de salida del CFE
            json_fname = OUT_DIR + _json_fname + '_' + str(ncfe) + '.json'

            #jse_cfe = jEncoder().encode(json_doc.create) # debug
            #jse_cfe = json_doc.create                    # debug

            with open(json_fname, 'w') as fp:
                json.dump(json_doc.create, fp, INDENT, SORT_K, SEPS)
            ncfe += 1


