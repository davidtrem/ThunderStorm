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
import os.path as osp
from os import walk
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
        [head, tail] = osp.split(base_name)
        data = self.data
        tcf_data = extract_data_from_tcf(base_name + '.tcf')
        user_name=tcf_data[0]

        result_base_name=head + osp.sep + 'Result' + osp.sep + tail + '_' + user_name +'_' + tail
        sdb_data = extract_data_from_sbd(result_base_name + '.sbd')

        data['valim_leak'] = tcf_data[1]*np.ones(len(sdb_data[0]))
        data['tlp'] = sdb_data[0:3]
        data['leak_evol'] = sdb_data[3]

        leak_base_dir_name= head + osp.sep + 'Leak'
        print leak_base_dir_name
        data['leak_data'] = read_leak_curves(leak_base_dir_name)
        print data['leak_data'][0]
        # Read in pulses
#        Hanwa_zip = HanwaTransientZip(base_name + '.zip')
#        (base_name, volt_list) = Hanwa_zip.filecontents
#        tlp_v = []
#        for pulse_voltage in volt_list:
#            filename = base_name + '_TlpVolt_' + pulse_voltage + 'V.wfm'
#            tlp_v.append(Hanwa_zip.data_from_transient_file(filename)[1])
#        tlp_v = np.asarray(tlp_v)
#        tlp_i = []
#        for pulse_voltage in volt_list:
#            filename = base_name + '_TlpCurr_' + pulse_voltage + 'V.wfm'
#            tlp_i.append(Hanwa_zip.data_from_transient_file(filename)[1])
#        tlp_i = np.asarray(tlp_i)
#        time_array = Hanwa_zip.data_from_transient_file(filename)[0]
#        delta_t = time_array[1]-time_array[0]
#        data['tlp_pulses'] = np.array((tlp_v, tlp_i))
#        data['valim_tlp'] = volt_list
#        data['delta_t'] = delta_t * 1e-6
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


def extract_data_from_sbd(sbd_file_name):
    """Extract data from *.sbd file
    *.sbd files contain tlp curve and leakage evolution
    Return an array with
    Vsupply, tlp voltage, tlp current, leakage
    """
    with open(sbd_file_name, 'U') as sbd_file:
        sbd_file_str = sbd_file.read()
    re_str = r'^Point,.*\current\n(.*)'
    test_result_re = re.compile(re_str, re.S | re.M)
    data_str = test_result_re.findall(sbd_file_str)
#    print data_str#, sbd_file_str
#
    data_str_file = StringIO()
    data_str_file.write(data_str[0])
    data_str_file.reset()
    data = np.loadtxt(data_str_file, delimiter=',', usecols=(0, 2, 3, 4))
#    print data
    return data.T

def extract_data_from_tcf(tcf_file_name):
    # from the .tcf file, username, leak voltage evuation point needs to beextracted.

    with open(tcf_file_name, 'r') as tcf_file:
            tcf_file_str=tcf_file.read()
    data=[]
    re_str = re.compile('UserName=(.*?)\x0A')
    user_name = re_str.findall(tcf_file_str)[0]
    data.append(user_name)
    re_str = re.compile('LeakSelectPoint=(.*?)\x0A')
    LeakSelectPoint = re_str.findall(tcf_file_str)[0]
    re_str = re.compile( 'Voltage' + LeakSelectPoint + '=(.*?)\x0A')
    LeakSelectVoltage = re_str.findall(tcf_file_str)[0]
    # if leakvoltage is e.g. 800m replace by 0.8
    if 'm' in LeakSelectVoltage:
        LeakSelectVoltage=float(LeakSelectVoltage.replace('m',''))*1e-3
    data.append(LeakSelectVoltage)
    return data

def get_number_of_files_In_dir(dir):
   dir_count, file_count=0, 0
   for root, dirs, files in walk(dir):
        dir_count += len(dirs)
        file_count += len(files)
   return file_count


def read_leak_curves(leak_path):
    """Read *.tld files and
    Return the leakage IV curves
    """
    curves=[]
    if osp.isdir(leak_path):
        n_files=get_number_of_files_In_dir(leak_path)
        print n_files
        for index in np.arange(n_files):
            with open(osp.join(leak_path, 'Leak_'+str(index)+'.tld'), 'r') as file:
                    file_str=file.read()
                    data_str_file = StringIO()
                    data_str_file.write(file_str)
                    data_str_file.reset()
                    data = np.loadtxt(data_str_file, delimiter=',', usecols=(0, 1))
            curves.append(data.T)
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
    """ testing the module before posting """

    filename="D:\linten\Python\TestData\IMEC\TLP\GDIODE_nw_L70\GDIODE_nw_L70.tcf"
    data=ReadHanwa(filename)
