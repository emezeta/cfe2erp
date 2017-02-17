# -*- encoding: utf-8 -*-
# !/usr/bin/env python

from __future__ import print_function

import dateutil
import re
import sys

import template


# import subprocess
# import json
# from time import strftime
# from lxml import etree, objectify
# from IPython import embed
# from apparmor.common import msg

__author__ = "emezeta"
__author_email__ = "emezeta@insiberia.net"
__copyright__ = "Copyright (C) 2017 eFacturaUy"
__license__ = "GPL 3.0"
__version__ = "0.99"


"""
    Los sobres xml del tipo `EnvioCFE_entreEmpresas` constan de 2 elementos:
    Un CFE y su Adenda. Un atributo, la versión del esquema xsd.

"""


def no_vacios(d):
    return dict([(k, v) for k, v in d.iteritems() if(str(v).strip()) ])


class EnvioCFEentreEmpresas(object):


    def __init__(self, xmlfile):
        self.xmlfile = xmlfile
        try:
            with open(xmlfile, "r") as fxml:
                self.xmlstr = fxml.read().replace('&', '&amp;')
        except Exception as ex:
            msg = "El archivo xml %s no está disponible." % (self.xmlfile,)
            print(msg)
            sys.exit()
        self.prefix = re.compile('^{.*}')


    def Caratula(self,C):

        try:
            self.CantCFE         = C.CantCFE.pyval
            self.Fecha           = dateutil.parser(C.Fecha.pyval)
            self.Idemisor        = C.Idemisor.pyval
            self.RUCEmisor       = C.RUCEmisor.pyval
            self.RutReceptor     = C.RutReceptor.pyval
            self.X509Certificate = C.X509Certificate.pyval
        except:
            msg = "ERROR: La carátula no ha podido ser inicializada\n XML : s%" % (self.xml_file,)
            print(msg)
            sys.exit()


    def parse_str(self):
        """
            @param: xml_str string de un sobre EnvioCFE_entreEmpresas
            La salida es una tupla de largo 2. (documentos, Caratula)
            Caratula    :  elemento Caratula del Sobre
            documentos  :  lista de elementos `CFE_Adenda`
        """
        xml_doc = etree.fromstring(self.xmlstr)
        docs = list()
        caratula_ = None
        for e in xml_doc.getchildren():
            tag = self.tag_ns(e)
            if tag == "Caratula":
                caratula_ = e
            elif tag == "CFE_Adenda":
                docs.append(e)
            else:
                msg = "ERROR: El tag o elemento %s no debería estar allí." % (e,)
                print(msg)
                sys.exit(1)
        res = tuple((caratula_, docs))
        return res


    def iv(self, value=None):
        # Is Value? - # menos líneas en la implementación de las clases.
        try:
            res = value.pyval
        except:
            msg = "\tWarning: no hay valor para %s" % (value,)
            print(msg)
            res = None
        assert isinstance(res, object)
        return res


    def tag_ns(self, elem):
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


class eDoc(EnvioCFEentreEmpresas):

    """
        Representa al elemento CFE del schema.
        Iimpementa un wrapper para uno de:
        eTck, eFact, eFact_Exp, eRem, eRem_Exp, eResg
    """

    def __init__(self, edoc, *args, **kargs):
        self.eDoc = edoc
        self.tag = self.tag_ns(edoc)
        if self.tag not in ('eTck', 'eFact', 'eFact_Exp', 'eRem', 'eRem_Exp', 'eResg'):
            msg = "ERROR: el tag %s es desconocido. Cancela." % (self.tag,)
            print(tag)
            sys.exit()


    def edoc_tmpl(self):
        res = dict()
        res.update(template.eDoc)
        for i in self.eDoc:
            if i is not None:
                tag =self.tag_ns(i)
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
        self.tag = self.tag_ns(elem)


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
        self.tag = self.tag_ns(elem)


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
        self.tag = self.tag_ns(elem)


class DscRecGlobal(eDoc):
    def __init__ (self, elem):
        self.elem = elem
        self.tag = self.tag_ns(elem)


class MrdiosPago(eDoc):
    def __init__ (self, elem):
        self.elem = elem
        self.tag = self.tag_ns(elem)


class Referencia(eDoc):
    def __init__ (self, elem):
        self.elem = elem
        self.tag = self.tag_ns(elem)


class CAEdata(eDoc):
    def __init__ (self, elem):
        self.elem = elem
        self.tag = self.tag_ns(elem)


class ComplFiscal(eDoc):
    def __init__ (self, elem):
        self.elem = elem
        self.tag = self.tag_ns(elem)
