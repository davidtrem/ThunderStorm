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

class TLPPulsePickFigure(object):
    """A simple TLP figure
    """
    def __init__(self, figure, raw_data, title=""):
        pulses = raw_data.pulses
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

        # pulses figure
        time = np.arange(pulses.pulses_length) * pulses.delta_t
        offseted_time = pulses.offsets_t + time[:, np.newaxis]
        self.offseted_time = offseted_time * 1e9
        # time in nanosecond
        self.pulses = pulses
        # V curves
        v_pulse_plot = figure.add_axes((0.55, 0.55, 0.35, 0.35))
        # I curves
        i_pulse_plot = figure.add_axes((0.55, 0.1, 0.35, 0.35),
                                       sharex=v_pulse_plot)
        self.figure = figure
        self.v_pulse_plot = v_pulse_plot
        self.i_pulse_plot = i_pulse_plot
        self.selected_flag = selected_flag
        self. selected_point = selected_point
        self.volt = volt
        self.curr = curr
        self.update(selected_flag)


    def onpickevent(self, event):
        if event.mouseevent.button == 1:
            #ax1.set_autoscale_on(False)
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
        v_pulse_plot = self.v_pulse_plot
        i_pulse_plot = self.i_pulse_plot
        v_pulse_plot.hold(False)
        i_pulse_plot.hold(False)
        if not((-selected_flag).all()): # if at least one true...
            v_pulse_plot.plot(self.offseted_time.T[selected_flag].T,
                              self.pulses.voltage[selected_flag].T, 'b')
            v_pulse_plot.grid(True)
            v_pulse_plot.set_ylabel("Voltage")
            v_pulse_plot.set_visible(True)

            i_pulse_plot.plot(self.offseted_time.T[selected_flag].T,
                              self.pulses.current[selected_flag].T, 'b')
            i_pulse_plot.grid(True)
            i_pulse_plot.set_xlabel("time (ns)")
            i_pulse_plot.set_ylabel("Current")
            i_pulse_plot.set_visible(True)
        else:
            v_pulse_plot.set_visible(False)
            i_pulse_plot.set_visible(False)
        self.figure.canvas.draw()


class PulsesFigure(object):
    def __init__(self, figure, pulses, title=""):
        time = np.arange(pulses.pulses_length) * pulses.delta_t
        offseted_time = pulses.offsets_t + time[:, np.newaxis]
        self.offseted_time = offseted_time * 1e9
        # time in nanosecond
        self.pulses = pulses
        # V curves
        v_pulse_plot = figure.add_axes((0.55, 0.55, 0.35, 0.35))
        # I curves
        i_pulse_plot = figure.add_axes((0.55, 0.1, 0.35, 0.35),
                                       sharex=v_pulse_plot)
        figure.canvas.draw()
        self.figure = figure
        self.v_pulse_plot = v_pulse_plot
        self.i_pulse_plot = i_pulse_plot

    def update(self, selected_flag):
        v_pulse_plot = self.v_pulse_plot
        i_pulse_plot = self.i_pulse_plot
        v_pulse_plot.hold(False)
        i_pulse_plot.hold(False)
        if not((-selected_flag).all()): # if at least one true...
            v_pulse_plot.plot(self.offseted_time.T[selected_flag].T,
                              self.pulses.voltage[selected_flag].T, 'b')
            v_pulse_plot.grid(True)
            v_pulse_plot.set_ylabel("Voltage")
            v_pulse_plot.set_visible(True)

            i_pulse_plot.plot(self.offseted_time.T[selected_flag].T,
                              self.pulses.current[selected_flag].T, 'b')
            i_pulse_plot.grid(True)
            i_pulse_plot.set_xlabel("time (ns)")
            i_pulse_plot.set_ylabel("Current")
            i_pulse_plot.set_visible(True)
        else:
            v_pulse_plot.set_visible(False)
            i_pulse_plot.set_visible(False)
        self.figure.canvas.draw()

