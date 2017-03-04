# coding: utf-8
#!/usr/bin/env python

from __future__ import print_function

import json
import subprocess
import sys
from lxml import etree, objectify
from time import strftime

from libpyefuy import ecfeee, csv_tools



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

    """ Los nombres de `Objetos` capitalizados.
        Los nombres de `element` lxml en minúsculas.
    """
    # from IPython import embed; embed()
    # import ipdb; ipdb.set_trace()
    dir_entrada = sys.argv[-1:][0]

    cmd = 'ls -1 %s/*.xml' % (dir_entrada,)
    files = subprocess.check_output(cmd, shell=True).split()

    for _file in files:
        '''
        try:
            cfe_empresas = ecfeee.initSobre(_file)
        except Exception as e:
            msg = '\n\tERROR: %s \n\tal procesar %s' % (e, _file)
            print(msg)
        '''
        sobre = ecfeee.initSobre(_file)

        Caratula = ecfeee.Caratula(sobre.caratula)
        cfe_adenda_lst = sobre.cfe_adenda_lst
        sobre_consitency_chk(cfe_adenda_lst, Caratula.CantCFE)

        prn_caratula(Caratula, _file)

        """ prepara el manejo de la salida `csv` """
        csv_fname  = _file.split('/')[-1:][0][:-3] + 'csv'
        csv_handle = csv_tools.handle(csv_fname)

        """ Se itera sobre los CFE_Adenda contenidos en el sobre (1 a 250 veces) """
        CFE_Adenda = list()
        for cfe_adenda in cfe_adenda_lst:

            ccsv_row = list()   # salida registro cabezal
            lcvs_row = list()   # salida registro línea
            """
            Documentación
                cfe = cfe_adenda[0]     # CFE
                    eDoc = cfe[0] {Encabezado, Detalle, CAEData}
                    Signature = cfe[1]

                adenda = cfe_adenda[1]  # Adenda
            """
            if len(cfe_adenda) > 1:
                Adenda = cfe_adenda[1].text
            Signature = cfe_adenda[0][1]

            # import ipdb; ipdb.set_trace()
            cfe_doc   = ecfeee.eDoc(cfe_adenda[0][0])
            CFE_Adenda.append(cfe_doc)


            #edo=CFE_Adenda[0]
            #import ipdb; ipdb.set_trace()
            #edo.Encabezado()







            """
            print('Emisor_RznSoc '+'Ttpo_CFE '+'IdDoc_Serie '+'IdDoc_Nro '+'SubTotal')
            linea = 'Emisor: %s %s: %s %s %s' % (cfe_doc.Encabezado.Emisor.RznSoc.pyval, cfe_doc.tag_ns(cfe_doc),cfe_doc.Encabezado.IdDoc.Serie.pyval, cfe.Encabezado.IdDoc.Nro.pyval,cfe_doc.SubTotInfo.STI_Item.ValSubtotSTI.pyval)
            print(linea, '\n ===')

            # la línea es un cabezal
            ccsv_row.append('C')
            ccsv_row.append(Caratula.Fecha.strftime('%Y-%m-%d %H:%M:%S'))
            ccsv_row.append(cfe_doc.Encabezado.Emisor.RznSoc.pyval)
            ccsv_row.append(ecfeee.tag_ns(cfe_doc))
            ccsv_row.append(cfe_doc.Encabezado.IdDoc.Serie.pyval)
            ccsv_row.append(cfe_doc.Encabezado.IdDoc.Nro.pyval)

            # lrpmqtp charset!
            csv_handle.record(ccsv_row)


        csv_handle.write_csv()
    """









