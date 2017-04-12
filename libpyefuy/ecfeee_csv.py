# coding: utf-8
# !/usr/bin/env python3

from __future__ import print_function
import re
import sys
from dateutil import parser

from lxml import etree, objectify

prefix = re.compile('^{.*}')

def dscreg(drg):
    "Reducir la cantidad de Items"
    res = list()

    items = getattr(drg, 'DscRcgGlobal', [])
    #print(items)
    if items is None:
        return res
    for i in items:
        if float(i['ValorDR']) > 0.0:
            dscreg = dict( GlosaDR=i['GlosaDR'], ValorDR = i['ValorDR'], DetalDR="Tasa/Valor: %s - Dto/Rec: %s - Tipo: %s" % (i['TpoDR'],i['TpoMovDR'],i['IndFactDR']))
            res.append(dscreg)
    return res

def arma_cabezal(cfead,fecha_caratula):

            # import ipdb; ipdb.set_trace()

            # *** COMIENZO Cabezal CSV ***
            enc    = cfead['cfe']['Encabezado'].Encabezado
            ee = enc['Emisor']
            er = enc['Receptor']
            ei = enc['IdDoc']
            et = enc['Totales']

            # *** crea línea de Cabezal CSV ***
            lcabezal = list()

            lcabezal.append('C')
            lcabezal.append(et['CantLinDet'])
            lcabezal.append(ei['FchEmis'])
            lcabezal.append(fecha_caratula)

            lcabezal.append(ei['TipoCFE'])               # es el número 101, 102, 111, ...
            lcabezal.append(td[str(ei['TipoCFE'])])      # es el nombre "eTicket", eFactura", ...
            lcabezal.append(ei['Serie'])
            lcabezal.append(ei['Nro'])

            lcabezal.append(ee['NomComercial'])
            lcabezal.append(ee['RznSoc'])
            lcabezal.append(ee['RUCEmisor'])

            lcabezal.append(et['TpoMoneda'])
            lcabezal.append(et['TpoCambio'])

            lcabezal.append(et['MntExpoyAsim'])          # exportación y asimilados
            lcabezal.append(et['MntImpuestoPerc'])
            lcabezal.append(et['MntNoGrv'])
            lcabezal.append(et['MontoNF'])

            lcabezal.append(et['MntNetoIvaTasaMin'])
            lcabezal.append(et['MntNetoIVATasaBasica'])
            lcabezal.append(et['MntNetoIVAOtra'])

            lcabezal.append(et['MntIVATasaMin'])
            lcabezal.append(et['MntIVATasaBasica'])
            lcabezal.append(et['MntIVAOtra'])

            lcabezal.append(et['MntIVaenSusp'])

            lcabezal.append(et['MntTotal'])
            lcabezal.append(et['MntTotRetenido'])
            lcabezal.append(et['MntPagar'])

            if cfead['cfe'].has_key('DscRcgGlobal') and len(cfead['cfe']['DscRcgGlobal'].DscRcgGlobal):

                #drg = dscreg(cfead['cfe']['DscRcgGlobal'])
                drg_items = cfead['cfe']['DscRcgGlobal'].DscRcgGlobal
                #import ipdb; ipdb.set_trace()

                for dr in drg_items:
                    #print(dr)
                    
                    lcabezal.append(dr['GlosaDR'])
                    lcabezal.append(dr['ValorDR'])
                    datal = "Tasa/Valor: %s - Dto/Rec: %s - Tipo: %s" % (dr['TpoDR'],dr['TpoMovDR'],dr['IndFactDR'])
                    lcabezal.append()

                for header in range(len(drg_items)):
                    campos_cabezal.append('dr%s_glosa' % (str(header),))
                    campos_cabezal.append('dr%s_valor' % (str(header),))
                    campos_cabezal.append('dr%s_deta'  % (str(header),))
                    #print('dr%s_glosa, dr%s_valor, dr%s_deta' % (str(header), str(header), str(header) ))


            res = (campos_cabezal, record(lcabezal))
            return res

def record(csv_row):

    """ Convertir a string todo lo que no sea strig
        (`int.encode` => ERROR )
        `int`, `long` y `float` deben pasar a ser strings
    """
    res = list()

    tipos_num = (int, long, float, complex)

    for i in csv_row:
        try:
            if getattr(i, 'pyval', False):
                if isinstance(i.pyval, (tipos_num,)):
                    res.append(str(i.pyval))
                elif isinstance(i.pyval, (str,unicode)):
                    res.append(i.pyval)
            else:
                if isinstance(i, (tipos_num,)):
                    res.append(str(i))
                elif isinstance(i, (str,unicode)):
                    res.append(i)
        except Exception as ex:
            #import ipdb; ipdb.set_trace()
            print('no hay valor, que feo', ex)
            sys.exit()

    return res

# Tipos de Documentos
td = {
 '101': u'e-Ticket',
 '102': u'Nota de Crédito de e-Ticket',
 '103': u'Nota de Débito de e-Ticket',
 '111': u'e-Factura',
 '112': u'Nota de Crédito de e-Factura',
 '113': u'Nota de Débito de e-Factura',
 '121': u'e-Factura Exportación',
 '122': u'Nota de Crédito de e-Factura Exportación',
 '123': u'Nota de Débito de e-Factura Exportación',
 '124': u'e-Remito de Exportación',

 '131': u'e-Ticket Venta por Cuenta Ajena',
 '132': u'Nota de Crédito de e-Ticket Venta por Cuenta Ajena',
 '133': u'Nota de Débito de e-Ticket Venta por Cuenta Ajena',
 '141': u'e-Factura Venta por Cuenta Ajena',
 '142': u'Nota de Crédito de e-Factura Venta por Cuenta Ajena',
 '143': u'Nota de Débito de e-Factura Venta por Cuenta Ajena',
 '181': u'e-Remito',
 '182': u'e-Resguardo CÓDIGO CFC',
}

campos_cabezal = ['indicador_linea', 'cant_lin', 'fecha_emis', 'fecha_firma', 'tipo_cfe', 'tipo_documento', 'serie', 'numero', 'proveedor_nombre', 'proveedor_rsocial', 'proveedor_rut', 'moneda', 'tipo_cambio', 'monto_exp_asim', 'monto_imp_percibido', 'monto_no_gravado', 'monto_no_facturable', 'neto_tminima', 'neto_tbasica', 'neto_otra', 'monto_iva_min', 'monto_iva_bas', 'monto_iva_otr', 'monto_iva_suspenso', 'monto_total', 'monto_tot_retenido', 'monto_pagar' ]


