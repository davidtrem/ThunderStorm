# -*- coding: utf-8 -*-

# Copyright (C) 2010 Trémouilles David

#This file is part of Thunderstorm.
#
#ThunderStrom is free software: you can redistribute it and/or modify
#it under the terms of the GNU Lesser General Public License as published by
#the Free Software Foundation, either version 3 of the License, or
#(at your option) any later version.
#
#ThunderStorm is distributed in the hope that it will be useful,
#but WITHOUT ANY WARRANTY; without even the implied warranty of
#MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#GNU Lesser General Public License for more details.
#
#You should have received a copy of the GNU Lesser General Public License
#along with ThunderStorm.  If not, see <http://www.gnu.org/licenses/>.

"""
Data storm
"""
from thunderstorm.thunder.importers.tools import plug_dict
from istorm_view import View

class Storm(list):
    """ A storm to group your ESD data
    """
    def __init__(self):
        list.__init__(self)
        for importer_name in plug_dict.keys():
            importer = plug_dict [importer_name]()
            setattr(self, 'import_'+importer_name,
                    self._gen_import_data(importer))
    def _gen_import_data(self, importer):
        def import_func(filename, comments=""):
            self.append(View(importer.load(filename, comments)))
        return import_func




