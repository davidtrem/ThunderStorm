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
from os import walk, listdir
import re
import logging

class ReadHanwa(object):
    """
    Read Hanwa TLP data and do few treatment
    """
    def __init__(self, file_name):
        self.base_file_name = file_name[:-4]
        self.data = {}
        self.read_data_from_files()

    def read_data_from_files(self):
        """ Read the data form the .tcf, .sbd, and csv files
        """
        [head, tail] = osp.split(self.base_file_name)
        tcf_data = extract_data_from_tcf(self.base_file_name + '.tcf')
        user_name = tcf_data[0]
        result_base_name = \
            osp.join(head,'Result', tail + '_' + user_name +'_' + tail)
        sdb_data = extract_data_from_sbd(result_base_name + '.sbd')

        self.data['valim_leak'] = tcf_data[1]*np.ones(len(sdb_data[0]))
        self.data['tlp'] = sdb_data[2:4]
        self.data['leak_evol'] = sdb_data[4]
        self.data['valim_tlp'] = sdb_data[0]

        leak_base_dir_name = head + osp.sep + 'Leak'
        self.data['leak_data'] = read_leak_curves(leak_base_dir_name)

        len_file_list = filecontents(head)
        pulse_id_array = np.arange(len_file_list) + 1

        def read_pulse_file(pulse_type, pulse_id, idx):
            """ Reads in the data , either the V -waveform or the I-waveform
                from the csv file
                pulse_type : 'V' or 'I'
                pulse_id : pulse identity number e.g. pulse 20
                index: which coloun of the csv you wantto return
                    0 : time line
                    1 : the v or I data ( corresponding to the selected type
            """
            pulse_id_filename = pulse_type+'_'+ str(pulse_id) + '.csv'
            pulse_w_filename = osp.join(head, 'Osillo'+pulse_type, \
                pulse_id_filename)
            return data_from_transient_file(pulse_w_filename)[idx]

        tlp_v = np.asarray(map(lambda x: (read_pulse_file('V', x, 1)), \
            pulse_id_array))
        tlp_i = np.asarray( map(lambda x: (read_pulse_file('I', x, 1)), \
            pulse_id_array) )
        time_array = read_pulse_file('I', 1, 0)
        delta_t = time_array[1] - time_array[0]

        self.data['tlp_pulses'] = np.array((tlp_v, tlp_i))
        self.data['delta_t'] = delta_t * 1e-6

        return None

    @property
    def data_to_num_array(self):
        """ converts the data into a numpy array
        """
        num_data = {}
        for data_name in ('tlp', 'valim_tlp', 'tlp_pulses',
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

    data_str_file = StringIO()
    data_str_file.write(data_str[0])
    data_str_file.reset()
    data = np.loadtxt(data_str_file, delimiter = ',', usecols = (0, 1, 2, 3, 4))
    return data.T

def extract_data_from_tcf(tcf_file_name):
    """ from the .tcf file, username, leak voltage evuation
        point needs to beextracted.
    """
    with open(tcf_file_name, 'U') as tcf_file:
        tcf_file_str = tcf_file.read()
    data = []
    re_str = re.compile('UserName=(.*?)\n')
    user_name = re_str.findall(tcf_file_str)[0]
    data.append(user_name)
    re_str = re.compile('LeakSelectPoint=(.*?)\n')
    leak_select_point = re_str.findall(tcf_file_str)[0]
    re_str = re.compile( 'Voltage' + leak_select_point + '=(.*?)\n')
    leak_select_voltage = re_str.findall(tcf_file_str)[0]
    # if leakvoltage is e.g. 800m replace by 0.8
    if 'm' in leak_select_voltage:
        leak_select_voltage = float(leak_select_voltage.replace('m', ''))*1e-3
    data.append(leak_select_voltage)
    return data

def get_number_of_files_in_dir(pathname):
    """ returns the number of files in a directory """
    file_count = 0
    for files in walk(pathname):
        file_count += len(files)
    return file_count

def read_leak_curves(leak_path):
    """Read *.tld files and
    Return the leakage IV curves
    """
    curves = []
    if osp.isdir(leak_path):
        n_files = get_number_of_files_in_dir(leak_path)
        for index in np.arange(n_files):
            leak_index_filename = 'Leak_'+ str(index)+'.tld'
            leak_file_path = osp.join(leak_path, leak_index_filename)
            with open(leak_file_path, 'r') as leak_file:
                file_str = leak_file.read()
                data_str_file = StringIO()
                data_str_file.write(file_str)
                data_str_file.reset()
                data = np.loadtxt(data_str_file, delimiter = ',', \
                    usecols = (0, 1))
            curves.append(data.T)
    return curves

def data_from_transient_file(filename):
    """ Extracts the data form transient csv files """
    data = np.loadtxt(filename, delimiter = ',', skiprows = 1)
    return data.T


def filecontents(path):
    """ returns the number of common indexes in the transient
        V and I csv files
    """
    log = logging.getLogger('thunderstorm.thunder.importers')
    v_path = osp.join(path, 'OsilloV')
    v_file_list = listdir(v_path)
    i_path = osp.join(path, 'OsilloI')
    i_file_list = listdir(i_path)
    if len(v_file_list) != len(i_file_list):
        log.warn("Current and Voltage waveform mismatch")
    return len(i_file_list)
