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
Utils to read data from SERMA TLP setup file
"""

import zipfile as z
from cStringIO import StringIO
import tarfile as tf
import re
import os
import logging

import numpy as np


class ReadSERMA(object):
    """
    Read SERMA TLP data and do few treatment
    """
    def __init__(self, file_name):
        self.base_file_name = file_name[:-4]
        self.data = {}
        self._read_data_from_files()

    def _read_data_from_files(self):
        base_name = self.base_file_name
        data = self.data
        csv_data = extract_data_from_csv(base_name + '.csv')
        data['valim_leak'] = csv_data[0]
        data['tlp'] = csv_data[1:3]
        data['leak_evol'] = csv_data[3]
        data['leak_data'] = []

        serma_wfm = SERMATransientRead(base_name)
        (wfm_list, volt_list) = serma_wfm.filecontents
        tlp_v = []
        tlp_i = []
        offsets_t = []
        for filename in wfm_list:
            serma_wfm_data = serma_wfm.data_from_transient_file(filename)
            tlp_v.append(serma_wfm_data[1])
            tlp_i.append(serma_wfm_data[2])
            offsets_t.append(serma_wfm_data[0][0])
        time_array = serma_wfm_data[0]
        delta_t = time_array[1] - time_array[0]
        tlp_v = np.asarray(tlp_v)
        tlp_i = np.asarray(tlp_i)
        offsets_t = np.asarray(offsets_t)

        serma_leak = SERMALeakageRead(base_name)
        leak_list = serma_leak.filecontents
        leak_data = []
        for filename in leak_list:
            serma_leak_data = serma_leak.data_from_leakage_file(filename)
            leak_data.append(serma_leak_data)

        if len(leak_data) == len(data['tlp'][0]):
            ref_data = leak_data[0]
            leak_data.insert(0, ref_data)

        data['leak_data'] = leak_data
        data['tlp_pulses'] = np.array((tlp_v, tlp_i))
        data['valim_tlp'] = volt_list
        data['delta_t'] = delta_t * 1e-9
        data['offsets_t'] = offsets_t * 1e-9

        return None

    @property
    def data_to_num_array(self):
        num_data = {}
        for data_name in ('tlp', 'valim_tlp', 'tlp_pulses',
                          'valim_leak', 'leak_evol',
                          'offsets_t', 'leak_data'):
            num_data[data_name] = np.array(self.data[data_name])
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
    test_result_re = re.compile(r'^Index,.*\]\n(.*)', re.S | re.M)
    data_str = test_result_re.findall(tsr_file_str)
    data_str_file = StringIO()
    data_str_file.write(data_str[0])
    data_str_file.reset()
    data = np.loadtxt(data_str_file, delimiter=',', usecols=(1, 2, 3, 4))
    return data.T


class SERMATransientRead(object):
    """Utils to extract Waveform data from SERMA tester files
    """
    def __init__(self, base_dir):
        self.base_dir = os.path.dirname(base_dir)
        self.wfm_location = None  # Determined in filecontents function

    def data_from_transient_file(self, filename):
        if (os.path.isfile(self.wfm_location)
                and tf.is_tarfile(self.wfm_location)):
            tfile = tf.open(self.wfm_location, 'r')
            my_file = tfile.extractfile(filename)
            full_file = my_file.read()
            tfile.close()
        elif z.is_zipfile(self.wfm_location):
            zfile = z.ZipFile(self.wfm_location)
            full_file = zfile.read(filename)
            zfile.close()
        else:
            filepath = os.path.join(self.wfm_location, filename)
            with open(filepath, 'U') as wfm_file:
                full_file = wfm_file.read()
            wfm_file.close()

        data_string = '\n'.join(full_file.split('\r\n'))
        data_string_file = StringIO()
        data_string_file.write(data_string)
        data_string_file.reset()
        return np.loadtxt(data_string_file, delimiter=',', skiprows=1).T

    @property
    def filecontents(self):
        log = logging.getLogger('thunderstorm.thunder.importers')
        is_zip = False
        is_tar = False
        #check location of waveforms
        base_dir = self.base_dir
        if os.path.exists(os.path.join(base_dir, 'WFM')):
            self.wfm_location = os.path.join(base_dir, 'WFM')
            log.debug('waveforms in dir: wfm')
        elif os.path.exists(os.path.join(base_dir, 'HV-Pulse')):
            self.wfm_location = os.path.join(base_dir, 'HV-Pulse')
            log.debug('waveforms in dir: HV-Pulse')
        else:
            found_file = False
            file_list = os.listdir(base_dir)
            for item in file_list:
                if 'transients' in item:
                    self.wfm_location = os.path.join(base_dir, item)
                    if tf.is_tarfile(self.wfm_location):
                        is_tar = True
                        log.debug('waveforms in tar file')
                        found_file = True
                    elif z.is_zipfile(self.wfm_location):
                        is_zip = True
                        log.debug('waveforms in zip file')
                        found_file = True
                    else:
                        log.debug('waveforms in unknown type of file')

            if not found_file:
                log.debug('No waveforms found')

        wfm_list = []
        if is_zip:
            zfile = z.ZipFile(self.wfm_location)
            wfm_list = zfile.namelist()
        elif is_tar:
            tfile = tf.open(self.wfm_location, 'r')
            for info in tfile.getmembers():
                wfm_list.append(info.name)
        else:
            wfm_list = os.listdir(self.wfm_location)
        #filter all .csv files
        wfm_list = [elem for elem in wfm_list if elem.count('.csv')]

        voltages_list = []
        #for filename in wfm_list:
        #    elems = filename[:-5].split('_')
        #    voltages_list.append(elems[1])
        #voltages_list.sort(key=float)
        #sort waveforms according to returned string from get_wfm_number
        wfm_list.sort(key=self.get_wfm_number)
        return (wfm_list, voltages_list)

    def get_wfm_number(self, filename):
        #return first number in filename as an int
        elems = filename.split('.')
        #print( "%s;%i" % (elems[2],int(re.search("\d+",elems[2]).group(0))))
        return int(re.search("\d+", elems[2]).group(0))


class SERMALeakageRead(object):
    """Utils to extract leakage data from SERMA tester files
    """

    def __init__(self, base_dir):
        self.base_dir = os.path.dirname(base_dir)
        self.leak_location = None  # Determined in filecontents function

    def data_from_leakage_file(self, filename):
        if (os.path.isfile(self.leak_location)
                and tf.is_tarfile(self.leak_location)):
            tfile = tf.open(self.leak_location, 'r')
            my_file = tfile.extractfile(filename)
            full_file = my_file.read()
            tfile.close()
        elif z.is_zipfile(self.leak_location):
            zfile = z.ZipFile(self.leak_location)
            full_file = zfile.read(filename)
            zfile.close()
        else:
            filepath = os.path.join(self.leak_location, filename)
            with open(filepath, 'U') as leak_file:
                full_file = leak_file.read()
            leak_file.close()

        data_string = '\n'.join(full_file.split('\r\n'))
        data_string_file = StringIO()
        data_string_file.write(data_string)
        data_string_file.reset()
        return np.loadtxt(data_string_file, delimiter=',', skiprows=1).T

    @property
    def filecontents(self):
        log = logging.getLogger('thunderstorm.thunder.importers')
        is_zip = False
        is_tar = False
        #check location of waveforms
        base_dir = self.base_dir
        if os.path.exists(os.path.join(base_dir, 'IV-FILE')):
            self.leak_location = os.path.join(base_dir, 'IV-FILE')
            log.debug('leakage curve in dir: IV-FILE')
        elif os.path.exists(os.path.join(base_dir, 'Leak-Curve')):
            self.leak_location = os.path.join(base_dir, 'Leak-Curve')
            log.debug('leakage curve in dir: Leak-Curve')
        elif os.path.isfile(os.path.join(base_dir, 'leakages.zip')):
            self.leak_location = os.path.join(base_dir, 'leakages.zip')
            is_zip = True
            log.debug('leakages in zip file')
        elif os.path.isfile(os.path.join(base_dir, 'leakages.tar.gz')):
            self.leak_location = os.path.join(base_dir, 'leakages.tar.gz')
            is_tar = True
            log.debug('leakages in tar file')
        else:
            log.debug('No leakages found')

        leak_list = []
        if is_zip:
            zfile = z.ZipFile(self.leak_location)
            leak_list = zfile.namelist()
        elif is_tar:
            tfile = tf.open(self.leak_location, 'r')
            for info in tfile.getmembers():
                leak_list.append(info.name)
        else:
            leak_list = os.listdir(self.leak_location)

        #filter all .csv files
        leak_list = [elem for elem in leak_list if elem.count('.csv')]

        leak_list.sort(key=self.get_leak_number)
        return (leak_list)

    def get_leak_number(self, filename):
        #return first number in filename as an int
        elems = filename.split('.')
        #print( "%s;%i" % (elems[2],int(re.search("\d+",elems[2]).group(0))))
        return int(re.search("\d+", elems[2]).group(0))
