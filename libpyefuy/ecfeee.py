# -*- encoding: utf-8 -*-
# !/usr/bin/env python

from __future__ import print_function

import re
import sys
from dateutil import parser
from lxml import etree, objectify
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
        `iv` function check for any value in the lxml.objectify `val`
        :return: `val` value or None
    """
    try:
        res = val.pyval
    except:
        msg = "Warning: no hay valor para %s" % (val,)
        print(msg)
        res = None
    return res




class initSobre(object):
    """
        Abre el archivo xml, inicializa el arbol element.tree y
        separa la Carátula de su(s) CFE_Adenda(s)
    """


    def __init__(self, xmlfile):
        """
            Lee el archivo xml y crea el arbol xml element tree
            :param: xmlfile: archivo xml contiene un Sobre ecee
        """
        self.xmlfile = xmlfile
        try:
            with open(xmlfile, "r") as fxml:
                xmlstr = fxml.read().replace('&', '&amp;')
            self.xmldoc = etree.fromstring(xmlstr)
        except Exception as ex:
            msg = "El archivo xml %s no está disponible o no es un sobre xml `EnvioCFE_entreEmpresas`" % (self.xmlfile,)
            print(msg)
            sys.exit()


    def carat_docs(self):
        """
            Divide el árbol en `Caratula` y `CFE_Adenda`
            @Caratula: elementoetree `Caratula`
            @documentos: Lista de elementos etree, cutos elementos son `CFE_Adenda`(s) del sobre.

            :return:   tupla de largo 2. ([documentos CFE_Adenda,], Caratula)
        """

        docs  = list()
        cart = None
        for e in self.xmldoc.getchildren():
            tag = tag_ns(e)
            if tag == "Caratula":
                cart = e
            elif tag == "CFE_Adenda":
                docs.append(e)
            else:
                msg = "ERROR: El tag o elemento %s no debería estar allí." % (e,)
                print(msg)
                sys.exit(1)
        res = tuple((cart, docs))
        return res



class Caratula(object):

    def __init__(self, elemtree):
        """
            Crea el objeto Caratula a partir de un elemento etree lxml
            :param elemtree: Un elemeto Catatula.
            :return: Un objeto Caratula

            C.Fecha.pyval == '2016-01-27T18:10:09-03:00'
            # >>> Fecha = dateutil.parser.parse(C.Fecha.pyval)
            # >>> Fecha.strftime('%Y-%m-%d %H:%M:%S')
            ... 2016-11-11 18:10:09 ...etc
        """

        C = objectify.fromstring(etree.tostring(elemtree))
        import ipdb; ipdb.set_trace()
        try:
            self.CantCFE         = C.CantCFE.pyval
            self.Fecha           = parser.parse(C.Fecha.pyval)
            self.Idemisor        = C.Idemisor.pyval
            self.RUCEmisor       = C.RUCEmisor.pyval
            self.RutReceptor     = C.RutReceptor.pyval
            self.X509Certificate = C.X509Certificate.pyval
        except:
            msg = "ERROR: La carátula no ha podido ser inicializada!"
            print(msg)
            sys.exit()


class Adenda(object):
    def __init__(self, adenda):
        tag = tag_ns(adenda)
        if tag == 'Adenda':
            self.Adenda = objectify.fromstring(etree.tostring(adenda))
        else:
            msg = "ERROR: La Adenda del CFE no se ha encontrado."
            print(msg)



class eDoc(object):

    """
        El elemento CFE de cada CFE_Adenda
        Iimpementa un wrapper para uno de:
        eTck, eFact, eFact_Exp, eRem, eRem_Exp, eResg
    """

    def __init__(self, edoc, *args, **kargs):
        self.eDoc = edoc
        self.tag = tag_ns(edoc)
        if self.tag not in ('eTck', 'eFact', 'eFact_Exp', 'eRem', 'eRem_Exp', 'eResg'):
            msg = "ERROR: el tag %s es desconocido. Cancela." % (self.tag,)
            print(self.tag)
            sys.exit()


    def edoc_tmpl(self):
        res = dict()
        res.update(template.eDoc)
        for i in self.eDoc:
            if i is not None:
                tag = tag_ns(i)
                if   tag == 'TmstFirma':
                    res[tag] = objectify.fromstring(etree.tostring(i))
                elif tag == 'Encabezado':
                    res[tag] = eDoc.Encabezado(objectify.fromstring(etree.tostring(i)))
                elif tag == 'Detalle':
                    res[tag] = eDoc.Detalle(objectify.fromstring(etree.tostring(i)))
                elif tag == 'SubTotInfo':
                    res[tag] = eDoc.SubTotInfo(objectify.fromstring(etree.tostring(i)))
                elif tag == 'DscRcgGlobal':
                    res[tag] = eDoc.DscRcgGlobal(objectify.fromstring(etree.tostring(i)))
                elif tag == 'MediosPago':
                    res[tag] = eDoc.MediosPago(objectify.fromstring(etree.tostring(i)))
                elif tag == 'CAEData':
                    res[tag] = eDoc.CAEData(objectify.fromstring(etree.tostring(i)))
                elif tag == 'Referencia':
                    res[tag] = eDoc.Referencia(objectify.fromstring(etree.tostring(i)))
                elif tag == 'Compl_Fiscal':
                    res[tag] = eDoc.Compl_Fiscal(objectify.fromstring(etree.tostring(i)))
                else:
                    res['error'] = "Cancela, el elemento es desconocido : %s" % (i,)
                    print("Cancela, el elemento es desconocido : %s" % (i,))
                    sys.exit()
        return res



class Encabezado(eDoc):

    def __init__ (self, elem):
        self.elem = elem
        self.tag = tag_ns(elem)


    def emisor (self):
        e = self.elem['Emisor']
        res = dict(
            CdgDGISucur = iv(e.CdgDGISucur),
            Ciudad = iv(e.Ciudad),
            Departamento = iv(e.Departamento),
            DomFiscal = iv(e.DomFiscal),
            RUCEmisor = iv(e.RUCEmisor),
            RznSoc = iv(e.RznSoc),
        )
        return res


    def iddoc (self):
        i = self.elem['IdDoc']
        res = dict(
            FchEmis = iv(i.FchEmis),
            FchVenc = iv(i.FchVenc),  # No Obligatorio
            FmaPago = iv(i.FmaPago),
            Nro = iv(i.Nro),
            Serie = iv(i.Serie),
            TipoCFE=iv(i.TipoCFE),
        )
        return res


    def receptor (self):
        r = self.elem['Receptor']
        res = dict(
            CiudadRecep = iv(r.CiudadRecep),
            CodPaisRecep = iv(r.CodPaisRecep),
            CompraID=iv(r.CompraID),  # No Obligatorio
            DeptoRecep = iv(r.DeptoRecep),  # No Obligatorio
            DirRecep = iv(r.DirRecep),
            DocRecep = iv(r.DocRecep),
            PaisRecep = iv(r.PaisRecep),  # No Obligatorio
            RznSocRecep = iv(r.RznSocRecep),
            TipoDocRecep = iv(r.TipoDocRecep),
            InfoAdicional = iv(r.InfoAdicional),  # No Obligatorio
        )
        return res


    def totales (self):
        t = self.elem['Totales']
        res = dict(
            CantLinDet = iv(t.CantLinDet),
            IVATasaBasica = iv(t.IVATasaBasica),
            MntIVATasaBasica = iv(t.MntIVATasaBasica),  # No Obligatorio
            MntNetoIVATasaBasica = iv(t.MntNetoIVATasaBasica),  # No Obligatorio
            MntPagar = iv(t.MntPagar),
            MntTotal = iv(t.MntTotal),
            MontoNF = iv(t.MontoNF),  # No Obligatorio
        )
        return res


class Detalle(eDoc):

    def __init__ (self, elem):
        self.elem = elem
        self.tag = tag_ns(elem)


    def cantidad (self):
        self.elem.Item.Cantidad


    def coditem (self):
        self.elem.Item.CodItem


    def descuentomonto (self):
        self.elem.Item.DescuentoMonto


    def descuentopct (self):
        self.elem.Item.DescuentoPct


    def indfact (self):
        self.elem.Item.IndFact


    def montoitem (self):
        self.elem.Item.MontoItem


    def nomitem (self):
        self.elem.Item.NomItem


    def nrolindet (self):
        self.elem.Item.NroLinDet


    def preciounitario (self):
        self.elem.Item.PrecioUnitario


    def unimed (self):
        self.elem.Item.UniMed


class SubTotInfo(eDoc):
    def __init__ (self, elem):
        self.elem = elem
        self.tag = tag_ns(elem)


class DscRecGlobal(eDoc):
    def __init__ (self, elem):
        self.elem = elem
        self.tag = tag_ns(elem)


class MrdiosPago(eDoc):
    def __init__ (self, elem):
        self.elem = elem
        self.tag = tag_ns(elem)


class Referencia(eDoc):
    def __init__ (self, elem):
        self.elem = elem
        self.tag = tag_ns(elem)


class CAEdata(eDoc):
    def __init__ (self, elem):
        self.elem = elem
        self.tag = tag_ns(elem)


class ComplFiscal(eDoc):
    def __init__ (self, elem):
        self.elem = elem
        self.tag = tag_ns(elem)
