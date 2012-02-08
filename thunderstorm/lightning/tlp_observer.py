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
This module contain base utils to observ a TLP curve
"""

import numpy as np
import matplotlib.cm

class TLPPickFigure(object):
    """
    Base class for tlp point picking
    """
    def __init__(self, figure, raw_data, title=""):
        # init tlp plot
        tlp_plot = figure.add_axes((0.1, 0.1, 0.35, 0.8))
        tlp_plot.grid(True)
        tlp_plot.set_xlabel("Voltage (V)")
        tlp_plot.set_ylabel("Current (A)")
        tlp_plot.set_title(title)
        volt = raw_data.tlp_curve[0]
        curr = raw_data.tlp_curve[1]
        tlp_plot.plot(volt, curr, '-')
        tlp_plot.set_autoscale_on(False)
        selected_flag = np.zeros(volt.shape[0], dtype=np.bool)
        points, = tlp_plot.plot(volt, curr, 'o', picker=5)
        points.identity = "Who am I?" #for latter implementation
        figure.canvas.mpl_connect('pick_event', self.onpickevent)
        # init object attributes
        self.selected_flag = selected_flag
        self.figure = figure
        self.tlp_plot = tlp_plot
        self.selected_point = None
        self.volt = volt
        self.curr = curr
        self.color_map = matplotlib.cm.get_cmap('RdYlBu_r')

    def onpickevent(self, event):
        if event.mouseevent.button == 1:
            selected_flag = self.selected_flag
            ind = event.ind[0]
            selected_flag[ind] = not selected_flag[ind]
            if self.selected_point != None:
                self.selected_point.remove()
            if not((-selected_flag).all()): # at least one true
                indexes = np.linspace(0, 1, selected_flag.sum())
                self.selected_point = self.tlp_plot.scatter(self.volt[selected_flag],
                                                            self.curr[selected_flag],
                                                            c=indexes, s=40, zorder=3,
                                                            cmap=self.color_map)
            else:
                self.selected_point = None
            self.update(selected_flag)
            self.figure.canvas.draw()

    def update(self, selected_flag):
        """Must be implemented in child class
        """
        raise NotImplementedError
