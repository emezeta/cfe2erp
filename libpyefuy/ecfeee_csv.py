# coding: utf-8
# !/usr/bin/env python3

from __future__ import print_function
import sys


# Tipos de Documentos
cfe_nombre = \
    {
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

campos_cabezal = \
    (               'id_cabezal',
                    'cant_lin',
                    'fecha_emis',
                    'fecha_firma',
                    'tipo_cfe',
                    'tipo_documento',
                    'serie',
                    'numero',
                    'proveedor_nombre',
                    'proveedor_rsocial',
                    'proveedor_rut',
                    'moneda',
                    'tipo_cambio',
                    'monto_exp_asim',
                    'monto_imp_percibido',
                    'monto_no_gravado',
                    'monto_no_facturable',
                    'neto_tminima',
                    'neto_tbasica',
                    'neto_otra',
                    'monto_iva_min',
                    'monto_iva_bas',
                    'monto_iva_otr',
                    'monto_iva_suspenso',
                    'monto_total',
                    'monto_tot_retenido',
                    'monto_pagar'
    )

campos_linea = \
    (               'id_linea',
                    'nrolindet',
                    'indfact',
                    'nomitem',
                    'cantidad',
                    'unimed',
                    'descitem',
                    'preciounitario',
                    'montoitem',
                    'descuentomonto',
                    'dtoporcentaje',
                    'cod1',
                    'cod2',
                    'cod3',
                    'cod4',
                    'cod5',
                    'dto1_tip',
                    'dto1_val',
                    'dto2_tip',
                    'dto2_val',
                    'dto3_tip',
                    'dto3_val',
                    'dto4_tip',
                    'dto4_val',
                    'dto5_tip',
                    'dto5_val',
    )


class csv_Doc(object):

    def __init__(self, cfe_adenda, fecha):

        if cfe_adenda is not None:

            self._cfe        = cfe_adenda['cfe']
            self._adenda     = cfe_adenda['adenda']
            self._fecha      = fecha
            self._encabezado = self._cfe['Encabezado'].Encabezado
            self._detalle    = self._cfe['Detalle'].Detalle
            if self._cfe.has_key('DscRcgGlobal'):
                drg = getattr(cfe_adenda['cfe']['DscRcgGlobal'], 'Items', False)
                self._drg_items = drg if drg and len(drg) else None
            else:
                self._drg_items = None

    @property
    def cabezal(self):

        # *** COMIENZO Cabezal CSV ***#

        Emisor  = self._encabezado['Emisor']
        IdDoc   = self._encabezado['IdDoc']
        Totales = self._encabezado['Totales']
        nom_doc = cfe_nombre[str( IdDoc['TipoCFE'] )]
        # *** crea línea de Cabezal CSV ***
        cabezal = list()
        cabezal.append('C')                                   # 'id_cabezal',
        cabezal.append( Totales['CantLinDet'] )               # 'cant_lin',
        cabezal.append( IdDoc['FchEmis'] )                    # 'fecha_emis',
        cabezal.append( self._fecha )                               # 'fecha_firma',  Caratula
        cabezal.append( IdDoc['TipoCFE'] )                    # 'tipo_cfe',
        cabezal.append( nom_doc )                             # 'tipo_documento',
        cabezal.append( IdDoc['Serie'] )                      # 'serie',
        cabezal.append( IdDoc['Nro'] )                        # 'numero',
        cabezal.append( Emisor['NomComercial'] )              # 'proveedor_nombre',
        cabezal.append( Emisor['RznSoc'] )                    # 'proveedor_rsocial',
        cabezal.append( Emisor['RUCEmisor'] )                 # 'proveedor_rut',
        cabezal.append( Totales['TpoMoneda'] )                # 'moneda',
        cabezal.append( Totales['TpoCambio'] )                # 'tipo_cambio',
        cabezal.append( Totales['MntExpoyAsim'] )             # 'monto_exp_asim',
        cabezal.append( Totales['MntImpuestoPerc'] )          # 'monto_imp_percibido',
        cabezal.append( Totales['MntNoGrv'] )                 # 'monto_no_gravado',
        cabezal.append( Totales['MontoNF'] )                  # 'monto_no_facturable',
        cabezal.append( Totales['MntNetoIvaTasaMin'] )        # 'neto_tminima',
        cabezal.append( Totales['MntNetoIVATasaBasica'] )     # 'neto_tbasica',
        cabezal.append( Totales['MntNetoIVAOtra'] )           # 'neto_otra',
        cabezal.append( Totales['MntIVATasaMin'] )            # 'monto_iva_min',
        cabezal.append( Totales['MntIVATasaBasica'] )         # 'monto_iva_bas',
        cabezal.append( Totales['MntIVAOtra'] )               # 'monto_iva_otr',
        cabezal.append( Totales['MntIVaenSusp'] )             # 'monto_iva_suspenso',
        cabezal.append( Totales['MntTotal'] )                 # 'monto_total',
        cabezal.append( Totales['MntTotRetenido'] )           # 'monto_tot_retenido',
        cabezal.append( Totales['MntPagar'] )                 # 'monto_pagar'
        cc = list(campos_cabezal)
        # si hay descuentos/recargos globales (redondeos)
        if self._drg_items is not None:
            hdr = 0
            for dr in self._drg_items:
                cabezal.append(dr['GlosaDR'])
                cabezal.append(dr['ValorDR'])
                detal = "Tasa/Valor: %s - Dto/Rec: %s - Tipo: %s" % (dr['TpoDR'],dr['TpoMovDR'],dr['IndFactDR'])
                cabezal.append(detal)
                cc.append('dr%s_glosa' % (str(hdr),))
                cc.append('dr%s_valor' % (str(hdr),))
                cc.append('dr%s_deta'  % (str(hdr),))
                hdr += 1
        if self._adenda:
            cabezal.append(self._adenda)
        else:
            cabezal.append('None')
        cc.append('adenda')
        res = (cc, self.record(cabezal))
        return res


    @property
    def lineas(self):

        # *** COMIENZO líneas CSV ***

        lineas = list()
        for lin in self._detalle:
            linea = list()
            linea.append('L')                        # 'id_linea',
            linea.append(lin['NroLinDet'])           # 'nrolindet',
            linea.append(lin['IndFact'])             # 'indfact',
            linea.append(lin['NomItem'])             # 'nomitem',
            linea.append(lin['Cantidad'])            # 'cantidad',
            linea.append(lin['UniMed'])              # 'unimed',
            linea.append(lin['DscItem'])             # 'descitem',
            linea.append(lin['PrecioUnitario'])      # 'preciounitario',
            linea.append(lin['MontoItem'])           # 'montoitem',
            linea.append(lin['DescuentoMonto'])      # 'descuentomonto',
            linea.append(lin['DescuentoPct'])        # 'dtoporcentaje',

            if lin['CodItem'] is not 'None':
                hdr = 0
                for coditem in lin['CodItem']:
                    linea.append(coditem)
                    hdr =+ 1
                for i in range(5-hdr):
                    linea.append('None')
                    hdr =+ 1
            else:
                for i in range(5):
                    linea.append('None')

            if lin['SubDescuento'] is not 'None':
                hdr = 0
                for dto in lin['SubDescuento']:
                    # tipo y valor del descuento
                    linea.append(dto['DescTipo'])
                    linea.append(dto['DescVal'])
                    hdr =+ 1
                for i in range(5-hdr):
                    linea.append('None')
                    linea.append('None')
                    hdr += 1
            else:
                for i in range(5):
                    linea.append('None')
            lineas.append(self.record(linea))
        res =  (campos_linea, lineas)
        return res


    def record(self, csv_row):

        """
            Convertir a string todo lo que no sea string
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
