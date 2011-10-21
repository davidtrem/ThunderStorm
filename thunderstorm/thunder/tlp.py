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

""" tlp data
"""

import numpy as np
from thunderstorm.thunder.pulses import IVTime

class TLPcurve(object):
    """The data for a TLP curve
    """
    def __init__(self, current, voltage):
        """current is a 1D numpy array
        voltage is a 1D numpy array
        of same length
        """
        assert current.__class__ == np.ndarray
        assert voltage.__class__ == np.ndarray
        assert current.shape == voltage.shape
        assert len(current.shape) == 1
        length = current.shape[0]
        format = np.dtype([('Voltage', (np.float64, length)),
                            ('Current', (np.float64, length))])
        data = np.zeros(1, format)
        data['Voltage'] = voltage
        data['Current'] = current
        self._data = data

    @property
    def current(self):
        """Return the current array of the TLP curve
        """
        return self._data['Current']

    @property
    def voltage(self):
        """Return the voltage array of the TLP curve
        """
        return self._data['Voltage']

    @property
    def data(self):
        """Return a copy of the raw tlp curve data
        """
        return self._data.copy()


class RawTLPdata(object):
    """All measurement data: device name, pulses, TLP curve, leakage ...
    are packed in this class
    """

    def __init__(self, device_name, pulses,
                 iv_leak, tlp_curve, leak_evol,
                 file_path, tester_name=None):
        """
        Parameters
        ----------
        device_name: string
            The device name

        pulses:
            A set of TLP IVTime pulses

        iv_leak:
            Leakage curves data

        tlp_curve:
            TLP curve data
        """
        if not(type(device_name) is str):
            raise TypeError("Device name must be a string")
        self._device_name = device_name

        if not(pulses.__class__ is IVTime):
            raise TypeError("Pulses must be an IVTime object")
        self._pulses_data = pulses
        #TODO this should be reworked to handle None
        #if no transient data is available
        if pulses.pulses_length == 0 or pulses.pulses_nb == 0:
            self.has_transient_pulses = False
        else:
            self.has_transient_pulses = True

        if (leak_evol == None or len(leak_evol) == 0
            or np.alltrue(leak_evol == 0)):
            self.has_leakage_evolution = False
            self._leak_evol = None
        else:
            self.has_leakage_evolution = True
            self._leak_evol = leak_evol

        if len(iv_leak) == 0:
            self.has_leakage_ivs = False
            self._iv_leak_data = None
        else:
            self.has_leakage_ivs = True
            self._iv_leak_data = iv_leak

        self._tlp_curve = tlp_curve
        self._tester_name = tester_name
        self._original_data_file_path = file_path

    def __repr__(self):
        message = "%g pulses \n" %self.pulses.pulses_nb
        message += "Original file: " + self.original_file_name
        return message

    @property
    def tester_name(self):
        return self._tester_name

    @property
    def pulses(self):
        """Pulses data """
        return self._pulses_data

    @property
    def iv_leak(self):
        """Leakage curve data """
        return self._iv_leak_data

    @property
    def device_name(self):
        return self._device_name

    @property
    def tlp_curve(self):
        return self._tlp_curve

    @property
    def leak_evol(self):
        return self._leak_evol

    @property
    def original_file_name(self):
        return self._original_data_file_path


class Experiment(object):

    def __init__(self, raw_data, exp_name="Unknown"):
        assert raw_data.__class__ is RawTLPdata
        self._raw_data = raw_data
        self._exp_name = exp_name
        return

    def __repr__(self):
        message = "Experiement: "
        message += self._exp_name +"\n"
        return message

    @property
    def raw_data(self):
        return self._raw_data

    @property
    def exp_name(self):
        return self._exp_name

    @exp_name.setter
    def exp_name(self, value):
        self._exp_name = value
