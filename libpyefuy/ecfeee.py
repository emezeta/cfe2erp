# coding: utf-8
# !/usr/bin/env python3
from __future__ import print_function

__author__ = "emezeta"
__author_email__ = "emezeta@insiberia.net"
__copyright__ = "Copyright (C) 2017 eFacturaUy"
__license__ = "GPL 3.0"
__version__ = "0.99"

import re
import sys
from dateutil import parser

from lxml import etree, objectify
from libpyefuy import config


prefix = re.compile('^{.*}')

"""
EnvioCFE_entreEmpresas
    Caratula
    CFE_Adenda
        CFE
            eFact
            Signature
        Adenda
"""
def tag_ns(elem):
    """
        elem: es un elemento, tiene un tag!
        elimina el {namespace} del tag de elem
    """
    try:
        _tag = elem.tag
    except Exception as ex:
        msg = "El elemento %s no tiene un tag. \n\tError: %s" % (elem, ex)
        print(msg)
        return False
    ns = prefix.match(_tag)
    if ns:
        tag = ns.string[ns.end():]
    else:
        tag = _tag
    return tag


def _dorp_none(self,tmp_val=None):

    if tmp_val is None: raise
    res = dict()
    for val in tmp_val:
        if tmp_val[val] is not None:
            res[val] = tmp_val[val]
    return res


def _str_none(self,tmp_val=None):

    if tmp_val is None: raise
    res = dict()
    for val in tmp_val:
        if tmp_val[val] is None:
            res[val] = 'None'
    return res



class XmlLoad(object):
    """
        Lee el archivo del xml y crea un arbol `lxml.etree`
    """

    def __init__(self, xmlfile=None):
        """
            :param: xmlfile: archivo xml contiene un Sobre ecee

            @self.xml_doc: es el root del lxml corresponsidente al Sobre
        """
        try:
            doc_root = etree.parse(xmlfile).getroot()
            if len(doc_root):
                self.xml_doc = doc_root
            else:
                msg = "Archivo %s no es un `EnvioCFE_entreEmpresas`" % (xmlfile)
                raise Exception("Error: %s" % (msg,))
                sys.exit()
        except Exception as ex:
            msg = "Archivo %s no disponible o no es un `EnvioCFE_entreEmpresas` \n\t%s" % (xmlfile, ex)
            print(msg)  # raise Exception("Error: %s" % (msg,))
            sys.exit()



class Caratula(object):

    """
        Crea el objeto Caratula a partir de un elemento etree lxml
        :param caratula: Elemeto lxml `Catatula`.
        :return: Objeto Caratula

        C.Fecha.pyval == '2016-01-27T18:10:09-03:00'
        # >>> Fecha = dateutil.parser.parse(C.Fecha.pyval)
        # >>> Fecha.strftime('%Y-%m-%d %H:%M:%S')
        ... 2016-11-11 18:10:09 ...etc
    """
    def __init__(self, caratula=None):

        if caratula is not None:
            C = objectify.fromstring(etree.tostring(caratula))
        else:
            print(u'La clase `Caratula` debe ser instanciada con el valor de `self.caratula` de la clase `EnvioCFE_entreEmpresas` como parámetro')
            sys.exit()
        try:
            self.CantCFE         = C.CantCFE.pyval
            self.Fecha           = parser.parse(C.Fecha.pyval)
            self.Idemisor        = C.Idemisor.pyval
            self.RUCEmisor       = C.RUCEmisor.pyval
            self.RutReceptor     = C.RutReceptor.pyval
            self.X509Certificate = C.X509Certificate.pyval
        except Exception as ex:
            _msg = u"ERROR: %s \n\tNo se ha podido inicializar la carátula!" % (ex,)
            print(_msg)
            sys.exit()  # raise Exception("Error: %s" % (msg,))



class CFE_Adenda(object):
    """
        Representa al elemento `CFE_Adenda`. Un CFE y su eventual Adenda.
        La instancia será una tupla de 2 elementos (cfe, adenda)
    """
    def __init__(self, elem_cfead=None):
        """
           :param elem_cfead:   El parámetro es un elemento con la estructura:
                                cfe   :
                                        elemento eDoc
                                        elemento Signature
                                Adenda:
                                        texto de la adenda o `None`
                                        (no obligatorio)

        """
        if elem_cfead is None:
            msg = u'La clase `CFE_Adenda` debe ser instanciada con el valor de `self.cfe_adenda` de la clase "EnvioCFE_entreEmpresas" como parámetro. Verificar xml de entrada'
            print(msg)
            sys.exit() # raise Exception("Error: %s" % (msg,))

        tag_cfe    = "{http://cfe.dgi.gub.uy}CFE"
        tag_adenda = "{http://cfe.dgi.gub.uy}Adenda"

        self._cfe     = elem_cfead.find(tag_cfe)
        self._adenda  = elem_cfead.find(tag_adenda)


    def CFE(self):
        """
        :return eDoc_obj

        @eDoc_obj:  Objeto a cuyos valores se accede mediante el operador punto (.)


        Estos son los objetos que componen cada CFE
            'TmstFirma', 'Encabezado', 'Detalle', 'SubTotInfo', 'DscRcgGlobal',
            'MediosPago', 'CAEData', 'Referencia', 'Compl_Fiscal'


        @Signature: es la eFirma del eDoc
        """

        if self._cfe is None:
            msg = u'El método `_CFE` debe recibir un elemento `CFE` (eDoc, Signature) como parámetro'
            print(msg) # raise Exception("El método `_CFE` debe recibir un elemento `CFE` (eDoc, Signature) como parámetro")
            sys.exit()

        eDoc_obj = dict( TmstFirma=None, Encabezado=None, Detalle=None,
                         SubTotInfo=None, DscRcgGlobal=None,
                         MediosPago=None, CAEData=None, Referencia=None,
                         Compl_Fiscal=None, Signature=None )

        eDoc_obj['Signature'] = self._cfe[1]
        """
            Note:
                Algunos elementos no son obligatorios 'n/o'. En aquellos CFE que no definan los n/o
                el objeto correpondiento no existirá. Para el caso de la salida CSV es necesario
                completar los valores necesarios con 'None'. Ejemplo. Descuento global.
                Asimismo para todos los sub_elementos de cada elemento analizado.
        """
        _edoc = self._cfe[0] # uno de {`eTck, eFact, eFact_Exp, eRem, eRem_Exp, eResg`}
        for edoc_child in _edoc.getchildren():
            echild_obj = objectify.fromstring(etree.tostring(edoc_child))
            tag = tag_ns(edoc_child)

            if   tag == 'TmstFirma':
                eDoc_obj[tag] = TmstFirma(echild_obj)
            elif tag == 'Encabezado':
                eDoc_obj[tag] = Encabezado(echild_obj)
            elif tag == 'Detalle':
                eDoc_obj[tag] = Detalle(echild_obj)
            elif tag == 'SubTotInfo':
                eDoc_obj[tag] = SubTotInfo(echild_obj)
            elif tag == 'DscRcgGlobal':
                eDoc_obj[tag] = DscRcgGlobal(echild_obj)
            elif tag == 'MediosPago':
                eDoc_obj[tag] = None #echild_obj
            elif tag == 'CAEData':
                eDoc_obj[tag] = None #echild_obj
            elif tag == 'Referencia':
                eDoc_obj[tag] = None #echild_obj
            elif tag == 'Compl_Fiscal':
                eDoc_obj[tag] = None #echild_obj
            else:
                raise Exception(u"Cancela, el elemento %s es desconocido o en CFE no es válido." % (tag,))

        return eDoc_obj


    def Adenda(self):

        res = 'None'
        if self._adenda is not None:
            tag = tag_ns(self._adenda)
            if tag == 'Adenda':
                adenda = objectify.fromstring(etree.tostring(self._adenda)).text
                if not adenda:
                    res = 'None'
                else:
                    res = adenda.replace(config.delimiter, '~') if len(adenda.strip())>1 else 'None'
        return res



class TmstFirma(object):

    def __init__(self, tmstfirma=None):

        if tmstfirma is None:
            msg = u'La clase `TmstFirma` debe ser instanciada con el valor de ' \
                  u'TmstFirma del objeto `CFE.eDoc`, clase `CFE_Adenda` como parámetro'
            print(msg)
            sys.exit() # raise Exception("Error: %s" % (msg,))
        else:
            self.tmstfirma = tmstfirma.text

# from IPython import embed; embed()
# import ipdb; ipdb.set_trace()



class Encabezado(object):

    def __init__(self, encab_obj):
        self._encabezado(encab_obj)

    def _encabezado(self,encab_obj):
        """
            Se inicializan todos los miembros del dict() de salida
        """
        e = encab_obj.Emisor
        tmp_emisor = dict(
            CdgDGISucur          = e.CdgDGISucur.pyval         if hasattr(e, 'CdgDGISucur'        ) else 'None',
            Ciudad               = e.Ciudad.pyval              if hasattr(e, 'Ciudad'             ) else 'None',
            Departamento         = e.Departamento.pyval        if hasattr(e, 'Departamento'       ) else 'None',
            DomFiscal            = e.DomFiscal.pyval           if hasattr(e, 'DomFiscal'          ) else 'None',
            RUCEmisor            = e.RUCEmisor.pyval           if hasattr(e, 'RUCEmisor'          ) else 'None',
            RznSoc               = e.RznSoc.pyval              if hasattr(e, 'RznSoc'             ) else 'None',
            NomComercial         = e.NomComercial.pyval        if hasattr(e, 'NomComercial'       ) else 'None',
            InfoAdicionalEmisor  = e.InfoAdicionalEmisor.pyval if hasattr(e, 'InfoAdicionalEmisor') else 'None',
            Telefono             = e.Telefono.pyval            if hasattr(e, 'Telefono'           ) else 'None',
            CorreoEmisor         = e.CorreoEmisor.pyval        if hasattr(e, 'CorreoEmisor'       ) else 'None',
            EmiSucursal          = e.EmiSucursal.pyval         if hasattr(e, 'EmiSucursal'        ) else 'None',
        )

        i = encab_obj.IdDoc
        tmp_iddoc = dict(
            FchEmis              = i.FchEmis.pyval              if hasattr(i,'FchEmis')             else 'None',
            FchVenc              = i.FchVenc.pyval              if hasattr(i,'FchVenc')             else 'None',
            FmaPago              = i.FmaPago.pyval              if hasattr(i,'FmaPago')             else 'None',
            Nro                  = i.Nro.pyval                  if hasattr(i,'Nro'    )             else 'None',
            Serie                = i.Serie.pyval                if hasattr(i,'Serie'  )             else 'None',
            TipoCFE              = i.TipoCFE.pyval              if hasattr(i,'TipoCFE')             else 'None',
        )

        r = encab_obj.Receptor
        tmp_receptor = dict(
            CiudadRecep          = r.CiudadRecep.pyval          if hasattr(r, 'CiudadRecep'         ) else 'None',
            CodPaisRecep         = r.CodPaisRecep.pyval         if hasattr(r, 'CodPaisRecep'        ) else 'None',
            CompraID             = r.CompraID.pyval             if hasattr(r, 'CompraID'            ) else 'None',
            DeptoRecep           = r.DeptoRecep.pyval           if hasattr(r, 'DeptoRecep'          ) else 'None',
            DirRecep             = r.DirRecep.pyval             if hasattr(r, 'DirRecep'            ) else 'None',
            DocRecep             = r.DocRecep.pyval             if hasattr(r, 'DocRecep'            ) else 'None',
            PaisRecep            = r.PaisRecep.pyval            if hasattr(r, 'PaisRecep'           ) else 'None',
            RznSocRecep          = r.RznSocRecep.pyval          if hasattr(r, 'RznSocRecep'         ) else 'None',
            TipoDocRecep         = r.TipoDocRecep.pyval         if hasattr(r, 'TipoDocRecep'        ) else 'None',
            InfoAdicional        = r.InfoAdicional.pyval        if hasattr(r, 'InfoAdicional'       ) else 'None',
            CP                   = r.CP.pyval                   if hasattr(r, 'CP'                  ) else 'None',
        )

        t = encab_obj.Totales

        tmp_totales = dict(
            CantLinDet           = t.CantLinDet.pyval                 if hasattr(t, 'CantLinDet'          ) else 'None',
            TpoMoneda            = t.TpoMoneda.pyval                  if hasattr(t, 'TpoMoneda'           ) else 'None',
            TpoCambio            = t.TpoCambio.pyval                  if hasattr(t, 'TpoCambio'           ) else 'None',
            MntNoGrv             = t.MntNoGrv.pyval                   if hasattr(t, 'MntNoGrv'            ) else 'None',
            MntExpoyAsim         = t.MntExpoyAsim.pyval               if hasattr(t, 'MntExpoyAsim'        ) else 'None',
            MntImpuestoPerc      = t.MntImpuestoPerc.pyval            if hasattr(t, 'MntImpuestoPerc'     ) else 'None',
            MntIVaenSusp         = t.MntIVaenSusp.pyval               if hasattr(t, 'MntIVaenSusp'        ) else 'None',
            IVATasaMin           = t.IVATasaMin.pyval                 if hasattr(t, 'IVATasaMin'          ) else 'None',
            IVATasaBasica        = t.IVATasaBasica.pyval              if hasattr(t, 'IVATasaBasica'       ) else 'None',
            MntIVATasaMin        = t.MntIVATasaMin.pyval              if hasattr(t, 'MntIVATasaMin'       ) else 'None',
            MntIVATasaBasica     = t.MntIVATasaBasica.pyval           if hasattr(t, 'MntIVATasaBasica'    ) else 'None',
            MntIVAOtra           = t.MntIVAOtra.pyval                 if hasattr(t, 'MntIVAOtra'          ) else 'None',
            MntNetoIvaTasaMin    = t.MntNetoIvaTasaMin.pyval          if hasattr(t, 'MntNetoIvaTasaMin'   ) else 'None',
            MntNetoIVATasaBasica = t.MntNetoIVATasaBasica.pyval       if hasattr(t, 'MntNetoIVATasaBasica') else 'None',
            MntNetoIVAOtra       = t.MntNetoIVAOtra.pyval             if hasattr(t, 'MntNetoIVAOtra'      ) else 'None',
            MntTotal             = t.MntTotal.pyval                   if hasattr(t, 'MntTotal'            ) else 'None',
            MntTotRetenido       = t.MntTotRetenido.pyval             if hasattr(t, 'MntTotRetenido'      ) else 'None',
            MontoNF              = t.MontoNF.pyval                    if hasattr(t, 'MontoNF'             ) else 'None',
            MntPagar             = t.MntPagar.pyval                   if hasattr(t, 'MntPagar'            ) else 'None',
        )
        if tmp_totales['TpoMoneda'] == 'UYU':
            tmp_totales['TpoCambio'] = 1.0

        self.Encabezado = dict(
            Emisor=tmp_emisor, IdDoc=tmp_iddoc, Receptor=tmp_receptor, Totales=tmp_totales
        )


class Detalle(object):

    def __init__(self, detalle):
        self._detalle(detalle)

    def _detalle(self, detalle):
        detalle_lineas = list()
        for i in detalle.getchildren():

            tmp_item = dict(
                NroLinDet       = i.NroLinDet.pyval       if hasattr(i,'NroLinDet'     ) else 'None',
                IndFact         = i.IndFact.pyval         if hasattr(i,'IndFact'       ) else 'None',
                CodItem         = i.CodItem               if hasattr(i,'CodItem'       ) else 'None',
                NomItem         = i.NomItem.pyval         if hasattr(i,'NomItem'       ) else 'None',
                Cantidad        = i.Cantidad.pyval        if hasattr(i,'Cantidad'      ) else 'None',
                UniMed          = i.UniMed.pyval          if hasattr(i,'UniMed'        ) else 'None',
                DscItem         = i.DscItem.pyval         if hasattr(i,'DscItem') and i.DscItem is not '0' else 'None',  # Descripción
                PrecioUnitario  = i.PrecioUnitario.pyval  if hasattr(i,'PrecioUnitario') else 'None',
                MontoItem       = i.MontoItem.pyval       if hasattr(i,'MontoItem'     ) else 'None',
                SubDescuento    = i.SubDescuento          if hasattr(i,'SubDescuento'  ) else 'None',
                DescuentoMonto  = i.DescuentoMonto.pyval  if hasattr(i,'DescuentoMonto') else 'None',
                DescuentoPct    = i.DescuentoPct.pyval    if hasattr(i,'DescuentoPct'  ) else 'None',
            )

            if tmp_item['CodItem'] is not 'None':
                tmp_item['CodItem'] = [{'TpoCod': cdi.TpoCod.pyval, 'Cod': cdi.Cod.pyval} for cdi in tmp_item['CodItem']]

            if tmp_item['SubDescuento'] is not 'None':
                # DescTipo [ 1 = $ o 2 = % ]
                tmp_item['SubDescuento'] = [ { 'DescTipo': '$' if sdto.DescTipo.pyval == 1 else '%',
                                               'DescVal' : sdto.DescVal.pyval } for sdto in tmp_item['SubDescuento']
                                                   if sdto['DescVal'].pyval is not 0 ]
            if tmp_item['IndFact'] is not 'None':
                tmp_item['IndFact'] = indfact[str(tmp_item['IndFact'])]

            detalle_lineas.append(tmp_item)
        
        self.Detalle = detalle_lineas



class DscRcgGlobal(object):

    def __init__(self, dscrcgglobal):
        self._dscrcgglobal(dscrcgglobal)

    def _dscrcgglobal(self, dscrcgglobal):
        drg_items = list()
        if hasattr(dscrcgglobal,'DRG_Item') and len(dscrcgglobal.DRG_Item):
            for drgi in dscrcgglobal.DRG_Item:
                tmp_drgitem = dict(
                    TpoMovDR    =  drgi.TpoMovDR.pyval  if hasattr(drgi,'TpoMovDR'  ) else 'None',
                    TpoDR       =  drgi.TpoDR.pyval     if hasattr(drgi,'TpoDR'     ) else 'None',
                        GlosaDR     =  drgi.GlosaDR.pyval   if hasattr(drgi,'GlosaDR'   ) else 'None',
                        ValorDR     =  drgi.ValorDR.pyval   if hasattr(drgi,'ValorDR'   ) else 'None',
                        IndFactDR   =  drgi.IndFactDR.pyval if hasattr(drgi,'IndFactDR' ) else 'None'   # ver tabla  "indfactdr"
                )
                if tmp_drgitem['ValorDR'] is not 'None':
                    tmp_drgitem['TpoDR'] = "%" if tmp_drgitem['TpoDR'] == 1 else '$'
                    if tmp_drgitem['IndFactDR'] is not 'None':
                        tmp_drgitem['IndFactDR'] = indfactdr[str(tmp_drgitem['IndFactDR'])]

                    drg_items.append(tmp_drgitem)

        self.Items = drg_items or []

    """
        Se eleiminaron estos dos elementos.
            NroLinDR    =  drgi.NroLinDR       if hasattr(drgi,'NroLinDR'  ) else 'None', # sin función útil
            CodDR       =  drgi.CodDR          if hasattr(drgi,'CodDR'     ) else 'None', # sin función útil
    """


class SubTotInfo(object):

    def __init__(self, elem):
        if tag_ns(elem) not in "SubTotInfo":
            print(u'La clase `SubTotInfo` debe ser instanciada con un elemento `SubTotInfo`, sin embargo se encontró %s' % (elem,))
            sys.exit()
        self._subtotinfo(elem)


    def _subtotinfo(self, elem):
        sti_items = list()

        if hasattr(elem,'STI_Item') and len(elem.STI_Item):
            for sti in elem.STI_Item:
                tmp_stiitem = dict(
                        NroSTI       =  sti.NroSTI       if hasattr(sti,'NroSTI'      ) else 'None',
                        GlosaSTI     =  sti.GlosaSTI     if hasattr(sti,'GlosaSTI'    ) else 'None',
                        OrdenSTI     =  sti.OrdenSTI     if hasattr(sti,'OrdenSTI'    ) else 'None',
                        ValSubtotSTI =  sti.ValSubtotSTI if hasattr(sti,'ValSubtotSTI') else 'None'
                )
                sti_items.append(tmp_stiitem)

        self.Items = sti_items or []


indfact = indfactdr = \
    {
         '1': u'Exento de IVA',
         '2': u'Gravado a Tasa Mínima',
         '3': u'Gravado a Tasa Básica',
         '4': u'Gravado a Otra Tasa',
         '5': u'Entrega Gratuita',
         '6': u'Prod/Serv no facturable',
         '7': u'Prod/Serv no facturable negativo',
         '8': u'Ítem a rebajar(remito)',
         '9': u'Ítem a ajustar(resgdo)',
        '10': u'Exportación y asimiladas',
        '11': u'Impuesto percibido',
        '12': u'IVA en suspenso',
    }

"""
Indicador de Facturación:
 1: Exento de IVA
 2: Gravado a Tasa Mínima
 3: Gravado a Tasa Básica
 4: Gravado a Otra Tasa
 5: Entrega Gratuita
 6: Producto o servicio no facturable
 7: Producto o servicio no facturable negativo
 8: Solo para remitos: Ítem a rebajar en remitos. En área de referencia se debe indicar el N° de remito que ajusta
 9: Solo para resguardos: Ítem a ajustar en resguardos. En área de referencia se debe indicar el N° de remito que ajusta
10: Exportación y asimiladas
11: Impuesto percibido
12: IVA en suspenso
"""



"""
    def _coditem(self,coditem=None):
        res = list()
        if coditem is None:
            return None
        else:
            for cdi in coditem:
                res.append(cdi)
        return res

    def _sub_descuento(self,sub_descuento):

        res = list()
        if sub_descuento is not None:
            for sdto in sub_descuento:
                res.append(sdto)
        return res


        self.Detalle = dict(
                Item = tmp_item
        )

class SubTotInfo(eDoc):
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


