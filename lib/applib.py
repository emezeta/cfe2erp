# -*- encoding: utf-8 -*-
#!/usr/bin/env python


import datetime
import re

prefix = re.compile('^{.*}')

def ifis(obj):

    """
    Los objetos del arbol 'root' son atomicos, listas o diccionarios.
    Un valor atómico o una lista no vacía serán devueltos como tal.
    Un diccionario no vacío será devuelto como una lista sobre le primer nivel del diccionario.

    :param obj:     Elemento del arbol del xml
    :return:        'no iterable' o una list o None

    TODO: Quizá un metodo recursivo fuera más apropiado.
    """
    res = ''
    if isinstance(obj, (str,datetime.date,unicode,list)):
        res = obj
    elif isinstance(obj, (int,long,float)):
        res = str(obj)
    elif isinstance(obj, (dict,)):
        obj_content = [ {elem:obj[elem]} for elem in obj ]
        if obj_content:
            res = obj_content
        else:
            res = None
    elif obj is None:
        res = None
    else:
        # logging.info("[%s] INFO  : %s " % (prefix(), ifis))
        raise ValueError('ifis')

    return res


def tag_ns(elem):
    """
        elem: es un elemento, tiene un tag!
        strip ns from tag/element name
    """
    try:
        _tag = elem.tag
    except:
        print("Error %s no tiene un tag..." % (elem,))
        return False

    ns = prefix.match(_tag)
    if ns:
        tag = ns.string[ns.end():]
    else:
        tag = _tag
    return tag
