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
Various way to calculate leakage evolution
"""

from numpy import log, absolute
import numpy as npy

def point_evol(iv_leak, evol_point):
    """
    Return the voltage and current evolution at the point define in the given
    measure.
    """
    voltage = iv_leak[:, 0, evol_point]
    current = iv_leak[:, 1, evol_point]
    return (voltage, current)


def sum_var(iv_leak):
    """
    Return the relative evolution of the integral of the
    absolute value of the leakage for a given measurement.
    """
    evol = npy.sum(log(absolute(iv_leak[:, 0]) + 1e-60), axis=1)
    relative_evol = (evol - evol[0]) / abs(evol[0]) * 100
    return relative_evol

