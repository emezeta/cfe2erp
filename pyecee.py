# coding: utf-8
#!/usr/bin/env python3

from __future__ import print_function


import subprocess
import sys

from libpyefuy import config, csv_tools, ecfeee_csv
from libpyefuy.ecfeee import EnvioCFE_entreEmpresas as ecfeee
from libpyefuy.ecfeee import Caratula, CFE_Adenda

OUT_DIR = config.out_path


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


def prn_caratula(caratula, xml_file):
    print('CFEs en el sobre: %s | Archivo %s' % (caratula.CantCFE, xml_file))
    print('Dia: %s ' % (caratula.Fecha.strftime('%Y-%m-%d %H:%M:%S'), ))
    return True


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
        try:
            root       = ecfeee(_file)
            caratula   = Caratula(root.caratula)
            cfe_adenda = CFE_Adenda(root.cfe_adenda).cfead
            sobre_consitency_chk(root.cfe_adenda, caratula.CantCFE)
        except Exception:
            import ipdb, sys
            ipdb.post_mortem(sys.exc_info()[2])

        """ prepara el manejo de la salida `csv` """
        _csv_fname  = _file.split('/')[-1:][0][:-4]

        """ Se itera sobre los CFE_Adenda del sobre. Entre 1 y 250 por cada _file """
        ncfe = 0
        for cfead in cfe_adenda:
            csv_fname = OUT_DIR + _csv_fname + '_' + str(ncfe) + '.csv'
            ncfe += 1
            stream = open(csv_fname, "w")
            csv_handle = csv_tools.csvUnicodeHandler(stream)

            fecha_caratula = caratula.Fecha.strftime('%Y-%m-%d %H:%M:%S')

            try:
                csv_doc = ecfeee_csv.csv_Doc(cfead,fecha_caratula)
            except Exception:
                import ipdb, sys
                ipdb.post_mortem(sys.exc_info()[2])

            header_cabezal, linea_cabezal = csv_doc.cabezal
            header_lineas, lineas = csv_doc.lineas

            csv_handle.writerow(header_cabezal)
            csv_handle.writerow(linea_cabezal)
            csv_handle.writerow(header_lineas)
            for linea in lineas:
                csv_handle.writerow(linea)
