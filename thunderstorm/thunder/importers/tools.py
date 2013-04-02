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
Define the plugin class mother of all plugins.
Also define the functions to be implemented
to build a plugin.
init populate the ImportPlugin class with the plugins class from plug dir.
Only plugin files starting with "plug" followed by underscore and ending with
".py" are taken into account.
import_plugs variable contains all the import plugins

"""

from os.path import basename, splitext

from ..tlp import Droplet, H5IVTime


class ImportPlugin(object):
    """Generic import plugin class"""
    label = "Unknown"
    file_ext = "*.*"

    def __init__(self):
        pass

    def import_data(self, filename):
        """Must return the data to be plotted
        return a RawTLPdata instance
        """
        raise NotImplementedError

    def __repr__(self):
        """
        Give the name of the plugin class
        """
        return "%s" % (self.__class__.__name__)

    def raw_data_from_file(self, file_name):
        return self.import_data(file_name)

    @staticmethod
    def load_in_droplet(raw_data, h5file, exp_name=None):
        if exp_name is None:
            exp_name = splitext(basename(raw_data.original_file_name))[0]
        h5group = h5file.create_group(exp_name)
        if raw_data.has_transient_pulses:
            data = H5IVTime(h5group)
            data.import_ivtime(raw_data.pulses)
        h5group['tlp_curve'] = raw_data.tlp_curve
        h5group.attrs['device_name'] = raw_data.device_name
        h5group.attrs['tester_name'] = raw_data.tester_name
        h5group.attrs['original_file_path'] = str(raw_data.original_file_name)
        if raw_data.has_leakage_evolution:
            h5group['leak_evol'] = raw_data.leak_evol
        if raw_data.has_leakage_ivs:
            h5group['iv_leak'] = raw_data.iv_leak
        h5file.flush()
        return Droplet(h5group)

    def load(self, file_name, exp_name=None, h5file=None):
        """import data and pack them in a droplet
        return the droplet
        """
        raw_data = self.raw_data_from_file(file_name)
        return self.load_in_droplet(raw_data, h5file, exp_name)


def _init():
    """Activate importer plugins
    available in this directory
    """
    from . import plug_laas
    from . import plug_oryx
    from . import plug_hppi
    from . import plug_serma
    from . import plug_hanwa
    from . import plug_barth
    plug_dict = {}
    for plug in ImportPlugin.__subclasses__():
        plug_dict[plug.label] = plug
    return plug_dict

plug_dict = _init()
del _init
