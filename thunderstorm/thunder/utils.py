# -*- coding: utf-8 -*-

from cStringIO import StringIO

def string2file(raw_string):
    """The function return a file like object contaiing the given string

    """
    filelike = StringIO()
    filelike.write(raw_string)
    filelike.reset()
    return filelike
