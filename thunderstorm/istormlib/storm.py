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

from .istorm_view import View
from ..thunder.tlp import Droplet


class Storm(list):
    """ A storm to manipulate a group of your ESD data
    """
    def __init__(self):
        list.__init__(self)

    def load(self, oef_filename):
        self.append(View(Droplet(oef_filename)))

    def overlay_raw_tlp(self, tlp_fig, index_list=None,
                        experiment_list=()):
        if index_list is None:
            index_list = ()
        tlp_fig.clean()
        tlp_fig.decorate()
        if index_list == () and len(experiment_list) != 0:
            for experiment in experiment_list:
                tlp_fig.add_curve(experiment.raw_data)
        else:
            for idx in index_list:
                tlp_fig.add_curve(self[idx].experiment.raw_data)
