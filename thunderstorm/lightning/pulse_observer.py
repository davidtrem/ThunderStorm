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
Tools to observe transient curves corresponding to TLP points
"""


from tlp_observer import TLPPickFigure
import numpy as np

class TLPPulsePickFigure(TLPPickFigure):
    """
    TLP picking tool showing transient pulses
    """
    def __init__(self, figure, raw_data, title=""):
        # init tlp pick plot
        TLPPickFigure.__init__(self, figure, raw_data, title)
        # pulses figure
        pulses = raw_data.pulses
        time = np.arange(pulses.pulses_length) * pulses.delta_t
        offseted_time = pulses.offsets_t + time[:, np.newaxis]
        # I and V curves
        v_pulse_plot = figure.add_axes((0.55, 0.55, 0.35, 0.35))
        v_pulse_plot.grid(True)
        v_pulse_plot.set_ylabel("Voltage")

        i_pulse_plot = figure.add_axes((0.55, 0.1, 0.35, 0.35),
                                       sharex=v_pulse_plot)
        i_pulse_plot.grid(True)
        i_pulse_plot.set_xlabel("time (ns)")
        i_pulse_plot.set_ylabel("Current")

        # Init object attributes
        self.offseted_time = offseted_time * 1e9 # time in nanosecond
        self.v_pulse_plot = v_pulse_plot
        self.v_pulse_lines = None
        self.i_pulse_plot = i_pulse_plot
        self.i_pulse_lines = None
        self.pulses = raw_data.pulses

    def update(self, selected_flag):
        v_pulse_plot = self.v_pulse_plot
        i_pulse_plot = self.i_pulse_plot
        if self.v_pulse_lines != None:
            for line in self.v_pulse_lines:
                line.remove()
            for line in self.i_pulse_lines:
                line.remove()
        if not((-selected_flag).all()): # if at least one true...
            indexes = np.linspace(0, 1, selected_flag.sum())
            colors = self.color_map(indexes)
            v_pulse_plot.axes.set_color_cycle(colors)
            i_pulse_plot.axes.set_color_cycle(colors)
            time = self.offseted_time.T[selected_flag].T
            pulses = self.pulses
            self.v_pulse_lines = \
                v_pulse_plot.plot(time,
                                  pulses.voltage[selected_flag].T)
            self.i_pulse_lines = \
                i_pulse_plot.plot(time,
                                  pulses.current[selected_flag].T)
        else:
            self.v_pulse_lines = None
            self.i_pulse_lines = None
            #Should print something on the graph to say "please select
            # a point on TLP plot"

