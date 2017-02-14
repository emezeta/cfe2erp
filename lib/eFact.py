# -*- encoding: utf-8 -*-
#!/usr/bin/env python

from __future__ import print_function

import sys
import re
import subprocess
import json
from time import strftime
from lxml import etree, objectify
from lib import template, applib

from IPython import embed



__author__ = "emezeta"
__author_email__ = "emezeta@insiberia.net"
__copyright__ = "Copyright (C) 2017 eFacturaUy"
__license__ = "GPL 3.0"
__version__ = "0.99"


"""
    clases resuelven los diferentes elementos de un docu,eto de tipo eFact 111 al 114 (crep
"""



class Encabezado(object):

    def __init__(self, elem):
        self.elem = elem
        self.tag = applib.tag_ns(elem)

    def emisor(self):
        e = self.elem['Emisor']
        res = dict(
            CdgDGISucur  = e.CdgDGISucur.pyval,
            Ciudad       = e.Ciudad.pyval,
            Departamento = e.Departamento.pyval,
            DomFiscal    = e.DomFiscal.pyval,
            RUCEmisor    = e.RUCEmisor.pyval,
            RznSoc       = e.RznSoc.pyval
        )
        return res


    def iddoc(self):
        i = self.elem['IdDoc']
        res = dict(
            FchEmis = i.FchEmis.pyval ,
            # FchVenc = i.FchVenc.pyval , NO
            FmaPago = i.FmaPago.pyval ,
            Nro     = i.Nro.pyval     ,
            Serie   = i.Serie.pyval   ,
            TipoCFE = i.TipoCFE.pyval ,
        )
        return res


    def receptor(self):
        r = self.elem['Receptor']
        res = dict(
            CiudadRecep   = r.CiudadRecep.pyval  ,
            CodPaisRecep  = r.CodPaisRecep.pyval ,
            #CompraID      = r.CompraID.pyval     , no obligatorio
            #DeptoRecep    = r.DeptoRecep.pyval   , NO
            DirRecep      = r.DirRecep.pyval     ,
            DocRecep      = r.DocRecep.pyval     ,
            #PaisRecep     = r.PaisRecep.pyval    , NO
            RznSocRecep   = r.RznSocRecep.pyval  ,
            TipoDocRecep  = r.TipoDocRecep.pyval ,
        )
        return res
        # InfoAdicional = r.InfoAdicional, no obligatorio


    def totales(self):
        t = self.elem['Totales']
        res = dict(
            CantLinDet           = t.CantLinDet.pyval           ,
            IVATasaBasica        = t.IVATasaBasica.pyval        ,
            #MntIVATasaBasica     = t.MntIVATasaBasica.pyval     , NO
            #MntNetoIVATasaBasica = t.MntNetoIVATasaBasica.pyval , NO
            MntPagar             = t.MntPagar.pyval             ,
            MntTotal             = t.MntTotal.pyval             ,
            #MontoNF              = t.MontoNF.pyval                    , NO
        )
        return res


class Detalle(object):

    def __init__(self, elem):
        self.elem = elem
        self.tag = applib.tag_ns(elem)

    def cantidad(self):
        self.elem.Item.Cantidad

    def coditem(self):
        self.elem.Item.CodItem

    def descuentomonto(self):
        self.elem.Item.DescuentoMonto

    def descuentopct(self):
        self.elem.Item.DescuentoPct

    def indfact(self):
        self.elem.Item.IndFact

    def montoitem(self):
        self.elem.Item.MontoItem

    def nomitem(self):
        self.elem.Item.NomItem

    def nrolindet(self):
        self.elem.Item.NroLinDet

    def preciounitario(self):
        self.elem.Item.PrecioUnitario

    def unimed(self):
        self.elem.Item.UniMed



class CAEdata(object):
    def __init__(self, elem):
        self.elem = elem
        self.tag = applib.tag_ns(elem)



class SubTotInfo(object):
    def __init__(self, elem):
        self.elem = elem
        self.tag = applib.tag_ns(elem)



class Referencia(object):
    def __init__(self, elem):
        self.elem = elem
        self.tag = applib.tag_ns(elem)







