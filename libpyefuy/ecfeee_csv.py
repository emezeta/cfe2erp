# coding: utf-8
# !/usr/bin/env python3

from __future__ import print_function
import re
import sys
from dateutil import parser

from lxml import etree, objectify

prefix = re.compile('^{.*}')


def arma_cabezal(cfead,fecha_caratula):

            # *** COMIENZO Cabezal CSV ***


            # enc    = cfead['cfe']['Encabezado'].Encabezado
            enc    = cfead['cfe']['Encabezado'].Encabezado
            rdg    = getattr(cfead['cfe'],'DscRcgGlobal', False)

            ee = enc['Emisor']
            er = enc['Receptor']
            ei = enc['IdDoc']
            et = enc['Totales']
            if rdg:
                rd = dict(Valor = rdg[0], Deta = rdg[1], Nota = rdg[2])
            else:
                rd = dict(Valor = 'None', Deta = 'None', Nota = 'None')

            td = tipodoc
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

            lcabezal.append(rd['Valor'])     # valor del dto.
            lcabezal.append(rd['Deta'])      # resumen del dto
            lcabezal.append(rd['Nota'])
            res = record(lcabezal)
            return res

def record(csv_row):

    """ Convertir todo a string (`int.encode` => ERROR )
        `int`, `long` y `float` deben pasar a ser strings
    """
    res = list()

    tipos_num = (int, long, float, complex)

    for i in csv_row:
        try:
            if getattr(i, 'pyval', False):
                if isinstance(i.pyval, (tipos_num,)):
                    res.append(str(i.pyval))
                elif isinstance(i.pyval, (str,)):
                    res.append(i.pyval)
            else:
                if isinstance(i, (tipos_num,)):
                    res.append(str(i))
                elif isinstance(i, (str,)):
                    res.append(i)
        except Exception as ex:
            #import ipdb; ipdb.set_trace()
            print('no hay valor, que feo', ex)
            sys.exit()

    return res

tipodoc = {
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

campos_cabezal = ('indicador_linea', 'cant_lin', 'fecha_emis', 'fecha_firma', 'tipo_cfe', 'tipo_documento', 'serie', 'numero', 'proveedor_nombre', 'proveedor_rsocial', 'proveedor_rut', 'moneda', 'tipo_cambio', 'monto_exp_asim', 'monto_imp_percibido', 'monto_no_gravado', 'monto_no_facturable', 'neto_tminima', 'neto_tbasica', 'neto_otra', 'monto_iva_min', 'monto_iva_bas', 'monto_iva_otr', 'monto_iva_suspenso', 'monto_total', 'monto_tot_retenido',
 'monto_pagar', 'dto_recargo', 'det_dto_rec', 'dto_rec_nota')
