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

prefix = re.compile('^{.*}')



class XmlLoad(object):
    """
        Lee el archivo del xml y crea un arbol `lxml.etree`
    """

    def __init__(self, xmlfile=None):
        """
            :param: xmlfile: archivo xml contiene un Sobre ecee

            @caratula:  Elemento `etree` único.
            @cfe_adenda_list: Lista de elementos etree, mín. 1, máx. 250
        """

        if xmlfile is not None:
            try:
                xmldoc = etree.parse(xmlfile)
                root = xmldoc.getroot()
            except Exception as ex:
                msg = "Archivo %s no disponible o no es un `EnvioCFE_entreEmpresas` \n\t%s" % (xmlfile, ex)
                print(msg)  # raise Exception("Error: %s" % (msg,))
                sys.exit()
                
        if len(root):
            self.root = root
        else:
            msg = "Archivo %s no disponible o no es un `EnvioCFE_entreEmpresas`" % (xmlfile)
            print(msg)  
            sys.exit()           
            
                
    
