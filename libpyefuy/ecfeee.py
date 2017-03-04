# coding: utf-8
# !/usr/bin/env python

from __future__ import print_function

import re
import sys
# from IPython import embed
from dateutil import parser
from lxml import etree, objectify
from mock import self

import template



__author__ = "emezeta"
__author_email__ = "emezeta@insiberia.net"
__copyright__ = "Copyright (C) 2017 eFacturaUy"
__license__ = "GPL 3.0"
__version__ = "0.99"

"""
    Los sobres xml del tipo `EnvioCFE_entreEmpresas` constan de 2 elementos:

        @ Caratula
        @ CFE_Adenda   ( lista de elementos mínimo 1 y máximo 250)

    y un atributo, la versión del esquema xsd.  (no interesa para estas clases)

    Se implementan clases útiles para leer (o escribir) sobres xml del tipo `EnvioCFE_entreEmpresas`

    TODO: o escribir.
"""

prefix = re.compile('^{.*}')


def tag_ns(elem):
    """
        elem: es un elemento, tiene un tag!
        strip ns from tag/element name
    """
    try:
        _tag = elem.tag
    except:
        msg = "Error %s no tiene un tag..." % (elem,)
        print(msg)
        return False
    ns = prefix.match(_tag)
    if ns:
        tag = ns.string[ns.end():]
    else:
        tag = _tag
    return tag


def no_vacios(d):
    return dict([(k, v) for k, v in d.iteritems() if(str(v).strip()) ])


def iv(val=None):
    """
        `iv` If_Value() function check for any value in the lxml.objectify `val`
        :param val: lxml.objectify `val` element
        :return: `val` value or error message
    """

    try:
        res = val.pyval
    except:
        msg = "Warning: no hay valor para %s" % (val,)
        print(msg)
        res = msg
    return res


def try_decode(str_doc):
    # import ipdb;ipdb.set_trace()
    # ['cp850', 'cp858', 'cp437', 'cp1140', 'cp1250', 'cp1252', 'latin_1', 'iso8859_15', 'utf_8', 'ascii' ]

    cod = None
    res = False
    doc = False
    codecs = ['utf_8', 'latin_1', 'cp1252', 'iso8859_15', 'cp850', 'cp437']
    for dec in codecs:
        cod = None
        try:
            doc = str_doc.decode(dec, 'error')
            cod = dec
            break
        except:
            pass

    if cod == 'utf_8':
        res = doc
    elif cod:
        try:
            res = doc.encode('utf_8')
        except Exception as ex:
            msg = "ERROR: Fallo de de/codificación de caracteres del archivo.\n\t\t %s" % ex
            print(msg)
            # res = False
            sys.exit()

    return res


def to_obj(elemento):

    return objectify.fromstring(etree.tostring(elemento))


class initSobre(object):
    """
        Abre el archivo xml, inicializa el arbol element.tree y
        separa la Carátula de su(s) CFE_Adenda(s)
    """


    def __init__(self, xmlfile):
        """
            Lee el archivo xml y crea el arbol xml element tree
            :param: xmlfile: archivo xml contiene un Sobre ecee

            Divide el árbol en `Caratula` (elemento único) y `CFE_Adenda` ( 1 a 250 elementos )
            @Caratula: elementoetree `Caratula`
            @documentos: Lista de elementos etree, tantos elementos como CFE_Adenda(s) contenga el sobre.

            :return:   tupla de largo 2. ([documentos CFE_Adenda,], Caratula)
        """

        try:
            xmldoc = etree.parse(xmlfile)
            self.xmldoc = xmldoc.getroot()
        except Exception as ex:
            msg = "Archivo %s no disponible o no es un CFE `EnvioCFE_entreEmpresas` \n\t%s" % (xmlfile, ex)
            print(msg)
            sys.exit()

        cfe_adenda_lst = list()
        cartula = None

        for e in self.xmldoc.getchildren():
            tag = tag_ns(e)
            if tag == "Caratula":
                cartula = e
            elif tag == "CFE_Adenda":
                cfe_adenda_lst.append(e)
            else:
                msg = "ERROR: El tag o elemento %s no debería estar allí." % (e,)
                print(msg)
                sys.exit()

        self.caratula       = cartula
        self.cfe_adenda_lst = cfe_adenda_lst



class Caratula(object):

    def __init__(self, caratula):
        """
            Crea el objeto Caratula a partir de un elemento etree lxml
            :param caratula: Elemeto lxml `Catatula`.
            :return: Objeto Caratula

            C.Fecha.pyval == '2016-01-27T18:10:09-03:00'
            # >>> Fecha = dateutil.parser.parse(C.Fecha.pyval)
            # >>> Fecha.strftime('%Y-%m-%d %H:%M:%S')
            ... 2016-11-11 18:10:09 ...etc
        """
        C = objectify.fromstring(etree.tostring(caratula))

        # import ipdb; ipdb.set_trace()
        try:
            self.CantCFE         = C.CantCFE.pyval
            self.Fecha           = parser.parse(C.Fecha.pyval)
            self.Idemisor        = C.Idemisor.pyval
            self.RUCEmisor       = C.RUCEmisor.pyval
            self.RutReceptor     = C.RutReceptor.pyval
            self.X509Certificate = C.X509Certificate.pyval
        except Exception as ex:
            msg = "ERROR: %s \n\tNo se ha podido inicializar la carátula!" % (ex,)
            print(msg)
            sys.exit()


class Adenda(object):

    """ `initSobre.sobre['CFE_Adenda']` """

    def __init__(self, adenda):
        """
        :param adenda: etree/CFE_Adenda/Adenda
        :return: texto adenda
        """
        tag = tag_ns(adenda)
        if tag == 'Adenda':
            adenda_obj = objectify.fromstring(etree.tostring(adenda))
            # self.Adenda_py = adenda_obj.pyval
            self.Adenda_obj = adenda_obj.text
        else:
            msg = "ERROR: La Adenda del CFE no se ha encontrado."
            print(msg)



class eDoc(object):
    """
    Reprecentación del elemento CFE.
    ================================

    La clase se inicializa con uno de los tipos de CFEs:
        `eTck, eFact, eFact_Exp, eRem, eRem_Exp, eResg`
    A priori no se sabe cual ellos será.
    """

    def __init__(self, edoc_elem):
        """
        :param edoc_elem: es un elemento lxml <Element {http://cfe.dgi.gub.uy}CFE
                          uno de `eTck, eFact, eFact_Exp, eRem, eRem_Exp, eResg`
        @edoc_elem_lst: elementos hijos.
        """
        # import ipdb; ipdb.set_trace()

        self.edoc_name     = tag_ns(edoc_elem)
        self.edoc_elem_lst = edoc_elem.getchildren()
        self.edoc_objects  = dict()
        self.edoc_values   = dict()
        # self.edoc_done     = list()
        self._wrap()


    def _wrap(self):

        edoc_objects = dict()
        # done = list()
        for edoc_elem in self.edoc_elem_lst:
            edoc_obj = objectify.fromstring(etree.tostring(edoc_elem))
            tag = tag_ns(edoc_elem)
            if   tag == 'TmstFirma':
                self.edoc_objects[tag] = edoc_obj.TmstFirma = edoc_obj.text
                # self.edoc_done.append(edoc_elem)
            elif tag == 'Encabezado':
                self.edoc_objects[tag] = edoc_obj
                self.Encabezado()
            elif tag == 'Detalle':
                self.edoc_objects[tag] = edoc_obj
            elif tag == 'SubTotInfo':
                self.edoc_objects[tag] = edoc_obj
            elif tag == 'DscRcgGlobal':
                self.edoc_objects[tag] = edoc_obj
            elif tag == 'MediosPago':
                self.edoc_objects[tag] = edoc_obj
            elif tag == 'CAEData':
                self.edoc_objects[tag] = edoc_obj
            elif tag == 'Referencia':
                self.edoc_objects[tag] = edoc_obj
            elif tag == 'Compl_Fiscal':
                self.edoc_objects[tag] = edoc_obj
            else:
                # import ipdb; ipdb.set_trace()
                edoc_objects[tag] = 'ERROR'
                raise Exception("Cancela, el elemento es desconocido : %s" % (tag,))

        """

        for i in done:
            edoc_elem_lst.remove(i)
        """

        self.edoc_objects.update(edoc_objects)



    def Encabezado(self):
        """

        """
        #import ipdb;ipdb.set_trace()
        E = self.edoc_objects['Encabezado']

        e = E.Emisor
        self.edoc_values['Emisor'] = dict(
            CdgDGISucur          = e.CdgDGISucur          if hasattr(e, 'CdgDGISucur' )         else None,
            Ciudad               = e.Ciudad               if hasattr(e, 'Ciudad'      )         else None,
            Departamento         = e.Departamento         if hasattr(e, 'Departamento')         else None,
            DomFiscal            = e.DomFiscal            if hasattr(e, 'DomFiscal'   )         else None,
            RUCEmisor            = e.RUCEmisor            if hasattr(e, 'RUCEmisor'   )         else None,
            RznSoc               = e.RznSoc               if hasattr(e, 'RznSoc'      )         else None,
        )

        i = E.IdDoc
        self.edoc_values['IdDoc'] = dict(
            FchEmis              = i.FchEmis              if hasattr(i,'FchEmis')               else None,
            FchVenc              = i.FchVenc              if hasattr(i,'FchVenc')               else None,  # No Obligatorio
            FmaPago              = i.FmaPago              if hasattr(i,'FmaPago')               else None,
            Nro                  = i.Nro                  if hasattr(i,'Nro'    )               else None,
            Serie                = i.Serie                if hasattr(i,'Serie'  )               else None,
            TipoCFE              = i.TipoCFE              if hasattr(i,'TipoCFE')               else None,
        )

        r = E.Receptor
        self.edoc_values['Receptor'] = dict(
            CiudadRecep          = r.CiudadRecep          if hasattr(r, 'CiudadRecep'         ) else None,
            CodPaisRecep         = r.CodPaisRecep         if hasattr(r, 'CodPaisRecep'        ) else None,
            CompraID             = r.CompraID             if hasattr(r, 'CompraID'            ) else None, # No Obligatorio
            DeptoRecep           = r.DeptoRecep           if hasattr(r, 'DeptoRecep'          ) else None, # No Obligatorio
            DirRecep             = r.DirRecep             if hasattr(r, 'DirRecep'            ) else None,
            DocRecep             = r.DocRecep             if hasattr(r, 'DocRecep'            ) else None,
            PaisRecep            = r.PaisRecep            if hasattr(r, 'PaisRecep'           ) else None, # No Obligatorio
            RznSocRecep          = r.RznSocRecep          if hasattr(r, 'RznSocRecep'         ) else None,
            TipoDocRecep         = r.TipoDocRecep         if hasattr(r, 'TipoDocRecep'        ) else None,
            InfoAdicional        = r.InfoAdicional        if hasattr(r, 'InfoAdicional'       ) else None, # No Obligatorio
        )


        t = E.Totales
        self.edoc_values['Totales'] = dict(
            CantLinDet           = t.CantLinDet           if hasattr(t, 'CantLinDet'          ) else None,
            IVATasaBasica        = t.IVATasaBasica        if hasattr(t, 'IVATasaBasica'       ) else None,
            MntIVATasaBasica     = t.MntIVATasaBasica     if hasattr(t, 'MntIVATasaBasica'    ) else None,  # No Obligatorio
            MntNetoIVATasaBasica = t.MntNetoIVATasaBasica if hasattr(t, 'MntNetoIVATasaBasica') else None,  # No Obligatorio
            MntPagar             = t.MntPagar             if hasattr(t, 'MntPagar'            ) else None,
            MntTotal             = t.MntTotal             if hasattr(t, 'MntTotal'            ) else None,
            MontoNF              = t.MontoNF              if hasattr(t, 'MontoNF'             ) else None,  # No Obligatorio
        )





"""
class Detalle(eDoc):

    def __init__(self):
        # self.elem = elem
        # self.tag = tag_ns(elem)
        super(eDoc, self).__init__()
        self.elem = self.


    def cantidad(self):
        res = self.elem.Item.Cantidad
        return res


    def coditem(self):
        res = self.elem.Item.CodItem


    def descuentomonto(self):
        res = self.elem.Item.DescuentoMonto


    def descuentopct(self):
        res = self.elem.Item.DescuentoPct


    def indfact(self):
        res = self.elem.Item.IndFact


    def montoitem(self):
        res = self.elem.Item.MontoItem


    def nomitem(self):
        res = self.elem.Item.NomItem


    def nrolindet(self):
        res = self.elem.Item.NroLinDet


    def preciounitario(self):
        res = self.elem.Item.PrecioUnitario


    def unimed(self):
        res = self.elem.Item.UniMed



class SubTotInfo(eDoc):
    def __init__(self, elem):
        self.elem = elem
        self.tag = tag_ns(elem)
        super(eDoc, self).__init__()



class DscRecGlobal(eDoc):
    def __init__(self, elem):
        self.elem = elem
        self.tag = tag_ns(elem)
        super(eDoc, self).__init__()



class MediosPago(eDoc):
    def __init__(self, elem):
        self.elem = elem
        self.tag = tag_ns(elem)
        super(eDoc, self).__init__()



class Referencia(eDoc):
    def __init__(self, elem):
        self.elem = elem
        self.tag = tag_ns(elem)
        super(eDoc, self).__init__()



class CAEdata(eDoc):
    def __init__(self, elem):
        self.elem = elem
        self.tag = tag_ns(elem)
        super(eDoc, self).__init__()



class ComplFiscal(eDoc):
    def __init__(self, elem):
        self.elem = elem
        self.tag = tag_ns(elem)
        super(eDoc, self).__init__()

"""
