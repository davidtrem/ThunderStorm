# -*- coding: utf-8 -*-

# Copyright (C) 2010 David Johnsson

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
Utils to read data from HPPI TLP setup file
"""

import numpy as np
from zipfile import ZipFile
from cStringIO import StringIO
import re
import os

DEBUG = False

class ReadHPPI(object):
    """
    Read HPPI TLP data and do few treatment
    """
    def __init__(self, file_name):
        self.base_file_name = file_name[:-4]
        #self.base_dir_name = os.path.dirname(file_name)
        self.data = {}
        self._read_data_from_files()

    def _read_data_from_files(self):
        base_name = self.base_file_name
        data = self.data
        csv_data = extract_data_from_csv(base_name + '.csv')
        data['valim_leak'] = csv_data[0]
        data['tlp'] = csv_data[1:3]
        data['leak_evol'] = csv_data[3]
        data['leak_data'] = read_leak_curves(base_name + '.ctr')
        hppi_wfm = HPPITransientRead(base_name)
        (wfm_list, volt_list) = hppi_wfm.filecontents
        tlp_v = []
        tlp_i = []
        for filename in wfm_list:
            tlp_v.append(hppi_wfm.data_from_transient_file(filename)[3])
            tlp_i.append(hppi_wfm.data_from_transient_file(filename)[1])
        tlp_v = np.asarray(tlp_v)
        tlp_i = np.asarray(tlp_i)

        time_array = hppi_wfm.data_from_transient_file(filename)[0]
        delta_t = time_array[1]-time_array[0]
        data['tlp_pulses'] = np.array((tlp_v, tlp_i))
        data['valim_tlp'] = volt_list
        data['delta_t'] = delta_t * 1e-9
        return None

    @property
    def data_to_num_array(self):
        num_data = {}
        for data_name in ('tlp', 'valim_tlp', 'tlp_pulses',
                          'valim_leak', 'leak_evol'):
            num_data[data_name] = np.array(self.data[data_name])
        num_data['leak_data'] = self.data['leak_data']
        num_data['delta_t'] = self.data['delta_t']
        return num_data


def extract_data_from_csv(tsr_file_name):
    """Extract data from *.csv file
    *.csvfiles contain tlp curve and leakage evolution
    Return an array with
    Vsupply, tlp voltage, tlp current, leakage
    """
    with open(tsr_file_name, 'U') as tsr_file:
        tsr_file_str = tsr_file.read()
    test_result_re = re.compile(r'^Index,HV.*\]\n(.*)', re.S | re.M)
    data_str = test_result_re.findall(tsr_file_str)
    data_str_file = StringIO()
    data_str_file.write(data_str[0])
    data_str_file.reset()
    data = np.loadtxt(data_str_file, delimiter=',', usecols=(1, 2, 3, 8))
    return data.T


def read_leak_curves(filename):
    """Currently not implemented
    an empty list is returned
    """
#    with open(filename, 'U') as data_file:
#        whole_data = data_file.read()
#
#    block_re_str = r"^(\[DATA\])(.*?)(?=\[DATA\]|\Z)"
#    block_re = re.compile(block_re_str, re.S | re.M)
#    blocks = block_re.findall(whole_data)
#
#    data_txt = ['\n'.join(block[1].split('\n')[3:-1]) for block in blocks]
    curves = []
#    for data in data_txt:
#        string_file = StringIO()
#        string_file.write(data)
#        string_file.reset()
#        curves.append(np.loadtxt(string_file, delimiter=',').T[1:])
    return curves



class HPPITransientRead(object):
    """Utils to extract data from HPPI tester files
    """
    def __init__(self, base_dir):
        self.base_dir = os.path.dirname(base_dir)

    def data_from_transient_file(self, filename):
        if self.wfmLoc.find('.zip') == -1:
            filepath = os.path.join(self.wfmLoc, filename)
            with open(filepath, 'U') as wfm_file:
                full_file = wfm_file.read()
            wfm_file.close()
        else:
            zfile = ZipFile(self.wfmLoc)
            full_file = zfile.read(filename)
            zfile.close()
        data_string = '\n'.join(full_file.split('\r\n'))
        data_string_file = StringIO()
        data_string_file.write(data_string)
        data_string_file.reset()
        return np.loadtxt(data_string_file, delimiter=',', skiprows=1).T

    @property
    def filecontents(self):
        is_zip = False
        #check location of waveforms
        base_dir = self.base_dir
        if os.path.exists(os.path.join(base_dir,'wfm')):
            self.wfmLoc = os.path.join(base_dir,'wfm')
            print('waveforms in dir: wfm')
        elif os.path.exists(os.path.join(base_dir,'HV-Pulse')):
            self.wfmLoc = os.path.join(base_dir,'HV-Pulse')
            print('waveforms in dir: HV-Pulse')
        elif os.path.isfile(os.path.join(base_dir,'transients.zip')):
            self.wfmLoc = os.path.join(base_dir,'transients.zip')
            is_zip = True
            print('waveforms in zip file')
        else:
            print('No waveforms found')

        if is_zip:
            zfile = ZipFile(self.wfmLoc)
            wfm_list = zfile.namelist()
        else:
            wfm_list = os.listdir(self.wfmLoc)

        voltages_list = []
        for filename in wfm_list:
            elems = filename[:-5].split('_')
            voltages_list.append(elems[1])
        voltages_list.sort(key=float)
        return (wfm_list, voltages_list)

