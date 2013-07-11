# -*- coding: utf-8 -*-

import sys
from io import StringIO


def string2file(raw_string):
    """The function return a file like object contaiing the given string.
    """
    filelike = StringIO()
    if sys.version_info[0] < 3:  # Python 2
        filelike.write(unicode(raw_string))
    else:  # Python 3
        filelike.write(raw_string)
    filelike.flush()
    filelike.seek(0)
    return filelike
