# coding: utf-8
# !/usr/bin/env python3
from __future__ import print_function

__author__ = "emezeta"
__author_email__ = "emezeta@insiberia.net"
__copyright__ = "Copyright (C) 2017 eFacturaUy"
__license__ = "GPL v3.0"
__version__ = "0.99"

import sys
import re
from dateutil import parser
from lxml import etree, objectify
from libpyefuy import config


prefix = re.compile('^{.*}')

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


def tag_ns(elem):
    """
        elimina el {namespace} del tag de elem
        :elem: es un elemento, tiene un tag!
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

    if tmp_val is None:
        raise
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
                #sys.exit()
        except Exception as ex:
            msg = "Archivo %s no disponible o no es un `EnvioCFE_entreEmpresas` \n\t%s" % (xmlfile, ex)
            print(msg)  # raise Exception("Error: %s" % (msg,))
            sys.exit()


"""
    EnvioCFE_entreEmpresas.xsd (del schema DGI v.1.36

        Caratula
        CFE_Adenda
            CFE
                eDoc (*)
                Signature
            Adenda

    (*)En realidad será uno de éstos:
    `eTck`, `eFact`, `eFact_Exp`, `eRem`, `eRem_Exp` y `eResg`
    Ver "template.doc" en esta misma carpeta.
"""


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
            'MediosPago', 'CAEData', 'Referencia', 'Compl_Fiscal', 'Signature'

        @Signature: es la eFirma del eDoc (actualmente no se realizan verificaciones WSE)
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



class Encabezado(object):

    def __init__(self, encab_obj):
        self._encabezado(encab_obj)

    def _encabezado(self,encab_obj):
        """
            Se inicializan todos los miembros del dict() de salida
        """

        o = encab_obj.Emisor
        tmp_emisor = dict(
            CdgDGISucur          = o.CdgDGISucur.pyval         if hasattr(o, 'CdgDGISucur'        ) else 'None',
            Ciudad               = o.Ciudad.pyval              if hasattr(o, 'Ciudad'             ) else 'None',
            Departamento         = o.Departamento.pyval        if hasattr(o, 'Departamento'       ) else 'None',
            DomFiscal            = o.DomFiscal.pyval           if hasattr(o, 'DomFiscal'          ) else 'None',
            RUCEmisor            = o.RUCEmisor.pyval           if hasattr(o, 'RUCEmisor'          ) else 'None',
            RznSoc               = o.RznSoc.pyval              if hasattr(o, 'RznSoc'             ) else 'None',
            NomComercial         = o.NomComercial.pyval        if hasattr(o, 'NomComercial'       ) else 'None',
            InfoAdicionalEmisor  = o.InfoAdicionalEmisor.pyval if hasattr(o, 'InfoAdicionalEmisor') else 'None',
            Telefono             = o.Telefono.pyval            if hasattr(o, 'Telefono'           ) else 'None',
            CorreoEmisor         = o.CorreoEmisor.pyval        if hasattr(o, 'CorreoEmisor'       ) else 'None',
            EmiSucursal          = o.EmiSucursal.pyval         if hasattr(o, 'EmiSucursal'        ) else 'None',
        )
        tmp_emisor = self._none(tmp_emisor)

        o = encab_obj.IdDoc
        tmp_iddoc = dict(
            FchEmis              = o.FchEmis.pyval              if hasattr(o,'FchEmis' )             else 'None',
            FchVenc              = o.FchVenc.pyval              if hasattr(o,'FchVenc' )             else 'None',
            FmaPago              = o.FmaPago.pyval              if hasattr(o,'FmaPago' )             else 'None',
            Nro                  = o.Nro.pyval                  if hasattr(o,'Nro'     )             else 'None',
            Serie                = o.Serie.pyval                if hasattr(o,'Serie'   )             else 'None',
            TipoCFE              = o.TipoCFE.pyval              if hasattr(o,'TipoCFE' )             else 'None',
            MntBruto             = o.MntBruto.pyval             if hasattr(o,'MntBruto')             else 'None'
        )
        tmp_iddoc = self._none(tmp_iddoc)

        o = encab_obj.Receptor
        tmp_receptor = dict(
            CiudadRecep          = o.CiudadRecep.pyval          if hasattr(o, 'CiudadRecep'         ) else 'None',
            CodPaisRecep         = o.CodPaisRecep.pyval         if hasattr(o, 'CodPaisRecep'        ) else 'None',
            CompraID             = o.CompraID.pyval             if hasattr(o, 'CompraID'            ) else 'None',
            DeptoRecep           = o.DeptoRecep.pyval           if hasattr(o, 'DeptoRecep'          ) else 'None',
            DirRecep             = o.DirRecep.pyval             if hasattr(o, 'DirRecep'            ) else 'None',
            DocRecep             = o.DocRecep.pyval             if hasattr(o, 'DocRecep'            ) else 'None',
            PaisRecep            = o.PaisRecep.pyval            if hasattr(o, 'PaisRecep'           ) else 'None',
            RznSocRecep          = o.RznSocRecep.pyval          if hasattr(o, 'RznSocRecep'         ) else 'None',
            TipoDocRecep         = o.TipoDocRecep.pyval         if hasattr(o, 'TipoDocRecep'        ) else 'None',
            InfoAdicional        = o.InfoAdicional.pyval        if hasattr(o, 'InfoAdicional'       ) else 'None',
            CP                   = o.CP.pyval                   if hasattr(o, 'CP'                  ) else 'None',
        )
        tmp_receptor = self._none(tmp_receptor)

        o = encab_obj.Totales
        tmp_totales = dict(
            CantLinDet           = o.CantLinDet.pyval                 if hasattr(o, 'CantLinDet'          ) else 'None',
            TpoMoneda            = o.TpoMoneda.pyval                  if hasattr(o, 'TpoMoneda'           ) else 'None',
            TpoCambio            = o.TpoCambio.pyval                  if hasattr(o, 'TpoCambio'           ) else 'None',
            MntNoGrv             = o.MntNoGrv.pyval                   if hasattr(o, 'MntNoGrv'            ) else 'None',
            MntExpoyAsim         = o.MntExpoyAsim.pyval               if hasattr(o, 'MntExpoyAsim'        ) else 'None',
            MntImpuestoPerc      = o.MntImpuestoPerc.pyval            if hasattr(o, 'MntImpuestoPerc'     ) else 'None',
            MntIVaenSusp         = o.MntIVaenSusp.pyval               if hasattr(o, 'MntIVaenSusp'        ) else 'None',
            IVATasaMin           = o.IVATasaMin.pyval                 if hasattr(o, 'IVATasaMin'          ) else 'None',
            IVATasaBasica        = o.IVATasaBasica.pyval              if hasattr(o, 'IVATasaBasica'       ) else 'None',
            MntIVATasaMin        = o.MntIVATasaMin.pyval              if hasattr(o, 'MntIVATasaMin'       ) else 'None',
            MntIVATasaBasica     = o.MntIVATasaBasica.pyval           if hasattr(o, 'MntIVATasaBasica'    ) else 'None',
            MntIVAOtra           = o.MntIVAOtra.pyval                 if hasattr(o, 'MntIVAOtra'          ) else 'None',
            MntNetoIvaTasaMin    = o.MntNetoIvaTasaMin.pyval          if hasattr(o, 'MntNetoIvaTasaMin'   ) else 'None',
            MntNetoIVATasaBasica = o.MntNetoIVATasaBasica.pyval       if hasattr(o, 'MntNetoIVATasaBasica') else 'None',
            MntNetoIVAOtra       = o.MntNetoIVAOtra.pyval             if hasattr(o, 'MntNetoIVAOtra'      ) else 'None',
            MntTotal             = o.MntTotal.pyval                   if hasattr(o, 'MntTotal'            ) else 'None',
            MntTotRetenido       = o.MntTotRetenido.pyval             if hasattr(o, 'MntTotRetenido'      ) else 'None',
            MontoNF              = o.MontoNF.pyval                    if hasattr(o, 'MontoNF'             ) else 'None',
            MntPagar             = o.MntPagar.pyval                   if hasattr(o, 'MntPagar'            ) else 'None',
        )
        if tmp_totales['TpoMoneda'] == 'UYU':
            tmp_totales['TpoCambio'] = 1.0

        self.Encabezado = dict(
            Emisor=tmp_emisor, IdDoc=tmp_iddoc, Receptor=tmp_receptor, Totales=tmp_totales
        )


    def _none(self, args):
        if len(args) < 1:
            return False
        for tmp in args:
            if isinstance(args[tmp], (str,unicode)):
                if len( args[tmp].encode('utf8') ) < 1:
                    args[tmp] = 'None'
        return args


class Detalle(object):

    def __init__(self, detalle):
        self._detalle(detalle)

    def _detalle(self, detalle):
        detalle_lineas = list()
        for o in detalle.getchildren():

            tmp_item = dict(
                NroLinDet       = o.NroLinDet.pyval       if hasattr(o,'NroLinDet'     ) else 'None',
                IndFact         = o.IndFact.pyval         if hasattr(o,'IndFact'       ) else 'None',
                CodItem         = o.CodItem               if hasattr(o,'CodItem'       ) else 'None',
                NomItem         = o.NomItem.pyval         if hasattr(o,'NomItem'       ) else 'None',
                Cantidad        = o.Cantidad.pyval        if hasattr(o,'Cantidad'      ) else 'None',
                UniMed          = o.UniMed.pyval          if hasattr(o,'UniMed'        ) else 'None',
                DscItem         = o.DscItem.pyval         if hasattr(o,'DscItem') and o.DscItem is not '0' else 'None',  # Descripción
                PrecioUnitario  = o.PrecioUnitario.pyval  if hasattr(o,'PrecioUnitario') else 'None',
                MontoItem       = o.MontoItem.pyval       if hasattr(o,'MontoItem'     ) else 'None',
                SubDescuento    = o.SubDescuento          if hasattr(o,'SubDescuento'  ) else 'None',
                DescuentoMonto  = o.DescuentoMonto.pyval  if hasattr(o,'DescuentoMonto') else 'None',
                DescuentoPct    = o.DescuentoPct.pyval    if hasattr(o,'DescuentoPct'  ) else 'None',
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


