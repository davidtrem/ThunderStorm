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
from thunderstorm.thunder.tlp import Experiment

class ImportPlugin(object):
    """Generic import plugin class"""
    label = "Unknown"
    file_ext = "*.*"

    def __init__(self):
        pass

    def import_data(self,filename):
        """Must return the data to be plotted
        return a RawTLPdata instance
        """
        raise NotImplementedError

    def __repr__(self):
        """
        Give the name of the plugin class
        """
        return "%s" % (self.__class__.__name__)

    def load(self, file_name, experiment_name=""):
        """import data and pack them in an experiment
        return an experiment
        """
        raw_data = self.import_data(file_name)
        return Experiment(raw_data, experiment_name)


def _init():
    """Activate importer plugins
    available in importers this directory
    """
    import plug_laas
    import plug_oryx
    import plug_hppi
    import plug_serma
    import plug_hanwa
    import plug_barth
    plug_dict = {}
    for plug in ImportPlugin.__subclasses__():
        plug_dict[plug.label] = plug
    return plug_dict

plug_dict = _init()
del _init
