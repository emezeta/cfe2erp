# -*- encoding: utf-8 -*-

# b = objectify.SubElement(root, "b")
from lxml import etree, objectify

Caratula_tmp = {
    'CantCFE'        : None,
    'Fecha'          : None,
    'Idemisor'       : None,
    'RUCEmisor'      : None,
    'RutReceptor'    : None,
    'X509Certificate': None,
}

# eDoc_tmp = 'eTck' or 'eFact' or 'eFact_Exp' or 'eRem' or 'eRem_Exp' or 'eResg'

CFE_Adenda_tmp = {
    'CFE'   :  { 'eDoc': None, 'Signature': None },
    'Adenda': None,
}



# faltan definir los tmp para  'eTck', 'eFact_Exp', 'eRem', 'eRem_Exp' y 'eResg'

eFact_tmp = {
    'TmstFirma' : None,
    'Encabezado': {
        'IdDoc'   : {
            'TipoCFE' : None,
            'Serie'   : None,
            'Nro'     : None,
            'FchEmis' : None,
            'MntBruto': None,
            'FmaPago' : None,
            'FchVenc' : None,
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
    'SubTotInfo': {
        "STI_Item": [{ "NroSTI": None, "GlosaSTI": None, "OrdenSTI": None,
                        "ValSubtotSTI": None, }]
    },
}

# por ahora no nos interesa.
Signature_tmp = {}











































