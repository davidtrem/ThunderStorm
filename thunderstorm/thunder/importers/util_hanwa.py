# -*- coding: utf-8 -*-

# Copyright (C) 2010 Linten Dimitri

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
Utils to read data from Hanwa TLP setup file
"""

import numpy as np
from cStringIO import StringIO
import re
import warnings

DEBUG = False

class ReadHanwa(object):
    """
    Read Hanwa TLP data and do few treatment
    """
    def __init__(self, file_name):
        self.base_file_name = file_name[:-4]
        self.data = {}
        self._read_data_from_files()

    def _read_data_from_files(self):
        base_name = self.base_file_name
        data = self.data
        tsr_data = extract_data_from_tsr(base_name + '.tsr')
        data['valim_leak'] = tsr_data[0]
        data['tlp'] = tsr_data[1:3]
        data['leak_evol'] = tsr_data[3]
        data['leak_data'] = read_leak_curves(base_name + '.ctr')
        Hanwa_zip = HanwaTransientZip(base_name + '.zip')
        (base_name, volt_list) = Hanwa_zip.filecontents
        tlp_v = []
        for pulse_voltage in volt_list:
            filename = base_name + '_TlpVolt_' + pulse_voltage + 'V.wfm'
            tlp_v.append(Hanwa_zip.data_from_transient_file(filename)[1])
        tlp_v = np.asarray(tlp_v)
        tlp_i = []
        for pulse_voltage in volt_list:
            filename = base_name + '_TlpCurr_' + pulse_voltage + 'V.wfm'
            tlp_i.append(Hanwa_zip.data_from_transient_file(filename)[1])
        tlp_i = np.asarray(tlp_i)
        time_array = Hanwa_zip.data_from_transient_file(filename)[0]
        delta_t = time_array[1]-time_array[0]
        data['tlp_pulses'] = np.array((tlp_v, tlp_i))
        data['valim_tlp'] = volt_list
        data['delta_t'] = delta_t * 1e-6
        return None

    @property
    def data_to_num_array(self):
        num_data = {}
        for data_name in ('tlp','valim_tlp', 'tlp_pulses',
                          'valim_leak', 'leak_evol'):
            num_data[data_name] = np.array(self.data[data_name])
        num_data['leak_data'] = self.data['leak_data']
        num_data['delta_t'] = self.data['delta_t']
        return num_data


def extract_data_from_tsr(tsr_file_name):
    """Extract data from *.tsr file
    *.tsr files contain tlp curve and leakage evolution
    Return an array with
    Vsupply, tlp voltage, tlp current, leakage
    """
    with open(tsr_file_name, 'U') as tsr_file:
        tsr_file_str = tsr_file.read()
    re_str = r'^"\[=====Test\ Result\ Table.*\]"\n(.*)\n"\[EOF\]"'
    test_result_re = re.compile(re_str, re.S | re.M)
    data_str = test_result_re.findall(tsr_file_str)

    data_str_file = StringIO()
    data_str_file.write(data_str[0])
    data_str_file.reset()
    data = np.loadtxt(data_str_file, delimiter=',', usecols=(0, 3, 4, 5))
    return data.T


def read_leak_curves(filename):
    """Read a *.ctr file and
    Return the leakage IV curves
    """
    with open(filename, 'U') as data_file:
        whole_data = data_file.read()

    block_re_str = r"^(\[DATA\])(.*?)(?=\[DATA\]|\Z)"
    block_re = re.compile(block_re_str, re.S | re.M)
    blocks = block_re.findall(whole_data)

    data_txt = ['\n'.join(block[1].split('\n')[3:-1]) for block in blocks]
    curves = []
    for data in data_txt:
        string_file = StringIO()
        string_file.write(data)
        string_file.reset()
        try:
            curves.append(np.loadtxt(string_file, delimiter=',').T[1:])
        except IOError:
            pass
    return curves


class HanwaTransientZip(object):
    """Utils to extract data from Hanwa zip files
    """
    def __init__(self, zfilename):
        self.zfilename = zfilename

    def data_from_transient_file(self, filename):
        zfile = ZipFile(self.zfilename)
        full_file = zfile.read(filename)
        zfile.close()
        data_string = '\n'.join(full_file.split('\r\n')[13:-2])
        data_string_file = StringIO()
        data_string_file.write(data_string)
        data_string_file.reset()
        return np.loadtxt(data_string_file, delimiter=',').T

    @property
    def list_transient_file(self):
        zfile = ZipFile(self.zfilename)
        file_list = zfile.namelist()
        zfile.close()
        return file_list

    @property
    def supply_voltage_list(self):
        """The TLP supply voltages list

        Return the TLP supply voltage list
        from the filenames in the zip file.

        Returns
        -------
        Return a list of voltages (list of string)

        Raises
        ------
        Throw a warning if voltage and current waveform voltages do
        not match.
        """
        zfile = ZipFile(self.zfilename)
        # filename format
        # for TLP voltage: 04-29-09_05'40'45_PM_TlpVolt_90V.wfm
        # for TLP current: 04-29-09_05'40'45_PM_TlpCurr_90V.wfm
        voltages_dict = {'TlpCurr' : [], 'TlpVolt' : []}
        for filename in zfile.namelist():
            elems = filename[:-5].split('_')
            voltages_dict[elems[3]].append(elems[4])
        voltages_dict['TlpCurr'].sort(key=float)
        voltages_dict['TlpVolt'].sort(key=float)
        if voltages_dict['TlpCurr'] != voltages_dict['TlpVolt']:
            warnings.warn("Current and Voltage waveform mismatch",
                          RuntimeWarning)
        return voltages_dict['TlpCurr']

    @property
    def filecontents(self):
        zfile = ZipFile(self.zfilename)
        volt_list = self.supply_voltage_list
        basename = '_'.join(zfile.namelist()[0].split('_')[0:3])
        zfile.close()
        return (basename, volt_list)

if __name__ == '__main__':
    "" testing the module before posting """