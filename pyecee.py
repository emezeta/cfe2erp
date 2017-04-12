# coding: utf-8
#!/usr/bin/env python

from __future__ import print_function

import json
import subprocess
import sys
#from lxml import etree, objectify
from time import strftime

from libpyefuy import config, csv_tools, ecfeee_csv
from libpyefuy.ecfeee import EnvioCFE_entreEmpresas as _ecfeee, Caratula, CFE_Adenda


OUT_DIR = config.out_path


"""
    **pyecee.py EnvioCFE_entreEmpresas**

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

    	2. Sin usar tmplt recorrer el dom, cargar `element.tag = valor`,
           asignando valor 'None' a los elementos opcionales ausentes, que
           no obstante hayan sido definidos para componer el conjunto de
           datos a extraer del xml.
    	   
        Para la interfase CSV se toma la alternativa 2.

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


def prn_caratula(caratula, xml_file):
    print('CFEs en el sobre: %s | Archivo %s' % (caratula.CantCFE, xml_file))
    print('Dia: %s ' % (caratula.Fecha.strftime('%Y-%m-%d %H:%M:%S'), ))
    return True


def pare():
    msg = 'ERROR: forzado'
    print(msg)
    sys.exit()


# from IPython import embed; embed()
# import ipdb; ipdb.set_trace()
if __name__ == "__main__":

    dir_entrada = sys.argv[-1:][0]
    cmd = 'ls -1 %s/*.xml' % (dir_entrada,)
    files = subprocess.check_output(cmd, shell=True).split()

    nroxml = 0
    #files = ['./Sob_18.xml']

    # se procesa un xml
    for _file in files:
        nroxml += 1
        #print("F", nroxml),
        root       = _ecfeee(_file)
        caratula   = Caratula(root.caratula)
        cfe_adenda = CFE_Adenda(root.cfe_adenda).cfead
        sobre_consitency_chk(root.cfe_adenda, caratula.CantCFE)

        """ prepara el manejo de la salida `csv` """
        _csv_fname  = _file.split('/')[-1:][0][:-4]


        """ Se itera sobre los CFE_Adenda del sobre. Entre 1 y 250 por cada _file """


        ncfe = 0
        for cfead in cfe_adenda:
            ncfe += 1

            Adenda = cfead['adenda']
            csv_fname = OUT_DIR + _csv_fname + '_' + str(ncfe) + '.csv'

            stream = open(csv_fname, "w")
            csv_handle = csv_tools.csvUnicodeHandler(stream)
            print('\n',_file)
            header_cabezal, linea_cabezal = ecfeee_csv.arma_cabezal(cfead,caratula.Fecha.strftime('%Y-%m-%d %H:%M:%S'))

            csv_handle.writerow(header_cabezal)
            csv_handle.writerow(linea_cabezal)


            # *** FIN   cabezal CSV ***
            """
            lin_cvs_row = list()
            for procersar i[' :
                lin_cvs_row.append('')
                # lrpmqtp charset!
                csv_handle.record(lin_cvs_row)      # nueva línea linea_csv       lcsv_row
            """

            #csv_handle.write_csv()


"""
        # from IPython import embed; embed()
        # import ipdb; ipdb.set_trace()

Líneas:
    serie                                               'NroLinDet'
    numero                                              'IndFact'
    proveedor_rut                                       'CodItem'
    articulo                                            'NomItem'
        codigo 1                                        'Cantidad'
        codigo 2                                        'UniMed'
    articulo_descripcion                                'DscItem'
    cantidad                                            'PrecioUnitario'
    unidad de medida                                    'MontoItem'
    precio unitario sin impuesto                        'SubDescuento'
    descuento                                           'DescuentoMonto'
    tipo de iva                                         'DescuentoPct'
    monto total iva
    monto total linea
"""
