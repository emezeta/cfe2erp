# coding: utf-8
#!/usr/bin/env python

from __future__ import print_function

import StringIO
import csv
import json
import subprocess
import sys
from lxml import etree, objectify
from time import strftime

from libpyefuy import ecfeee, template

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


def write_csv(fname, data):
    path = "/tmp/" + fname
    with open(path, "w") as f:
        f.write(data)



if __name__ == "__main__":

    entrada = sys.argv[-1:][0]
    files = subprocess.check_output('ls -1 %s/*.xml' % (entrada,),
                                    shell=True).split()


    for _file in files:

        # salida csv ---------------
        lin_csv = StringIO.StringIO()
        writer = csv.writer(lin_csv, delimiter= '|', lineterminator='\r\n')
        csv_fname = _file.split('/')[-1:][0][:-3] + 'csv'
        # --------------------------

        try:
            cfe_empresas = ecfeee.initSobre(_file)
        except Exception as e:
            msg = "\n\tERROR: %s \n\tal procesar %s." (e, _file)
            print(msg)

        root = cfe_empresas.xmldoc

        elemento_cfe_adenda = cfe_empresas.sobre['CFE_Adenda']

        Caratula = ecfeee.Caratula( cfe_empresas.sobre['Caratula'] )

        print("CFEs en el sobre: %s archivo %s" % (Caratula.CantCFE, _file))

        if not (len(elemento_cfe_adenda) == Caratula.CantCFE):
            msg = "ERROR: La cantidad de CFE <%s> en el sobre no coincide " \
                  "con la cantidad indicada en la carátula <%s>" \
                  % ( len(elemento_cfe_adenda), Caratula.CantCFE)
            print(msg)
            sys.exit()

        print("Dia: %s " % (Caratula.Fecha.strftime('%Y-%m-%d %H:%M:%S'), ))

        for cfe_adenda in elemento_cfe_adenda:

            csv_row = list()

            cfe_adenda_obj = objectify.fromstring(etree.tostring(cfe_adenda))
            cfe = cfe_adenda_obj.CFE
            tag = ecfeee.tag_ns(cfe)

            if tag == 'CFE':

                cfe_doc, signature = cfe.getchildren()
                eDoc_obj = objectify.fromstring(etree.tostring(cfe_doc))

                linea = "Emisor: %s %s: %s %s " % (eDoc_obj.Encabezado.Emisor.RznSoc.pyval, ecfeee.tag_ns(eDoc_obj), eDoc_obj.Encabezado.IdDoc.Serie.pyval, eDoc_obj.Encabezado.IdDoc.Nro.pyval)

                print(linea, "\n ===")

            csv_row.append('C')
            csv_row.append(Caratula.Fecha.strftime('%Y-%m-%d %H:%M:%S'))
            csv_row.append(eDoc_obj.Encabezado.Emisor.RznSoc.pyval)
            csv_row.append(ecfeee.tag_ns(eDoc_obj))
            csv_row.append(eDoc_obj.Encabezado.IdDoc.Serie.pyval)
            csv_row.append(eDoc_obj.Encabezado.IdDoc.Nro.pyval)

            # lrpmqtp charset!
            to_str = list()
            for i in csv_row:
                if isinstance(i, (int,long,float)):
                    i = str(i)
                to_str.append(i)

            writer.writerow([campo.encode('utf_8') for campo in to_str])

        write_csv(csv_fname, lin_csv.getvalue())









