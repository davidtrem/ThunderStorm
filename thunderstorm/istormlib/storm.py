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
from thunderstorm.lightning.simple_plots import TLPOverlay
from matplotlib.pyplot import figure

class Storm(list):
    """ A storm to manipulate a group of your ESD data
    """
    def __init__(self):
        list.__init__(self)
        self.visu_flag = []
        for importer_name in plug_dict.keys():
            importer = plug_dict [importer_name]()
            setattr(self, 'import_'+importer_name,
                    self._gen_import_data(importer))

    def _gen_import_data(self, importer):
        def import_func(filename, comments=""):
            self.append(View(importer.load(filename, comments)))
            self.visu_flag.append(True)
        return import_func

    def __repr__(self):
        if len(self) == 0:
            return "Empty"
        showtxt = ""
        for idx, elem in enumerate(self):
            showtxt += "%s : %s" % (idx, elem)
        return showtxt

    def overlay_raw_tlp(self, index_list=()):
        tlp_fig = TLPOverlay(figure())
        if index_list == ():
            for elem, is_visible in zip(self, self.visu_flag):
                if is_visible:
                    tlp_fig.add_curve(elem.experiment.raw_data.tlp_curve)
        else:
            for idx in index_list:
                tlp_fig.add_curve(self[idx].experiment.raw_data.tlp_curve)
        self.overlay_tlp_fig = tlp_fig





