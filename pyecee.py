# -*- encoding:UTF-8 -*-
#!/usr/bin/env python

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


    Levanta los sobres xml de una carpeta y los parsea uno a uno a árboles
    lxml (lxml.de)

    Por cada árbol analizado, se creará una lista de dos elementos:
        ["Encabezado", "lista de CFE_Adenda"]

    Cargar estructuras simples:
    '''''''''''''''''''''''''''
    	Dos alternativas
    	1. Usando un `teamplate` de estructura completa inicializada a None.
    	   Los los tipos de CFE descritos en EnvioCFE_entreEmpresas.xsd son
    	   seis: 'eTck', 'eFact', 'eFact_Exp', 'eRem', 'eRem_Exp' y 'eResg'

    	   Recorrer el dom cargando los elementos que corresponda.
    	   Eliminar todos los elementos 'None' de la 'instancia' de tmplt.


    	2. Sin usar tmplt recorrer el dom, cargar `element.tag = valor`.
    	   Recomponer la estrucutra.

    	Finalmente, armar cabezal/líneas de documentos a importar.
    	Serializar y almacenar.


    TODO::
        Deserializar (emezamos por json) y almacenar
        Documentar, agregar comentarios, pepochizar
        Crear un módulo/clase(s) importable(s)

"""

import sys
import re
import subprocess
import json
from time import strftime
from lxml import etree, objectify
from lib import template, applib
from lib import eFact

# from IPython import embed



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


def caratula_py(catla):

    caratula_obj= objectify.fromstring(etree.tostring(catla))
    res = template.Caratula_tmp

    ns  = prefix.match(caratula_obj.tag)
    _tag = ns.string[ns.end():]

    if _tag == 'Caratula':

        for i in caratula_obj.getchildren():

            try:
                ns  = prefix.match(i.tag)
                _tag = ns.string[ns.end():]
                res[_tag] = i # i.text?
            except:
                print "Error ------ prefix /tag Caratula"
                sys.exit()

    else:
        msg = "\tError ------ prefix /tag Caratula"

    return res



def efact_py(efact):

    res = dict()
    res.update(template.eFact_tmp)
    efact_obj = objectify.fromstring(etree.tostring(efact))
    """ no logré preguntarle amablemente al elemento si sus hijos
        servían para algo o no. Sin embargo entendió. """

    try:
        tmstfirma  =  efact_obj['TmstFirma'].pyval
        encabezado =  efact_obj['Encabezado']
        caedata    =  efact_obj['CAEData']
        detalle    =  efact_obj['Detalle']
    except:
        print "Cancela. Falta in elemento obligatorio."
        sys.exit()

    try:
        subtotinfo = efact_obj['SubTotInfo']
    except:
        subtotinfo = None

    try:
        referencia = efact_obj['Referencia']
    except:
        referencia = None

    res['TmstFirma'] = tmstfirma
    #import ipdb; ipdb.set_trace()

    for i in [encabezado,caedata,detalle,subtotinfo,referencia]:
        if i is not None:
            tag = tag_ns(i)
            if   tag == 'Encabezado':
                res[tag] = eFact.Encabezado(i)
            elif tag == 'Detalle':
                res[tag] = eFact.Detalle(i)
            elif tag == 'CAEData':
                res[tag] = eFact.CAEdata(i)
            elif tag == 'SubTotInfo':
                res[tag] = eFact.SubTotInfo(i)
            elif tag == 'Referencia':
                res[tag] = eFact.Referencia(i)
            else:
                print("Cancela, el elemento es desconocido :" % (i,))
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




if __name__ == "__main__":

    entrada = sys.argv[-1:][0]
    files = subprocess.check_output('ls -1 %s/*.xml' % (entrada,),
                                    shell=True).split()
    sobres = list()

    for _file in files:

        xml_str = parse_file(_file)

        # documentos: todos los CFE_Adenda del Sobre
        caratula, documentos = parse_str(xml_str)

        # es objeto python
        Caratula = caratula_py(caratula)

        fe = Caratula['Fecha'].text
        fech = "%s/%s/%s %s %s" % (fe[8:10], fe[5:7], fe[0:4], fe[11:19], fe[19:])
        cant = Caratula['CantCFE']
        idem = Caratula['Idemisor']
        rute = Caratula['RUCEmisor']
        rutr = Caratula['RutReceptor']

        print("Sobre %s  CFEs del sobre: %s" % (_file, cant))
        #import ipdb;ipdb.set_trace()
        for i in range(Caratula['CantCFE']):

            CFE = Adenda = None
            CFE_Adenda = documentos[0]

            for j in CFE_Adenda:
                tag = tag_ns(j)
                if tag == 'CFE':
                    CFE = j
                elif tag == 'Adenda':
                    Adenda = j
                else:
                    print "\tError ------ prefix /tag "
                    # grabar log y continue.

                    # ---- debug
                    iok = raw_input("Intenta continuar s/n :")
                    if iok not in ['S','s','Y','y']:
                        sys.exit()
                    else:
                        continue

            eDoc,Signature = CFE.getchildren()
            tag = tag_ns(eDoc)

            if   tag == 'eTck':
                pass
            elif tag == 'eFact':
                eDoc_py = efact_py(eDoc)
                encabezado = eDoc_py['Encabezado']
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
            print("\n\tCantCFE       : %s\n\tFecha         : %s\n\tIdemisor      : %s\n\tRUCEmisor     : %s\n\tRutReceptor   : %s\n\n" % (cant, fech, idem, rute, rutr))

            print("\tCfe Nro %s de %s\n\n" % (i+1,cant))

            print("\t\t %s" % (encabezado.tag,))

            print( "\tEmisor")
            for i in encabezado.emisor():
                print( "\t\t%s\t%s" % (i,encabezado.emisor()[i]))

            print( "\tIdDoc")
            for i in encabezado.iddoc():
                print( "\t\t%s\t%s" % (i,encabezado.iddoc()[i]))

            print( "\tReceptor")
            for i in encabezado.receptor():
                print( "\t\t%s\t%s" % (i,encabezado.receptor()[i]))

            print( "\tTotales")
            for i in encabezado.totales():
                print( "\t\t%s\t%s" % (i,encabezado.totales()[i]))

            print("x"*60)

            #raw_input('%s...\n' % (25*' ',))
































































