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
Utils to read data from Barth TLP setup file
"""

from thunder.utils import string2file
import numpy as np


class ReadBarth(object):
    """Read Barth TLP data and do few treatments
    """
    def __init__(self, file_name):
        self.base_file_name = file_name[:-4]
        self.data = {}
        self._read_data_from_files()

    def _read_data_from_files(self):
        base_name = self.base_file_name
        data = self.data
        twf_data = extract_data_from_twf(base_name + 'twf')
        data['vsupply_tlp'] = twf_data[3]
        data['delta_t'] = twf_data[2]
        data['tlp_v_waveforms'] = data[0]
        data['tlp_v_waveforms'] = data[1]

    @property
    def data_to_num_array(self):
        num_data = {}
        return num_data

def extract_data_from_twf(twf_file_name):
    """ Extract data from Barth TLP *.twf file
    """
    with open(twf_file_name, 'U') as twf_data_file:
        twf_file_str = twf_data_file.read()
        data = twf_file_str.split('\n\n')
        if data[0].split('\n')[0] != "4002-TLP Waveform Data":
            raise TypeError("%s is not a '4002-TLP Waveform Data' file" %
                            twf_file_name)
        # _vwf voltage waveform related
        # _iwf current waveform related
        delta_t_vwf = float(data[1].split('\t')[2])
        valim_vwf =  np.asarray(data[1].split('\n')[1].split(), dtype=np.float)
        delta_t_iwf = float(data[3].split('\t')[2])
        valim_iwf = np.asarray(data[3].split('\n')[1].split(), dtype=np.float)
        dut_vwf_str = data[2]
        dut_iwf_str = data[4]
        data_vwf = np.loadtxt(string2file(dut_vwf_str))
        data_iwf = np.loadtxt(string2file(dut_iwf_str))

        return data_vwf, data_iwf, delta_t_vwf, valim_vwf
