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
Define several classes to manipulate a set of TLP measurement
"""
from __future__ import division

import numpy as np
from numpy.fft import rfft, irfft


class PulseSet(object):
    """
    Generic class for a set of pulses
    """
    def __init__(self):
        pass

    @property
    def pulses_length(self):
        return self._data[0][1].shape[0]

    @property
    def pulses_nb(self):
        return self._data.shape[0]

    @property
    def valim(self):
        return self._data['Valim']

    @valim.setter
    def valim(self, value):
        self._data['Valim'] = value


class TimePulseSet(PulseSet):
    """
    """
    def __init__(self, pulses_length=2**2, pulses_nb=2, delta_t=1,
                 data1='data1', data2='data2'):
        PulseSet.__init__(self)
        format = np.dtype([('Valim', np.float32),
                           (data1, (np.float64, pulses_length)),
                           (data2, (np.float64, pulses_length))])
        self._data = np.empty(pulses_nb, format)
        self._delta_t = delta_t

    def to_freq(self, data_type):
        #self._data1 and self._data2 need to be defined by the object
        delta_f = 1 / (self.delta_t * self.pulses_length)
        data1, data2 = self._data.dtype.names[1:3]
        data1_freq = rfft(self._data[data1])
        data2_freq = rfft(self._data[data2])
        freq_pulses_length = data1_freq.shape[1]
        pulses_freq = data_type(freq_pulses_length, self.pulses_nb, delta_f)
        pulses_freq._data['Valim'] = self.valim
        pulses_freq._data[data1] = data1_freq
        pulses_freq._data[data2] = data2_freq
        return pulses_freq

    @property
    def delta_t(self):
        return self._delta_t

    @delta_t.setter
    def delta_t(self, val):
        self._delta_t = val


class FreqPulseSet(PulseSet):
    """
    """
    def __init__(self, pulses_length=2**2, pulses_nb=2, delta_f=1,
                 data1='data1', data2='data2'):
        PulseSet.__init__(self)
        format = np.dtype([('Valim', np.float32),
                           (data1, (np.complex128, pulses_length)),
                           (data2, (np.complex128, pulses_length))])
        self._data = np.empty(pulses_nb, format)
        self._delta_f = delta_f

    def to_time(self, data_type):
        parity = self.pulses_length % 2
        print parity
        delta_t =  0.5/((self.pulses_length-parity) * self.delta_f)
        data1, data2 = self._data.dtype.names[1:3]
        data1_time = irfft(self._data[data1])
        data2_time = irfft(self._data[data2])
        time_pulses_length = data1_time.shape[1]
        pulses_time = data_type(time_pulses_length, self.pulses_nb, delta_t)
        pulses_time._data['Valim'] = self.valim
        pulses_time._data[data1] = data1_time
        pulses_time._data[data2] = data2_time
        return pulses_time

    @property
    def delta_f(self):
        return self._delta_f


#----------------------------------
# Current Voltage representation

class _IV(object):
    def __init__(self, data_type, pulses_length, pulses_nb, delta_t,):
        data_type.__init__(self, pulses_length, pulses_nb, delta_t,
                           'Voltage', 'Current')

    @property
    def voltage(self):
        return self._data['Voltage']

    @voltage.setter
    def voltage(self, value):
        self._data['Voltage'] = value

    @property
    def current(self):
        return self._data['Current']

    @current.setter
    def current(self, value):
        self._data['Current'] = value


class IVTime(TimePulseSet, _IV):
    """
    """
    def __init__(self, pulses_length=2**2, pulses_nb=2, delta_t=1):
        _IV.__init__(self, TimePulseSet, pulses_length,
                    pulses_nb, delta_t)

    @property
    def to_freq(self):
        return TimePulseSet.to_freq(self, IVFreq)

    @property
    def to_vinc_ref(self):
        vinc_ref = VIncRefTime(self.pulses_length, self.pulses_nb,
                                   self.delta_t)
        vinc_ref._data['Valim'] = self.valim
        vinc_ref._data['Incident'] = (self.voltage + 50*self.current)/2.0
        vinc_ref._data['Reflected'] = (self.voltage - 50*self.current)/2.0
        return vinc_ref


class IVFreq(FreqPulseSet, _IV):
    """
    """
    def __init__(self, pulses_length=2**2, pulses_nb=2, delta_f=1):
        _IV.__init__(self, FreqPulseSet, pulses_length,
                     pulses_nb, delta_f)

    @property
    def to_time(self):
        return FreqPulseSet.to_time(self, IVTime)


#----------------------------------
# Incident Reflected representation

class _IncRef(object):

    def __init__(self, data_type, pulses_length, pulses_nb, delta_t,):
        data_type.__init__(self, pulses_length, pulses_nb, delta_t,
                           'Incident', 'Reflected')

    @property
    def incident(self):
        return self._data['Incident']

    @property
    def reflected(self):
        return self._data['Reflected']


class VIncRefTime(TimePulseSet, _IncRef):
    """
    """
    def __init__(self, pulses_length=2**2, pulses_nb=2, delta_t=1):
        _IncRef.__init__(self, TimePulseSet, pulses_length,
                    pulses_nb, delta_t)

    @property
    def to_freq(self):
        return TimePulseSet.to_freq(self, VIncRefFreq)

    @property
    def to_iv(self):
        iv = IVTime(self.pulses_length, self.pulses_nb, self.delta_t)
        iv._data['Valim'] = self.valim
        iv._data['Voltage'] = self.incident + self.reflected
        iv._data['Current'] = (self.incident - self.reflected)/50.0
        return iv


class VIncRefFreq(FreqPulseSet, _IncRef):
    """
    """
    def __init__(self, pulses_length=2**2, pulses_nb=2, delta_f=1):
        _IncRef.__init__(self, FreqPulseSet, pulses_length,
                         pulses_nb, delta_f)

    @property
    def to_time(self):
        return FreqPulseSet.to_time(self, VincRefTime)


#----------------------------------
# Incident Reflected Wave representation

class ABTime(TimePulseSet, _IncRef):
    """
    """
    def __init__(self, pulses_length=2**2, pulses_nb=2, delta_t=1):
        _IncRef.__init__(self, TimePulseSet, pulses_length,
                    pulses_nb, delta_t)

    @property
    def to_freq(self):
        return TimePulseSet.to_freq(self, ABFreq)

class ABFreq(FreqPulseSet, _IncRef):
    """
    """
    def __init__(self, pulses_length=2**2, pulses_nb=2, delta_f=1):
        _IncRef.__init__(self, FreqPulseSet, pulses_length,
                         pulses_nb, delta_f)

    @property
    def to_time(self):
        return FreqPulseSet.to_time(self, ABTime)
