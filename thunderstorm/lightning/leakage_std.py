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
Leakage plotting page
"""

import numpy as np
from numpy import ma

from utils import autoscale_visible_lines
import thunderstorm.thunder.leak_evol_calculation as leak_evol_calculation

class LeakFigure(object):
    """A standard leakage figure
    """
    def __init__(self, f_leak, device_name, iv_leak):
        self._graph = {}
        iv_leak = np.asarray(iv_leak)
        fig_leak = f_leak.add_subplot(111)
        fig_leak.grid(True)
        fig_leak.semilogy()
        fig_leak.set_xlabel('Voltage (V)')
        fig_leak.set_ylabel('Current (A)')
        fig_leak.set_title(device_name)
        fig_leak.fmt_xdata = lambda num : "%.2e" % num
        fig_leak.fmt_ydata = lambda num : "%.2e" % num
        # Initialize leakage curves
        fig_leak_curves = []
        idx = iv_leak.shape[0]
        while idx > 0:
            temp, = fig_leak.plot([1], [1])
            fig_leak_curves.append(temp)
            idx -= 1
        yleak = abs(iv_leak[:,1,:])
        self.noise_floor_limit = (yleak.max().max(), yleak.min().min())
        #Graph related attributes
        self._graph['leak_points'], = fig_leak.plot([1], [1],
                                                   'g-o', markersize=6 )
        self._graph['leak_curves'] = fig_leak_curves
        self._graph['fig_leak'] = fig_leak
        self.visible_flags = iv_leak.shape[0] * [True]
        #self.visible_flags[2] = False
        self.iv_leak = iv_leak
        self.figure = f_leak
        self._leak_evol_points_position = 0
        self.noise_floor = self.noise_floor_limit[1]
        return

    def update_leak_evol_points(self):
        """Update evol points plot for next time drawing """
        data = leak_evol_calculation.point_evol(self.iv_leak,
                                                self._leak_evol_points_position)
        noise_floor = self._noise_floor
        xdata = data[0]
        ydata = ma.array(abs(data[1]))
        ydata.mask = ydata < noise_floor
        ydata.fill_value = noise_floor
        mask = np.array(self.visible_flags)
        self._graph['leak_points'].set_data(xdata[mask],
                                            ydata.filled()[mask])
        return

    def update_leakage_curves(self):
        """Update leakage curves for next time drawing """
        visible_flags = self.visible_flags
        for idx, flag in enumerate(visible_flags):
            self._graph['leak_curves'][idx].set_visible(flag)
        autoscale_visible_lines(self._graph['fig_leak'])
        return

    def draw(self):
        self.figure.canvas.draw()
        return

    @property
    def evol_points_position(self):
        return self._leak_evol_points_position

    @evol_points_position.setter
    def evol_points_position(self, new_position):
        self._leak_evol_points_position = new_position
        self.update_leak_evol_points()
        self.draw()
        return

    @property
    def noise_floor(self):
        return self._noise_floor

    @noise_floor.setter
    def noise_floor(self, new_value):
        limit_min, limit_max = self.noise_floor_limit
        if new_value <= limit_min and new_value >= limit_max:
            self._noise_floor = new_value
            noise_floor = self._noise_floor
            iv_leak = self.iv_leak
            for idx in xrange(iv_leak.shape[0]):
                xdata = iv_leak[idx][0]
                ydata = ma.array(abs(iv_leak[idx][1]))
                ydata.mask = ydata < noise_floor
                ydata.fill_value = noise_floor
                self._graph['leak_curves'][idx].set_data(xdata,
                                                         ydata.filled())
            self.update_leakage_curves()
            self.update_leak_evol_points()
            self.draw()
        else:
            raise ValueError
