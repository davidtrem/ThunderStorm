#!/usr/bin/env python
# -*- coding: utf-8 -*-

from distutils.core import setup

setup(name = 'ThunderStorm',
      version = '0.4',
      author = 'David Trémouilles',
      author_email = 'david.trem at gmail.com',
      url = 'http://code.google.com/p/esdanalysistools/',
      packages = ['thunderstorm',
                  'thunderstorm.thunder',
                  'thunderstorm.thunder.importers',
                  'thunderstorm.lightning',
                  'thunderstorm.istormlib'],
      scripts = ['istorm.py',],
      )
