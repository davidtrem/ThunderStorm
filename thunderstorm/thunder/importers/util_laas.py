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
Read the data from LAAS TLP setup file
"""

import numpy as npy
import logging

class ReadLAAS(object):
    """
    Read LAAS TLP data and do few treatment for TLPtools
    """
    def __init__(self, datafile):
        self.datafile = datafile
        self.data = {}
        self.identification = ""
        self.read_data_from_file()
        #self.check_data_consistency()

    def read_column(self, nb_col=2):
        """
        Read data in column util an empty line is found.
        Return the nb_col column of the readed data
        """
        datafile = self.datafile
        dat_line = datafile.readline()
        if dat_line[:-1] == "":
            return [[0.0, 0.0]]
        data = []
        while dat_line:
            dat = dat_line.split()[0:nb_col+1]
            dat = [float(x) for x in dat]
            data.append(dat)
            dat_line = datafile.readline()[:-1]
        return data

    def read_data_from_file(self):
        """
        Read and extract the data from LAAS TLP sequentially
        """
        log = logging.getLogger('thunderstorm.thunder.importers')
        datafile = self.datafile
        data = self.data
        identification = self.identification
        data['valim_tlp'] = []
        data['tlp_pulses'] = []
        data['valim_leak'] = []
        data['leak_data'] = []

        line = datafile.readline()
        if line[0:16] != "Identification :":
            log.warn("Wrong file format")
            return
        identification = line[17:-1]
        log.debug("Identification:" + identification)
        datafile.readline()

        log.debug("Reading TLP curve")
        data['tlp'] = self.read_column()
        nb_pulse = len(data['tlp'])
        if nb_pulse == 0:
            log.debug("no data found")
        else:
            log.debug("Reading TLP pulses")
            while 1:
                line = datafile.readline()
                element = line.split('=')
                if element[0] != 'Valim (V)':
                    break
                alim = float(element[1][:-1])
                data['valim_tlp'].append(alim)
                datafile.readline()
                data['tlp_pulses'].append(self.read_column())

        log.debug("Reading static measurements")
        while 1:
            line = datafile.readline()
            if line[:-1] == "Premiere mesure statique":
                break
        datafile.readline()
        data['valim_leak'].append(0)
        data['leak_data'].append(self.read_column(2))
        while 1:
            line = datafile.readline()
            element = line.split('=')
            if element[0] != 'Valim (V)':
                break
            alim = float(element[1][:-1])
            data['valim_leak'].append(alim)
            datafile.readline()
            data['leak_data'].append(self.read_column(2))
        self.datafile.close()
        return None

    def check_data_consistency(self):
        """
        Chekc if data are consistent
        """
        raise NotImplementedError
        return None

    @property
    def data_to_num_array(self):
        num_data = {}
        for data_name in ('tlp', 'valim_tlp', 'tlp_pulses',
                          'valim_leak'):
            num_data[data_name] = npy.array(self.data[data_name])
        num_data['leak_data'] = [npy.array(dat).transpose()
                                 for dat in self.data['leak_data']]
        num_data['tlp'] = num_data['tlp'].transpose()[1:]
        num_data['tlp_pulses'] = npy.array([x.transpose()
                                            for x in num_data['tlp_pulses']])
        return num_data
