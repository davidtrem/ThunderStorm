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
from thunderstorm.istormlib.istorm_view import View
from thunderstorm.lightning.simple_plots import TLPOverlay
from matplotlib.pyplot import figure

class Storm(list):
    """ A storm to manipulate a group of your ESD data
    """
    def __init__(self, overlay_tlp_fig=None):
        list.__init__(self)
        for importer_name in plug_dict.keys():
            importer = plug_dict [importer_name]()
            setattr(self, 'import_'+importer_name,
                    self._gen_import_data(importer))
        self.overlay_tlp_fig = overlay_tlp_fig

    def _gen_import_data(self, importer):
        def import_func(filename, comments=""):
            self.append(View(importer.load(filename, comments)))
        return import_func

    def __repr__(self):
        if len(self) == 0:
            return "Empty"
        showtxt = ""
        for idx, elem in enumerate(self):
            showtxt += "%s : %s" % (idx, elem)
        return showtxt

    def overlay_raw_tlp(self, index_list=(), experiment_list=()):
        if self.overlay_tlp_fig == None:
            tlp_fig = TLPOverlay(figure())
        else:
            tlp_fig = self.overlay_tlp_fig
        tlp_fig.tlp_plot.cla()
        tlp_fig.decorate()
        if index_list == () and len(experiment_list) != 0:
            for experiment in experiment_list:
                tlp_fig.add_curve(experiment.raw_data.tlp_curve)
        else:
            for idx in index_list:
                tlp_fig.add_curve(self[idx].experiment.raw_data.tlp_curve)





