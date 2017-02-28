# coding: utf-8
# !/usr/bin/env python

from __future__ import print_function

import re
import sys
from dateutil import parser
from lxml import etree, objectify
import template

from IPython import embed

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
        #import ipdb; ipdb.set_trace()
        try:
            # with open(xmlfile, "r") as fxml:
            #    xmlstr = fxml.read().replace('&', '&amp;')
            # xml_doc = try_decode(xmlstr)
            xmldoc = etree.parse(xmlfile)
            self.xmldoc = xmldoc.getroot()
        except Exception as ex:
            msg = "El archivo xml %s no está disponible o no es un sobre xml `EnvioCFE_entreEmpresas` \n\t%s" % (xmlfile, ex)
            print(msg)
            sys.exit()

        cfe_ade = list()
        cartula = None
        res = {}
        for e in self.xmldoc.getchildren():
            tag = tag_ns(e)
            if tag == "Caratula":
                cartula = e
            elif tag == "CFE_Adenda":
                cfe_ade.append(e)
            else:
                msg = "ERROR: El tag o elemento %s no debería estar allí." % (e,)
                print(msg)
                sys.exit()
        self.caratula   = cartula
        self.cfe_adenda = cfe_ade



class Caratula(object):

    def __init__(self, caratula):
        """
            Crea el objeto Caratula a partir de un elemento etree lxml
            :param elemtree: Un elemeto Catatula.
            :return: Un objeto Caratula

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
        except:
            msg = "ERROR: La carátula no ha podido ser inicializada!"
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
            self.Adenda_py = adenda_obj.pyval
            self.Adenda_obj = adenda_obj.text
        else:
            msg = "ERROR: La Adenda del CFE no se ha encontrado."
            print(msg)



class Cfe(object):
    """
    Reprecentación del elemento CFE.
    ================================

    Usa un diccionarios inicializado a None.
    El diccionario contendrá uno de los siguiente tipos de CFEs:
        `eTck, eFact, eFact_Exp, eRem, eRem_Exp, eResg`
    """

    def __init__(self, cfe):
        """
        :param cfe:  es un único CFE
        :return:     un objeto python con todos los valores del CFE
        """


        self.edoc = cfe[0]
        self.signature = cfe[1]
        self.tmp  = template.eDoc

        res = dict()
        res.update(self.tmp)

        cfe_obj = objectify.fromstring(etree.tostring(self.edoc))
        tag = tag_ns(cfe_obj)

        if   tag == 'TmstFirma':
            res[tag] = cfe_obj.TmstFirma
        elif tag == 'Encabezado':
            res[tag] = cfe_obj.Encabezado()
        elif tag == 'Detalle':
            res[tag] = cfe_obj.Detalle()
        elif tag == 'SubTotInfo':
            res[tag] = cfe_obj.SubTotInfo()
        elif tag == 'DscRcgGlobal':
            res[tag] = cfe_obj.DscRcgGlobal()
        elif tag == 'MediosPago':
            res[tag] = cfe_obj.MediosPago()
        elif tag == 'CAEData':
            res[tag] = cfe_obj.CAEData()
        elif tag == 'Referencia':
            res[tag] = cfe_obj.Referencia()
        elif tag == 'Compl_Fiscal':
            res[tag] = cfe_obj.Compl_Fiscal()
        else:
            res['error'] = "Cancela, el elemento es desconocido : %s" % (tag,)
            print(res['error'])
            sys.exit()
        self.edoc = res
        # embed
        # import ipdb; ipdb.set_trace()
        # return res



class Encabezado(Cfe):

    def emisor(self):
        e = self.edoc['Emisor']
        res = dict(
            CdgDGISucur = iv(e.CdgDGISucur),
            Ciudad = iv(e.Ciudad),
            Departamento = iv(e.Departamento),
            DomFiscal = iv(e.DomFiscal),
            RUCEmisor = iv(e.RUCEmisor),
            RznSoc = iv(e.RznSoc),
        )
        return res


    def iddoc(self):
        i = self.edoc['IdDoc']
        res = dict(
            FchEmis = iv(i.FchEmis),
            FchVenc = iv(i.FchVenc),  # No Obligatorio
            FmaPago = iv(i.FmaPago),
            Nro     = iv(i.Nro),
            Serie   = iv(i.Serie),
            TipoCFE = iv(i.TipoCFE),
        )
        return res


    def receptor(self):
        r = self.edoc['Receptor']
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


    def totales(self):
        t = self.edoc['Totales']
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


class Detalle(Cfe):

    def __init__(self, elem):
        self.elem = elem
        self.tag = tag_ns(elem)
        super(Cfe, self).__init__()


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



class SubTotInfo(Cfe):
    def __init__(self, elem):
        self.elem = elem
        self.tag = tag_ns(elem)
        super(Cfe, self).__init__()



class DscRecGlobal(Cfe):
    def __init__(self, elem):
        self.elem = elem
        self.tag = tag_ns(elem)
        super(Cfe, self).__init__()



class MediosPago(Cfe):
    def __init__(self, elem):
        self.elem = elem
        self.tag = tag_ns(elem)
        super(Cfe, self).__init__()



class Referencia(Cfe):
    def __init__(self, elem):
        self.elem = elem
        self.tag = tag_ns(elem)
        super(Cfe, self).__init__()



class CAEdata(Cfe):
    def __init__(self, elem):
        self.elem = elem
        self.tag = tag_ns(elem)
        super(Cfe, self).__init__()



class ComplFiscal(Cfe):
    def __init__(self, elem):
        self.elem = elem
        self.tag = tag_ns(elem)
        super(Cfe, self).__init__()
