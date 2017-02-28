# coding: utf-8

'''
El template contiene todos los campos de un CFE para Envio entre empresas.
Actualmente 24/02 solo aparecen los del tipo `eFact`, falta agregar los
campos que resulten de la interseccion de los conjuntos
'''

Caratula = {
    'CantCFE'        : None,
    'Fecha'          : None,
    'Idemisor'       : None,
    'RUCEmisor'      : None,
    'RutReceptor'    : None,
    'X509Certificate': None,
}


'''
eDoc:
-----
Contiene todos los campos de un CFE para Envio entre empresas. Las llaves
del diccionario son la interseccion de los tipos de documentos:
    `eTck`, `eFact`, `eFact_Exp`, `eRem`, `eRem_Exp` y `eResg`
eDoc siempre adoptará los valores de uno de ellos.
'''

eDoc = {
    'TmstFirma' : None,
    'Encabezado': {
        'IdDoc'   : {
            'TipoCFE'    : None,
            'Serie'      : None,
            'Nro'        : None,
            'FchEmis'    : None,
            'MntBruto'   : None,
            'FmaPago'    : None,
            'FchVenc'    : None,
            'CantLinDet' : None,
        },
        'Emisor'  : {
            'RUCEmisor'          : None,
            'RznSoc'             : None,
            'NomComercial'       : None,
            'Telefono'           : None,
            'CorreoEmisor'       : None,
            'EmiSucursal'        : None,
            'CdgDGISucur'        : None,
            'DomFiscal'          : None,
            'Ciudad'             : None,
            'Departamento'       : None,
            'InfoAdicionalEmisor': None,
        },
        'Receptor': {
            'TipoDocRecep' : None,
            'CodPaisRecep' : None,
            'DocRecep'     : None,
            'RznSocRecep'  : None,
            'DirRecep'     : None,
            'CiudadRecep'  : None,
            'DeptoRecep'   : None,
            'PaisRecep'    : None,
            'CP'           : None,
            'InfoAdicional': None,
            'CompraID'     : None,
        },
        'Totales' : {
            'TpoMoneda'           : None,
            'TpoCambio'           : None,
            'MntNoGrv'            : None,
            'MntExpoyAsim'        : None,
            'MntImpuestoPerc'     : None,
            'MntIVaenSusp'        : None,
            'MntNetoIvaTasaMin'   : None,
            'MntNetoIVATasaBasica': None,
            'MntNetoIVAOtra'      : None,
            'IVATasaMin'          : None,
            'IVATasaBasica'       : None,
            'MntIVATasaMin'       : None,
            'MntIVATasaBasica'    : None,
            'MntIVAOtra'          : None,
            'MntTotal'            : None,
            'MntTotRetenido'      : None,
            'CantLinDet'          : None,
            'MontoNF'             : None,
            'MntPagar'            : None,
        }
    },
    'Detalle'   : [ {
        'Item': {
            'NroLinDet'     : None,
            'IndFact'       : None,
            'CodItem'       : [{'TpoCod': None, 'Cod': None}],
            'NomItem'       : None,
            'Cantidad'      : None,
            'UniMed'        : None,
            'DscItem'       : None,
            'PrecioUnitario': None,
            'MontoItem'     : None,
        },
    } ],
    'SubTotInfo': {
        'STI_Item': [{ 'NroSTI': None, 'GlosaSTI': None, 'OrdenSTI': None,
                        'ValSubtotSTI': None, }]
    },

    'DscRcgGlobal': [{'DRG_Item':
                          [{'NroLinDR' : None,
                            'TpoMovDR' : None,   #  D - Dto. / R - Rec.
                            'TpoDR'    : None,   #  1 - %    / 2 - $
                            'CodDR'    : None,
                            'GlosaDR'  : None,
                            'ValorDR'  : None,
                            'IndFactDR': None,   #  [0]
            }],
    }, ],

    'MediosPago': dict(),

    'Referencia': [{
       'Referencia': {
            'NroLinRef': None,
            'IndGlobal': None,
            'RazonRef' : None,
            'TpoDocRef': None,
            'Serie'    : None,
            'NroCFERef': None,
        }
    } ],
    'CAEData'   : {
        'CAE_ID' : None,
        'DNro'   : None,
        'HNro'   : None,
        'FecVenc': None,
    },

    'Compl_Fiscal':{
        'RUCEmisor': None,
        'TipoDocMdte': None, # [1]
        'Pais': None,
        'DocMdte': None,
        'NombreMdte': None,
    },

}

"""
Información adicional para la interpretación de algunos ítems.
==============================================================
    [0] Indicador de facturación `IndFactDR`
         1: Exento de IVA
         2: Gravado a Tasa Mínima
         3: Gravado a Tasa Básica
         4: Gravado a Otra Tasa
         6: Producto o servicio no facturable
         7: Producto o servicio no facturable negativo
        10: Exportación y asimiladas
        11: Impuesto percibido
        12: IVA en suspenso

    [1] Tipo de Complemento Fiscal `TipoDocMdte`
         1: NIE
         2: RUC (Uruguay)
         3: C.I. (Uruguay)
         4: Otros
         5: Pasaporte (todos los países)
         6: DNI (documento de identidad de Argentina, Brasil, Chile o Paraguay)
"""


















