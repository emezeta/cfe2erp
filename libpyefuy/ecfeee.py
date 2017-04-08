# coding: utf-8
# !/usr/bin/env python3

from __future__ import print_function
import re
import sys
from dateutil import parser

from lxml import etree, objectify

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



class EnvioCFE_entreEmpresas(object):
    """
        Parsea el contenido del xml y crea un arbol `lxml.etree`
        Luego almacena la `Caratula` en la variable de clase `caratula`
        y la lista de CFE_Adenda(s) en `cfe_adenda`
    """

    def __init__(self, xmlfile=None):
        """
            :param: xmlfile: archivo xml contiene un Sobre ecee

            @caratula:  Elemento `etree` único.
            @cfe_adenda: Lista de elementos etree, mín. 1, máx. 250
        """

        if xmlfile is not None:
            self.xmlfile = xmlfile
            try:
                xmldoc = etree.parse(xmlfile)
                xmldoc = xmldoc.getroot()
            except Exception as ex:
                msg = "Archivo %s no disponible o no es un `EnvioCFE_entreEmpresas` \n\t%s" % (xmlfile, ex)
                print(msg)  # raise Exception("Error: %s" % (msg,))
                sys.exit()

            self.cfe_adenda = list()
            for elem in xmldoc.getchildren():
                tag = tag_ns(elem)
                if tag == "Caratula":
                    self.caratula = elem
                elif tag == "CFE_Adenda":
                    self.cfe_adenda.append(elem)
                else:
                    msg = "ERROR: El tag o elemento %s no debería estar allí." % (elem,)
                    print(msg)
                    sys.exit()  # raise Exception("Error: %s" % (msg,))



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
            print('La clase `Caratula` debe ser instanciada con el valor de `self.caratula` de la clase `EnvioCFE_entreEmpresas` como parámetro')
            sys.exit()
        try:
            self.CantCFE         = C.CantCFE.pyval
            self.Fecha           = parser.parse(C.Fecha.pyval)
            self.Idemisor        = C.Idemisor.pyval
            self.RUCEmisor       = C.RUCEmisor.pyval
            self.RutReceptor     = C.RutReceptor.pyval
            self.X509Certificate = C.X509Certificate.pyval
        except Exception as ex:
            _msg = "ERROR: %s \n\tNo se ha podido inicializar la carátula!" % (ex,)
            print(_msg)
            sys.exit()  # raise Exception("Error: %s" % (msg,))



class CFE_Adenda(object):
    """
    xml = <CFE_Adenda>
                <CFE>
                    <eDoc/> *** uno de {`eTck, eFact, eFact_Exp, eRem, eRem_Exp, eResg`} ***
                    <Signature/>
                </CFE>
                <Adenda/>      *** no obligatorio ***
          <CFE_Adenda/>

        La instancia creará un lista de diccionarios. El largo de la lista será entre 1 y 250
        Cada diccionario contiene 2 elementos y será de la forma:
            CFE_Adenda =  {   cfe: ( {elementos del eDoc, ...}, elemento Signature ),
                           Adenda: "texto de la adenda"
            }
    """
    def __init__(self, cfe_adenda=None):
        """
           :param cfe_adenda:   lista `CFE_Adenda`(s) de elementos del sobre
                                cada elemento sería <CFE, Adenda*> *si existe adenda
                                mín. 1, máx. 250 elementos en la lista (en general es 1)
        """
        if cfe_adenda is None:
            msg = 'La clase `CFE_Adenda` debe ser instanciada con el valor de `self.cfe_adenda` de la clase "EnvioCFE_entreEmpresas" como parámetro. Verificar xml de entrada'
            print(msg)
            sys.exit() # raise Exception("Error: %s" % (msg,))

        self.cfead = list()

        for elem in cfe_adenda:                    # [cfe_adenda, ...] 1 a 250, en general es 1
            _cfe    = None
            _adenda = None
            for child_elem in elem.getchildren():  # [cfe, adenda]  o [cfe]
                tag = tag_ns(child_elem)
                if   tag == "CFE":
                    _cfe    = self._CFE(child_elem)        # child_elem [ eDoc, Signature ]
                elif tag == "Adenda":
                    _adenda = self._Adenda(child_elem)     # child_elem [ Adenda ]
                else:
                    msg = "ERROR: El tag o elemento %s no debería estar allí." % (child_elem,)
                    print(msg)
                    sys.exit() # raise Exception("Cancela, el elemento es desconocido : %s" % (tag,))
            self.cfead.append( dict(cfe=_cfe, adenda=_adenda) )



    def _CFE(self, cfe=None):
        """
        :param cfe:    cfe [eDoc, Signature]
        :return eDoc_obj

        @eDoc_obj:  Objeto a cuyos valores se accede mediante el operador punto (.)
                    ejemplo: edoc.Encabezado
        @Signature: es la eFirma del eDoc
        """

        if cfe is None:
            msg = 'El método `_CFE` debe recibir un elemento `CFE` (eDoc, Signature) como parámetro'
            print(msg) # raise Exception("El método `_CFE` debe recibir un elemento `CFE` (eDoc, Signature) como parámetro")
            sys.exit()

        _edoc = cfe[0]  # uno de {`eTck, eFact, eFact_Exp, eRem, eRem_Exp, eResg`}
        eDoc_obj = dict()
        eDoc_obj['Signature'] = cfe[1]

        elementos = ['TmstFirma', 'Encabezado', 'Detalle', 'SubTotInfo', 'DscRcgGlobal', 'MediosPago', 'CAEData', 'Referencia', 'Compl_Fiscal']



        for edoc_child in _edoc.getchildren():
            echild_obj = objectify.fromstring(etree.tostring(edoc_child))
            tag = tag_ns(edoc_child)
            """
                Formalmente este switch no es estricatamente innecesario.
                Alcanzaba con:
                    `eDoc_obj[tag] = echild_obj`
                Su existencia simplifica tareas de debug t/o mantenimientos
                y permite pasar un llamado a función diferente para
                diferentes elementos.

                Notese:
                    Algunos elementos no son obligatorios 'n/o'. En aquellos CFE que no definan los n/o
                    el objeto correpondiento no existirá. Para el caso de la salida CSV es necesario
                    completar los valores necesarios con 'None'. Ejemplo. Descuento global.

            """
            if   tag == 'TmstFirma':
                eDoc_obj[tag] = TmstFirma(echild_obj)
            elif tag == 'Encabezado':
                eDoc_obj[tag] = Encabezado(echild_obj)
            elif tag == 'Detalle':
                eDoc_obj[tag] = Detalle(echild_obj)
            elif tag == 'SubTotInfo':
                eDoc_obj[tag] = echild_obj
            elif tag == 'DscRcgGlobal':
                eDoc_obj[tag] = DscRcgGlobal(echild_obj) # n/o   dscrcgglobal
            elif tag == 'MediosPago':
                eDoc_obj[tag] = echild_obj
            elif tag == 'CAEData':
                eDoc_obj[tag] = echild_obj
            elif tag == 'Referencia':
                eDoc_obj[tag] = echild_obj
            elif tag == 'Compl_Fiscal':
                eDoc_obj[tag] = echild_obj
            else:
                raise Exception("Cancela, el elemento  %s es desconocido o en CFE no es válido." % (tag,))

        return eDoc_obj



    def _Adenda(self, adenda=None):

        """
            :param adenda: etree/CFE_Adenda/Adenda
            :return: texto adenda
        """
        res = "n/a"
        if adenda is not None:
            tag = tag_ns(adenda)
            if tag == 'Adenda':
                res = objectify.fromstring(etree.tostring(adenda)).text
        return res



class TmstFirma(object):

    def __init__(self, tmstfirma=None):

        if tmstfirma is None:
            msg = 'La clase `TmstFirma` debe ser instanciada con el valor de ' \
                  'TmstFirma del objeto `CFE.eDoc`, clase `CFE_Adenda` como parámetro'
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
            CantLinDet           = t.CantLinDet                 if hasattr(t, 'CantLinDet'          ) else 'None',
            TpoMoneda            = t.TpoMoneda                  if hasattr(t, 'TpoMoneda'           ) else 'None',
            TpoCambio            = t.TpoCambio                  if hasattr(t, 'TpoCambio'           ) else 'None',
            MntNoGrv             = t.MntNoGrv                   if hasattr(t, 'MntNoGrv'            ) else 'None',
            MntExpoyAsim         = t.MntExpoyAsim               if hasattr(t, 'MntExpoyAsim'        ) else 'None',
            MntImpuestoPerc      = t.MntImpuestoPerc            if hasattr(t, 'MntImpuestoPerc'     ) else 'None',
            MntIVaenSusp         = t.MntIVaenSusp               if hasattr(t, 'MntIVaenSusp'        ) else 'None',
            IVATasaMin           = t.IVATasaMin                 if hasattr(t, 'IVATasaMin'          ) else 'None',
            IVATasaBasica        = t.IVATasaBasica              if hasattr(t, 'IVATasaBasica'       ) else 'None',
            MntIVATasaMin        = t.MntIVATasaMin              if hasattr(t, 'MntIVATasaMin'       ) else 'None',
            MntIVATasaBasica     = t.MntIVATasaBasica           if hasattr(t, 'MntIVATasaBasica'    ) else 'None',
            MntIVAOtra           = t.MntIVAOtra                 if hasattr(t, 'MntIVAOtra'          ) else 'None',
            MntNetoIvaTasaMin    = t.MntNetoIvaTasaMin          if hasattr(t, 'MntNetoIvaTasaMin'   ) else 'None',
            MntNetoIVATasaBasica = t.MntNetoIVATasaBasica       if hasattr(t, 'MntNetoIVATasaBasica') else 'None',
            MntNetoIVAOtra       = t.MntNetoIVAOtra             if hasattr(t, 'MntNetoIVAOtra'      ) else 'None',
            MntTotal             = t.MntTotal                   if hasattr(t, 'MntTotal'            ) else 'None',
            MntTotRetenido       = t.MntTotRetenido             if hasattr(t, 'MntTotRetenido'      ) else 'None',
            MontoNF              = t.MontoNF                    if hasattr(t, 'MontoNF'             ) else 'None',
            MntPagar             = t.MntPagar                   if hasattr(t, 'MntPagar'            ) else 'None',
        )

        self.Encabezado = dict(
            Emisor = tmp_emisor, IdDoc = tmp_iddoc, Receptor = tmp_receptor, Totales = tmp_totales
        )


class Detalle(object):

    def __init__(self, detalle):
        self._detalle(detalle)

    def _detalle(self, detalle):
        i = detalle.Item
        tmp_item = dict(
            NroLinDet       = i.NroLinDet       if hasattr(i,'NroLinDet'     ) else 'None',
            IndFact         = i.IndFact         if hasattr(i,'IndFact'       ) else 'None',
            CodItem         = i.CodItem         if hasattr(i,'CodItem'       ) else 'None',
            NomItem         = i.NomItem         if hasattr(i,'NomItem'       ) else 'None',
            Cantidad        = i.Cantidad        if hasattr(i,'Cantidad'      ) else 'None',
            UniMed          = i.UniMed          if hasattr(i,'UniMed'        ) else 'None',
            DscItem         = i.DscItem         if hasattr(i,'DscItem'       ) else 'None',  # Descripción
            PrecioUnitario  = i.PrecioUnitario  if hasattr(i,'PrecioUnitario') else 'None',
            MontoItem       = i.MontoItem       if hasattr(i,'MontoItem'     ) else 'None',
            SubDescuento    = i.SubDescuento    if hasattr(i,'SubDescuento'  ) else 'None',
            DescuentoMonto  = i.DescuentoMonto  if hasattr(i,'DescuentoMonto') else 'None',
            DescuentoPct    = i.DescuentoPct    if hasattr(i,'DescuentoPct'  ) else 'None',
        )

        if tmp_item['CodItem'] is not 'None':
            tmp_item['CodItem'] = [cdi for cdi in tmp_item['CodItem']]

        if tmp_item['SubDescuento'] is not 'None':
            tmp_item['SubDescuento'] = [{'DescTipo': sdto.DescTipo , 'DescVal':sdto.DescVal} for sdto in tmp_item['SubDescuento']]

        self.Detalle = tmp_item



class DscRcgGlobal(object):

    def __init__(self, dscrcgglobal):
        self.DscRcgGlobal = ('None','None','None')
        self.drg_item_wrap(dscrcgglobal)

    def drg_item_wrap(self,dscrcgglobal):

        if hasattr(dscrcgglobal,'DRG_Item'):
            dtos = [self._dscrcgglobal(drgi) for drgi in dscrcgglobal.DRG_Item]
            i = dtos[0]
            valor =  i['ValorDR']
            deta  =  "Tasa/Valor: %s - Dto/Rec: %s - Concepto: %s - Tipo: %s" % (i['TpoDR'],i['TpoMovDR'],i['GlosaDR'],i['IndFactDR'],)
            nota  =  'None'
            if len(dtos) > 1:
                #import ipdb; ipdb.set_trace()
                nota = "Verificar descuentos globales"
            """
                valor: negativo o positivo,
                detalles:,
                nota: avisa si hay otros descuentos a considerar.
            """
            #print(valor,deta,nota)
            if valor:
                self.DscRcgGlobal = (valor, deta, nota)

    def _dscrcgglobal(self, drgi):

        tmp_drgitem = dict(
            #NroLinDR    =  drgi.NroLinDR       if hasattr(drgi,'NroLinDR'  ) else 'None',
            #CodDR       =  drgi.CodDR          if hasattr(drgi,'CodDR'     ) else 'None', # basura
            TpoMovDR    =  drgi.TpoMovDR       if hasattr(drgi,'TpoMovDR'  ) else 'None',  # ValorDR  D=dto   r=recgo.
            TpoDR       =  drgi.TpoDR          if hasattr(drgi,'TpoDR'     ) else 'None',  # TipoDRType 1=% 2=$
            GlosaDR     =  drgi.GlosaDR        if hasattr(drgi,'GlosaDR'   ) else 'None',
            ValorDR     =  drgi.ValorDR        if hasattr(drgi,'ValorDR'   ) else 'None',
            IndFactDR   =  drgi.IndFactDR      if hasattr(drgi,'IndFactDR' ) else 'None'   # ver tabla  "indfactdr"
        )

        tmp_drgitem['TpoDR'] = "%" if tmp_drgitem['TpoDR'] == '1' else '2'

        tmp_drgitem['IndFactDR'] = indfactdr[str(tmp_drgitem['IndFactDR'])] \
            if tmp_drgitem['IndFactDR'] is not 'None' else tmp_drgitem['IndFactDR']

        return tmp_drgitem

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



indfactdr = {
         '1': u'Exento de IVA',
         '2': u'Gravado a Tasa Mínima',
         '3': u'Gravado a Tasa Básica',
         '4': u'Gravado a Otra Tasa',
         '6': u'Producto o servicio no facturable',
         '7': u'Producto o servicio no facturable negativo',
        '10': u'Exportación y asimiladas',
        '11': u'Impuesto percibido',
        '12': u'IVA en suspenso',
}
