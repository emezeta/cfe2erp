# -*- encoding:UTF-8 -*-
#!/usr/bin/env python

import sys
import re
import subprocess
import json
from time import strftime
from lxml import etree, objectify
from lib import template, applib, eFact

from IPython import embed

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

prefix = re.compile('^{.*}')

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


def parse_file(_file):

    with open(_file, "r") as fxml:
        xmlstr = fxml.read().replace('&', '&amp;')

    return xmlstr


def parse_str(xml_str):
    """
        @param: xml_str string de un sobre EnvioCFE_entreEmpresas

        La salida es una tupla de largo 2. (documentos, Caratula)

        Caratula    :  elemento Caratula del Sobre
        documentos  :  lista de elementos `CFE_Adenda`
    """
    xml_doc = etree.fromstring(xml_str)
    docs = list()
    _caratula = None
    for e in xml_doc.getchildren():
        if e.tag == "{http://cfe.dgi.gub.uy}Caratula":
            _caratula = e
        elif e.tag == "{http://cfe.dgi.gub.uy}CFE_Adenda":
            docs.append(e)
        else:
            print "Error ------ prefix /tag "
            sys.exit(1)
    res = tuple((_caratula, docs))
    return res


def efact_py(efact):

    res = dict()
    res.update(template.eFact_tmp)

    #import ipdb; ipdb.set_trace()

    res = dict()
    for i in efact:
        if i is not None:
            tag = tag_ns(i)
            if   tag == 'TmstFirma':
                res[tag] = objectify.fromstring(etree.tostring(i))
            elif tag == 'Encabezado':
                res[tag]  = eFact.Encabezado(objectify.fromstring(etree.tostring(i)))
            elif tag == 'Detalle':
                res[tag] = objectify.fromstring(etree.tostring(i))
            elif tag == 'CAEData':
                res[tag] = objectify.fromstring(etree.tostring(i))
            elif tag == 'SubTotInfo':
                res[tag] = objectify.fromstring(etree.tostring(i))
            elif tag == 'Referencia':
                res[tag] = objectify.fromstring(etree.tostring(i))
            else:
                res['error'] = "Cancela, el elemento es desconocido : %s" % (i,)
                print("Cancela, el elemento es desconocido : %s" % (i,))
                sys.exit()
    return res


def signature_py(signature):
    res = dict()
    return res


def no_vacios(d):
    return dict([(k, v) for k, v in d.iteritems() if(str(v).strip()) ])

def tag_ns(elem):
    """
        elem: es un elemento, tiene un tag!
        strip ns from tag/element name
    """
    try:
        _tag = elem.tag
    except:
        print("Error %s no tiene un tag..." % (elem,))
        return False

    ns = prefix.match(_tag)
    if ns:
        tag = ns.string[ns.end():]
    else:
        tag = _tag
    return tag


class Caratula(object):
    def __init__(self,C):
        self.CantCFE         = C.CantCFE.pyval
        fe = C.Fecha.pyval
        self.Fecha = "%s/%s/%s %s %s" % (fe[8:10], fe[5:7], fe[0:4], fe[11:19], fe[19:])
        self.Idemisor        = C.Idemisor.pyval
        self.RUCEmisor       = C.RUCEmisor.pyval
        self.RutReceptor     = C.RutReceptor.pyval
        self.X509Certificate = C.X509Certificate.pyval



if __name__ == "__main__":
    # import ipdb; ipdb.set_trace()
    entrada = sys.argv[-1:][0]
    files = subprocess.check_output('ls -1 %s/*.xml' % (entrada,),
                                    shell=True).split()
    sobres = list()
    for _file in files:

        xml_str = parse_file(_file)

        # documentos: todos los CFE_Adenda del Sobre
        caratula, documentos = parse_str(xml_str)

        # instancia la clase Caratula
        Caratula = Caratula(objectify.fromstring( etree.tostring( caratula ) ))

        print("CFEs en el sobre: %s" % (Caratula.CantCFE,))

        for i in range(Caratula.CantCFE):
            CFE, Adenda = documentos[i].getchildren()

            eDoc,Signature = CFE.getchildren()
            tag = tag_ns(eDoc)

            if   tag == 'eTck':
                pass
            elif tag == 'eFact':
                encabezado = efact_py(eDoc)['Encabezado']
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






























































