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
Import module for LAAS TLP setup data
"""

import os
from thunderstorm.thunder.importers.tools import ImportPlugin
from thunderstorm.thunder.importers.util_laas import ReadLAAS
from thunderstorm.thunder.tlp import RawTLPdata
from thunderstorm.thunder.pulses import IVTime
import logging

class ImportLAAS(ImportPlugin):
    """Import data from LAAS TLP setup
    """
    label = "LAAS"
    file_ext = "*.mes"

    def __init__(self):
        ImportPlugin.__init__(self)

    def import_data(self, file_name):
        """Import LAAS data"""
        log = logging.getLogger('thunderstorm.info')
        file_path = os.path.realpath(file_name)
        datafile = open(file_name, 'U')
        alldata = ReadLAAS(datafile)
        datafile.close()
        log.info("Importing LAAS data...")
        data = alldata.data_to_num_array
        pulses = IVTime(data['tlp_pulses'].shape[2],
                        data['tlp_pulses'].shape[0],
                        delta_t=1)
        pulses.voltage = data['tlp_pulses'][:, 1, :]
        pulses.current = data['tlp_pulses'][:, 2, :]
        pulses.valim = data['valim_tlp']
        delta_t = (data['tlp_pulses'][0, 0, 1] - data['tlp_pulses'][0, 0, 0])
        pulses.delta_t = delta_t
        # peupler l'objet avec les bonnes données
        # implemter : recupération du delta_t dans l'util_laas
        tlp_curve = data['tlp']
        iv_leak = data['leak_data']
        leak_evol = None # To be implemented
        raw_data = RawTLPdata(alldata.identification, pulses, iv_leak,
                              tlp_curve, leak_evol, file_path,
                              tester_name = self.label)
        log.info("Importing LAAS data. Done!")
        return raw_data




