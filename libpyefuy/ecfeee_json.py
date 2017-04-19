# coding: utf-8
# !/usr/bin/env python3


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


class json_Doc(object):

    def __init__(self, cfe_adenda, fecha_caratula):

        if cfe_adenda is not None:

            self.cfe        = cfe_adenda.CFE()
            self.adenda     = cfe_adenda.Adenda()
            self.fecha      = fecha_caratula
            self.encabezado = self.cfe['Encabezado'].Encabezado
            self.detalle    = self.cfe['Detalle'].Detalle


    @property
    def create(self):


        # *** COMIENZO Cabezal CSV ***#

        Emisor  = self.encabezado['Emisor']
        IdDoc   = self.encabezado['IdDoc']
        Totales = self.encabezado['Totales']

        # si hay descuentos/recargos globales (redondeos)
        drg_items = 'None'
        if self.cfe.has_key('DscRcgGlobal'):
            drg = getattr(self.cfe['DscRcgGlobal'], 'Items', False)
            drg_items = drg if drg and len(drg) else 'None'
        self.drg_items = drg_items

        jcab = \
            dict(
                  cant_lin             = Totales['CantLinDet'],
                  fecha_emis           = IdDoc['FchEmis'],
                  fecha_firma          = self.fecha,
                  tipo_cfe             = IdDoc['TipoCFE'],
                  tipo_documento       = cfe_nombre[str( IdDoc['TipoCFE'] )],
                  serie                = IdDoc['Serie'],
                  numero               = IdDoc['Nro'],
                  proveedor_nombre     = Emisor['NomComercial'],
                  proveedor_rsocial    = Emisor['RznSoc'],
                  proveedor_rut        = Emisor['RUCEmisor'],
                  moneda               = Totales['TpoMoneda'],
                  tipo_cambio          = Totales['TpoCambio'],
                  monto_exp_asim       = Totales['MntExpoyAsim'],
                  monto_imp_percibido  = Totales['MntImpuestoPerc'],
                  monto_no_gravado     = Totales['MntNoGrv'],
                  monto_no_facturable  = Totales['MontoNF'],
                  neto_tminima         = Totales['MntNetoIvaTasaMin'],
                  neto_tbasica         = Totales['MntNetoIVATasaBasica'],
                  neto_otra            = Totales['MntNetoIVAOtra'],
                  monto_iva_min        = Totales['MntIVATasaMin'],
                  monto_iva_bas        = Totales['MntIVATasaBasica'],
                  monto_iva_otr        = Totales['MntIVAOtra'],
                  monto_iva_suspenso   = Totales['MntIVaenSusp'],
                  monto_total          = Totales['MntTotal'],
                  monto_tot_retenido   = Totales['MntTotRetenido'],
                  monto_pagar          = Totales['MntPagar'],
                  drg_items            = self.drg_items,
                  adenda               = self.adenda,
                )

        document = dict(dict(cabezal=jcab))

        jlin = list()
        for lin in self.detalle:

            jlin.append(dict(
                        nrolindet      = lin['NroLinDet'],
                        indfact        = lin['IndFact'],
                        nomitem        = lin['NomItem'],
                        cantidad       = lin['Cantidad'],
                        unimed         = lin['UniMed'],
                        descitem       = lin['DscItem'],
                        preciounitario = lin['PrecioUnitario'],
                        montoitem      = lin['MontoItem'],
                        descuentomonto = lin['DescuentoMonto'],
                        dtoporcentaje  = lin['DescuentoPct'],
                        coditem        = lin['CodItem'] or 'None',
                        subdescuento   = lin['SubDescuento'] or 'None'
                       ))


        document.update(lineas=jlin)

        return document






