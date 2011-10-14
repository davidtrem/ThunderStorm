#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""Python setup script for ThunderStorm
"""

from distutils.core import setup
from thunderstorm import __version__

setup(name = 'ThunderStorm',
      version = __version__,
      author = 'David Trémouilles, Dimitri Linten',
      author_email = 'david.trem at gmail.com Dimitri Linten at gmail.com',
      url = 'http://code.google.com/p/esdanalysistools/',
      license = 'LGPL',
      platforms = ['any'],
      packages = ['thunderstorm',
                  'thunderstorm.thunder',
                  'thunderstorm.thunder.importers',
                  'thunderstorm.lightning',
                  'thunderstorm.istormlib'],
      scripts = ['istorm.py',],
      )
