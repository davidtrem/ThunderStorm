# -*- coding: utf-8 -*-

# Copyright (C) 2010 Tr�mouilles David

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

import numpy as np

class TLPLeakagePickFigure(object):
    """A simple TLP figure
    """
    def __init__(self, figure, raw_data, title=""):
        tlp_plot = figure.add_axes((0.1, 0.1, 0.35, 0.8))
        tlp_plot.grid(True)
        tlp_plot.set_xlabel("Voltage (V)")
        tlp_plot.set_ylabel("Current (A)")
        tlp_plot.set_title(title)
        volt = raw_data.tlp_curve[0]
        curr = raw_data.tlp_curve[1]
        tlp_plot.plot(volt, curr, '-')
        selected_flag = np.zeros(volt.shape[0], dtype=np.bool)
        selected_flag[0] = True # set first one True
        points, = tlp_plot.plot(volt, curr, 'o', picker=5)
        points.identity = "Who am I?"
        selected_point, = tlp_plot.plot(volt[selected_flag],
                                        curr[selected_flag], 'ro')
        figure.canvas.mpl_connect('pick_event', self.onpickevent)


        self.iv_leak = raw_data.iv_leak
        # curves
        leak_plot = figure.add_axes((0.62, 0.1, 0.35, 0.8))
        leak_plot.set_title("DC Leakage Curves")
        leak_plot.grid(True)
        leak_plot.set_xlabel("Voltage (V)")
        leak_plot.set_ylabel("Current (A)")
        self.figure = figure
        self.leak_plot = leak_plot
        self.selected_flag = selected_flag
        self. selected_point = selected_point
        self.volt = volt
        self.curr = curr
        self.update(selected_flag)


    def onpickevent(self, event):
        if event.mouseevent.button == 1:
            selected_flag = self.selected_flag
            ind = event.ind[0]
            selected_flag[ind] = not selected_flag[ind]
            if not((-selected_flag).all()): # at least one true
                self.selected_point.set_data(self.volt[selected_flag],
                                             self.curr[selected_flag])
                self.selected_point.set_visible(True)
            else:
                self.selected_point.set_visible(False)
            self.update(selected_flag)
            self.figure.canvas.draw()

    def update(self, selected_flag):
        leak_plot = self.leak_plot
        leak_plot.cla()
        leak_plot.set_title("DC Leakage Curves")
        leak_plot.grid(True)
        leak_plot.set_xlabel("Voltage (V)")
        leak_plot.set_ylabel("Current (A)")
        if not((-selected_flag).all()): # if at least one true...
            data = self.iv_leak[selected_flag].T
            leak_plot.plot(data[:,0], data[:,1])
        else:
            pass
            #Should print something on the graph to say "please select
            # a point on TLP plot"
        self.figure.canvas.draw()

