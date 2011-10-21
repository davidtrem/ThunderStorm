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
Utils to read data from Oryx TLP setup file
This file was greatly improved with the help of Justin Katz
"""

import numpy as np
from zipfile import ZipFile
from cStringIO import StringIO
import re
import logging
import os
import glob


class ReadOryx(object):
    """
    Read Oryx TLP data and do few treatment
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
        # Transient datas
        try:
            oryx_zip = OryxTransientZip(base_name + '.zip')
        except IOError:
            data['waveform_available'] = False
            data['tlp_pulses'] = []
            data['valim_tlp'] = []
            data['delta_t'] = 0
            data['offsets_t'] = 0
        else:
            data['waveform_available'] = True
            (base_name, volt_list) = oryx_zip.filecontents
            tlp_v = []
            offsets_t = []
            for pulse_voltage in volt_list:
                filename = base_name + '_TlpVolt_' + pulse_voltage + 'V.wfm'
                transdata = oryx_zip.data_from_transient_file(filename)
                tlp_v.append(transdata[1])
                offsets_t.append(transdata[0][0])
            tlp_v = np.asarray(tlp_v)
            offsets_t = np.asarray(offsets_t)
            tlp_i = []
            for pulse_voltage in volt_list:
                filename = base_name + '_TlpCurr_' + pulse_voltage + 'V.wfm'
                tlp_i.append(oryx_zip.data_from_transient_file(filename)[1])
            tlp_i = np.asarray(tlp_i)
            time_data = oryx_zip.data_from_transient_file(filename)[0]
            delta_t = time_data[1] - time_data[0]
            data['tlp_pulses'] = np.array((tlp_v, tlp_i))
            data['valim_tlp'] = volt_list
            data['delta_t'] = delta_t * 1e-9
            data['offsets_t'] = offsets_t * 1e-9

    @property
    def data_to_num_array(self):
        num_data = {}
        for data_name in ('tlp', 'valim_tlp', 'tlp_pulses',
                          'valim_leak', 'leak_evol', 'offsets_t'):
            num_data[data_name] = np.array(self.data[data_name])
        num_data['leak_data'] = self.data['leak_data']
        num_data['delta_t'] = self.data['delta_t']
        num_data['waveform_available'] = self.data['waveform_available']
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
    curves = []
    try:
        with open(filename, 'U') as data_file:
            whole_data = data_file.read()

        block_re_str = r"^(\[DATA\])(.*?)(?=\[DATA\]|\Z)"
        block_re = re.compile(block_re_str, re.S | re.M)
        blocks = block_re.findall(whole_data)

        data_txt = ['\n'.join(block[1].split('\n')[3:-1]) for block in blocks]
        for data in data_txt:
            string_file = StringIO()
            string_file.write(data)
            string_file.reset()
            curves.append(np.loadtxt(string_file, delimiter=',').T[1:])
    except IOError:
        log = logging.getLogger('thunderstorm.thunder.importers')
        log.warn("No leakage curves available")
    finally:
        return curves


class OryxTransientZip(object):
    """
    Utils to extract data from oryx zip files
    Waveforms can be stored in either a zip file with the same name as
    the .tsr file, or it can be stored in a subfolder with the same name
    as the .tsr file.
    Note: Oryx deprecated saving as zip
    """
    def __init__(self, zfilename):
        #According to Justin unziped transient files
        #subfolder is now the default
        #This version create the zip file if it does not exists
        #and remove it when done
        self.zipcreated = ''
        if os.path.exists(zfilename):
            pass
        elif os.path.exists(zfilename[:-4]):
            #if a folder exist create the zip file
            zfile = ZipFile(zfilename, 'w')
            for filename in glob.glob(zfilename[:-4]+'/*'):
                zfile.write(filename, os.path.basename(filename))
            zfile.close()
            self.zipcreated = zfilename
        else:
            self.zipcreated = 'No transient data'
            raise IOError("NoTransientFiles")
        self.zfile = ZipFile(zfilename)

    def __del__(self):
        if self.zipcreated != 'No transient data':
            self.zfile.close()
            #remove the zip file if created here
            if self.zipcreated != '':
                os.remove(self.zipcreated)

    def data_from_transient_file(self, filename):
        full_file = self.zfile.read(filename)
        data_string = '\n'.join(full_file.split('\r\n')[13:-2])
        data_string_file = StringIO()
        data_string_file.write(data_string)
        data_string_file.reset()
        return np.loadtxt(data_string_file, delimiter=',').T

    @property
    def list_transient_file(self):
        file_list = self.zfile.namelist()
        return file_list

    @property
    def supply_voltage_list(self):
        """The TLP supply voltages list

        Return the TLP supply voltage list
        from the filenames in the zip file.

        Returns
        -------
        Return a list of voltages (list of string)
        """
        # filename format
        # for TLP voltage: 04-29-09_05'40'45_PM_TlpVolt_90V.wfm
        # for TLP current: 04-29-09_05'40'45_PM_TlpCurr_90V.wfm
        voltages_dict = {'TlpCurr' : [], 'TlpVolt' : [],
                         'TlpVMonCh3' : [], 'TlpVMonCh4' : [],
                         'TlpVoltCh3' : [], 'TlpVoltCh4' : []}
        for filename in self.zfile.namelist():
            if filename[-4:] == ".wfm":
                elems = filename[:-5].split('_')
                voltages_dict[elems[3]].append(elems[4])
        voltages_dict['TlpCurr'].sort(key=float)
        voltages_dict['TlpVolt'].sort(key=float)
        if voltages_dict['TlpCurr'] != voltages_dict['TlpVolt']:
            log = logging.getLogger('thunderstorm.thunder.importers')
            log.warn("Current and Voltage waveform mismatch")
        return voltages_dict['TlpCurr']

    @property
    def filecontents(self):
        volt_list = self.supply_voltage_list
        basename = '_'.join(self.zfile.namelist()[0].split('_')[0:3])
        return (basename, volt_list)

