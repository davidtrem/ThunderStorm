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
Import module for Oryx TLP setup data
"""

from thunderstorm.thunder.importers.tools import ImportPlugin
from thunderstorm.thunder.importers.util_oryx import ReadOryx
from thunderstorm.thunder.tlp import RawTLPdata
from thunderstorm.thunder.pulses import IVTime
import os
import logging


class ImportOryx(ImportPlugin):
    """Import data from Oryx TLP setup
    """
    label = "Oryx"
    file_ext = "*.tsr"

    def __init__(self):
        ImportPlugin.__init__(self)

    def import_data(self, file_name):
        """Import data
        return a RawTLPdata instance"""
        log = logging.getLogger('thunderstorm.info')
        log.info("Importing Oryx data...")
        file_path = os.path.realpath(file_name)
        alldata = ReadOryx(file_name)
        data = alldata.data_to_num_array
        if data['waveform_available'] == True:
            pulses = IVTime(data['tlp_pulses'].shape[2],
                            data['tlp_pulses'].shape[1],
                            delta_t=data['delta_t'],
                            offsets_t=data['offsets_t'])
            pulses.voltage = data['tlp_pulses'][0]
            pulses.current = data['tlp_pulses'][1]
        else:
            pulses = IVTime(0, data['tlp'].shape[1], delta_t=1)
        tlp_curve = data['tlp']
        iv_leak = data['leak_data']
        leak_evol = data['leak_evol']
        raw_data = RawTLPdata('not implemented', pulses, iv_leak,
                              tlp_curve, leak_evol, file_path,
                              tester_name=self.label)
        log.info("Importing Oryx data. Done!")
        return raw_data
