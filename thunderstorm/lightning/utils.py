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
Various utility functions
"""
import matplotlib

def autoscale_visible_lines(axs):
    """
    Function to autoscale only on visible lines.
    """
    mplt_ver = [int(elem) for elem in matplotlib.__version__.split('.')[0:2]]
    ignore = True
    for line in (axs.lines):
        if not line.get_visible():
            continue #jump to next line if this one is not visible
        if mplt_ver[0] == 0 and mplt_ver[1] < 98:
            axs.dataLim.update_numerix(line.get_xdata(),
                                       line.get_ydata(),
                                       ignore)
        else:
            axs.dataLim.update_from_data_xy(line.get_xydata(),
                                            ignore)
        ignore = False
    axs.autoscale_view()
    return None

def neg_bool_list(a_list):
    return [not elem for elem in a_list]
