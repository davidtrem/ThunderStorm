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

from thunderstorm.thunder.utils import string2file
import numpy as np
import logging
import re


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
        tlp_data = extract_data_from_tlp(base_name + '.tlp')
        data['valim_tlp'] = tlp_data[0]
        data['tlp'] = np.array((tlp_data[1],tlp_data[2]))
        data['leak_evol'] = tlp_data[3]
        twf_data = extract_data_from_twf(base_name + '.twf')
        if twf_data != False:
            data['tlp_v_waveforms'] = twf_data[0]
            data['tlp_i_waveforms'] = twf_data[1]
            data['delta_t'] = twf_data[2]
            data['vsupply_tlp'] = twf_data[3]
            data['waveform available'] = True
        else:
            data['waveform available'] = False

    @property
    def data_to_num_array(self):
        num_data = {}
        return num_data

def extract_data_from_tlp(tlp_file_name):
    with open(tlp_file_name, 'U') as tlp_data_file:
        tlp_file_str = tlp_data_file.read()
        version_re_str = r'^Version.*?\t(.*?)\n'
        version_re = re.compile(version_re_str, re.S | re.M)
        barth_file_version = version_re.findall(tlp_file_str)[0]
        if int(barth_file_version.split('.')[0]) < 4:
            re_str = r'^I\(AMPS\).*?\n(.*)\Z'
            col_id = {'pulseV':None, 'idut':0, 'vdut':1, 'leak':2}
        else:
            re_str = r'^Pulse V\(Volts\).*?\n(.*)\Z'
            col_id = {'pulseV':0, 'vdut':1, 'idut':2, 'leak':3}
        test_result_re = re.compile(re_str, re.S | re.M)
        data_str = test_result_re.findall(tlp_file_str)
        data = np.loadtxt(string2file(data_str[0])).T
        if col_id['pulseV'] != None:
            v_alim = data[col_id['pulseV']]
        else:
            v_alim = []
        v_tlp = data[col_id['vdut']]
        i_tlp = data[col_id['idut']]
        i_leak = data[col_id['leak']]
        return v_alim, v_tlp, i_tlp, i_leak


def extract_data_from_twf(twf_file_name):
    """ Extract data from Barth TLP *.twf file
    """
    try:
        with open(twf_file_name, 'U') as twf_data_file:
            twf_file_str = twf_data_file.read()
            data = twf_file_str.split('\n\n')
            head_line = data[0].split('\n')[0]
            if not (head_line.startswith("4002-TLP") or
                    head_line.startswith("4012-TLP")):
                raise TypeError("%s is not a '40?2-TLP Waveform Data' file" %
                                twf_file_name)
            # _vwf voltage waveform related
            # _iwf current waveform related
            delta_t_vwf = float(data[1].split('\t')[2])
            valim_vwf =  np.asarray(data[1].split('\n')[1].split(),
                                    dtype=np.float)
            delta_t_iwf = float(data[3].split('\t')[2])
            valim_iwf = np.asarray(data[3].split('\n')[1].split(),
                                   dtype=np.float)
            dut_vwf_str = data[2]
            dut_iwf_str = data[4]
            data_vwf = np.loadtxt(string2file(dut_vwf_str))
            data_iwf = np.loadtxt(string2file(dut_iwf_str))
            return data_vwf, data_iwf, delta_t_vwf, valim_vwf
    except IOError:
        log = logging.getLogger('thunderstorm.thunder.importers')
        log.warn("No pulse data found")
        return False

