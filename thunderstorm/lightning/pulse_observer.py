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

import numpy as np

class TLPPickFigure(object):
    """A simple TLP figure
    """
    def __init__(self, figure, tlp_curve_data,
                 pulses_figure, title=""):
        #create the pulses figure
        self.pulse_fig = pulses_figure
        tlp_plot = figure.add_subplot(111)
        tlp_plot.grid(True)
        tlp_plot.set_xlabel("Voltage (V)")
        tlp_plot.set_ylabel("Current (A)")
        tlp_plot.set_title(title)
        volt = tlp_curve_data[0]
        curr = tlp_curve_data[1]
        tlp_plot.plot(volt, curr, '-')
        selected_flag = np.zeros(volt.shape[0], dtype=np.bool)
        points, = tlp_plot.plot(volt, curr, 'o', picker=5)
        points.identity = "Who am I?"
        selected_point, = tlp_plot.plot(volt[selected_flag],
                                       curr[selected_flag], 'ro')
        figure.canvas.mpl_connect('pick_event', self.onpickevent)
        figure.canvas.draw()
        self.figure = figure
        self.selected_flag = selected_flag
        self. selected_point = selected_point
        self.volt = volt
        self.curr = curr
        
    def onpickevent(self, event):
        if event.mouseevent.button == 1:
            #ax1.set_autoscale_on(False)
            selected_flag = self.selected_flag
            ind = event.ind
            selected_flag[ind] = not selected_flag[ind]
            print 'onpick3 scatter'#, ind, np.take(x, ind), np.take(y, ind)
            self.selected_point.set_data(self.volt[selected_flag], 
                                         self.curr[selected_flag])
            self.pulse_fig.update(selected_flag)
            self.figure.canvas.draw()  
            

class PulsesFigure(object):
    def __init__(self, figure, pulses, title=""):
        time = np.arange(pulses.pulses_length) * pulses.delta_t
        offseted_time = pulses.offsets_t + time[:, np.newaxis]
        self.offseted_time = offseted_time * 1e9
        # time in nanosecond
        self.pulses = pulses
        # V curves
        v_pulse_plot = figure.add_subplot(211)
        v_pulse_plot.grid(True)
        v_pulse_plot.set_ylabel("Voltage")
        v_pulse_plot.set_title(title)
        # I curves
        i_pulse_plot = figure.add_subplot(212, sharex=v_pulse_plot)
        i_pulse_plot.grid(True)
        i_pulse_plot.set_xlabel("time (ns)")
        i_pulse_plot.set_ylabel("Current")
        figure.canvas.draw()
        self.figure = figure
        self.v_pulse_plot = v_pulse_plot
        self.i_pulse_plot = i_pulse_plot
        
    def update(self, selected_flag):
        self.v_pulse_plot.clear()
        self.v_pulse_plot.plot(self.offseted_time,
                               self.pulses.voltage[selected_flag].T)
        self.i_pulse_plot.clear()
        self.i_pulse_plot.plot(self.offseted_time,
                               self.pulses.current[selected_flag].T)
        self.figure.canvas.draw()
        