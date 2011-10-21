# -*- coding: utf-8 -*-

# Copyright (C) 2010 SALOME Pascal

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
Import module for SERMA TLP setup data
"""

from thunderstorm.thunder.importers.tools import ImportPlugin
from thunderstorm.thunder.importers.util_serma import ReadSERMA
from thunderstorm.thunder.tlp import RawTLPdata
from thunderstorm.thunder.pulses import IVTime
import os
import logging

class ImportSERMA(ImportPlugin):
    """Import data from SERMA TLP setup
    """
    label = "SERMA"
    file_ext = "*.csv"

    def __init__(self):
        ImportPlugin.__init__(self)

    def import_data(self, file_name):
        """Import data
        return a RawTLPdata instance"""
        log = logging.getLogger('thunderstorm.info')
        log.info("Importing SERMA data...")
        file_path = os.path.realpath(file_name)
        alldata = ReadSERMA(file_name)
        data = alldata.data_to_num_array
        pulses = IVTime(data['tlp_pulses'].shape[2],
                        data['tlp_pulses'].shape[1],
                        delta_t=data['delta_t'],
                        offsets_t=data['offsets_t'])
        pulses.voltage = data['tlp_pulses'][0]
        pulses.current = data['tlp_pulses'][1]
        #pulses.valim = data['valim_tlp'] #not implemented
        tlp_curve = data['tlp']
        iv_leak = data['leak_data']
        leak_evol = data['leak_evol']
        raw_data = RawTLPdata('not implemented', pulses, iv_leak,
                              tlp_curve, leak_evol, file_path,
                              tester_name = self.label)
        log.info("Importing SERMA data. Done!")
        return raw_data

