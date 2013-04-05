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
from os.path import realpath

import numpy as np
import h5py

from .pulses import IVTime


class Index(object):
    def __init__(self, data, idx):
        self._data = data
        self._idx = idx

    def __getitem__(self, index):
        return self._data[index, self._idx]


class H5IVTime(object):
    """Contain the transient waveforms
    """
    def __init__(self, droplet=None):
        if not(droplet.__class__ is h5py.Group):
            raise TypeError("droplet must be an h5py.Group object")
        self.droplet = droplet

    def import_ivtime(self, pulses):
        if not(pulses.__class__ is IVTime):
            raise TypeError("Must give an IVTime object")
        alldat = np.transpose(np.array((pulses.voltage, pulses.current)),
                              (1, 0, 2))
        self.droplet.create_dataset('IVTime',
                                    data=alldat,
                                    chunks=(2, 1, pulses.pulses_length),
                                    # Fist dim is pulse id, 2nd I ou V
                                    compression='gzip',
                                    compression_opts=9)
        self.droplet.create_dataset('Valim', data=pulses.valim,
                                    chunks=True, compression='gzip',
                                    compression_opts=9)
        self.droplet.attrs['delta_t'] = pulses.delta_t
        self.droplet['offsets_t'] = pulses.offsets_t

    @property
    def voltage(self):
        return Index(self.droplet['IVTime'], 0)

    @property
    def current(self):
        return Index(self.droplet['IVTime'], 1)

    @property
    def pulses_length(self):
        return self.droplet['IVTime'].shape[2]

    @property
    def pulses_nb(self):
        return self.droplet['IVTime'].shape[0]

    @property
    def valim(self):
        return self.droplet['Valim']

    @property
    def delta_t(self):
        return self.droplet.attrs['delta_t']

    @property
    def offsets_t(self):
        return self.droplet['offsets_t']


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
        data_fmt = np.dtype([('Voltage', (np.float64, length)),
                             ('Current', (np.float64, length))])
        data = np.zeros(1, data_fmt)
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


class _RawTLPdata(object):
    def __init__(self):
        self._tester_name = None
        self._pulses_data = None
        self._iv_leak_data = None
        self._device_name = None
        self._tlp_curve = None
        self._leak_evol = None
        self._original_data_file_path = None

    def __repr__(self):
        message = "%g pulses \n" % self.pulses.pulses_nb
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


class H5RawTLPdata(_RawTLPdata):
    """All measurement data: device name, pulses, TLP curve, leakage ...
    from the h5File are made accessible throught this class
    """
    def __init__(self, droplet=None):
        if not(droplet.__class__ is h5py.Group):
            raise TypeError("group must be an h5py.Group object")
        _RawTLPdata.__init__(self)
        self.droplet = droplet

        if 'IVTime' in droplet.keys():
            self._pulses_data = H5IVTime(droplet)
            self.has_transient_pulses = True
        else:
            self.has_transient_pulses = False

        if 'leak_evol' in droplet.keys():
            self.has_leakage_evolution = True
            self._leak_evol = droplet['leak_evol']
        else:
            self.has_leakage_evolution = False
            self._leak_evol = None

        if 'iv_leak' in droplet.keys():
            self.has_leakage_ivs = True
            self._iv_leak_data = droplet['iv_leak']
        else:
            self.has_leakage_ivs = False
            self._iv_leak_data = None

        self._tlp_curve = droplet['tlp_curve']
        self._device_name = droplet.attrs['device_name']
        self._tester_name = droplet.attrs['tester_name']
        self._original_data_file_path = droplet.attrs['original_file_path']


class RawTLPdata(_RawTLPdata):
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
        if not(pulses.__class__ is IVTime):
            raise TypeError("Pulses must be an IVTime object")
        _RawTLPdata.__init__(self)
        self._device_name = device_name
        self._pulses_data = pulses
        #TODO this should be reworked to handle None
        #if no transient data is available
        if pulses.pulses_length == 0 or pulses.pulses_nb == 0:
            self.has_transient_pulses = False
        else:
            self.has_transient_pulses = True

        if (leak_evol is None or len(leak_evol) == 0
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


class Droplet(object):
    """ A Droplet is basically one TLP measurement i.e. a set
        of TLP pulses, a TLP curve, leakages measurement etc...
        A Droplet is base on a hdf5 file group
    """
    def __init__(self, h5group):
        self._h5group = h5group
        self._exp_name = h5group.name[1:]
        self._raw_data = H5RawTLPdata(h5group)

    def __repr__(self):
        message = "Experiement: "
        message += self._exp_name + "\n"
        return message

    @property
    def full_file_name(self):
        return realpath(self._h5group.file.filename)

    @property
    def raw_data(self):
        return self._raw_data

    @property
    def exp_name(self):
        return self._exp_name

    @exp_name.setter
    def exp_name(self, value):
        raise NotImplemented
        #self._exp_name = value
