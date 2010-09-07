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

from thunderstorm.thunder.importers.tools import plug_dict


class Load(object):
    """Use Load.Tester_plugin_name('filename') to load a measurement from
    a given tester.
    Return an experiment.
    Load.plug_list return the available a list of tester import plugins
    """
    plug_list = plug_dict.keys()

# instantiate import plugins
for plug_name in Load.plug_list:
    setattr(Load, plug_name, plug_dict[plug_name]().load)
