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
Simple TLP curve plot
"""

import numpy as np

class TLPFigure(object):
    """A simple TLP figure
    """
    def __init__(self, figure, tlp_curve_data, title=""):
        tlp_plot = figure.add_subplot(111)
        tlp_plot.grid(True)
        tlp_plot.set_xlabel("Voltage (V)")
        tlp_plot.set_ylabel("Current (A)")
        tlp_plot.set_title(title + "TLP curve")
        tlp_plot.plot(tlp_curve_data[0], tlp_curve_data[1], '-o')
        self.plot = tlp_plot
        self.draw = figure.canvas.draw

class PulsesFigure(object):
    def __init__(self, figure, pulses, title=""):
        # V curves
        v_pulse_plot = figure.add_subplot(211)
        v_pulse_plot.grid(True)
        v_pulse_plot.set_ylabel("Voltage")
        v_pulse_plot.set_title(title)
        v_pulse_plot.plot(pulses.voltage.T)
        # I curves
        i_pulse_plot = figure.add_subplot(212)
        i_pulse_plot.grid(True)
        i_pulse_plot.set_xlabel("index")
        i_pulse_plot.set_ylabel("Current")
        i_pulse_plot.set_title(title)
        i_pulse_plot.plot(pulses.current.T)

        self.v_plot = v_pulse_plot
        self.i_plot = i_pulse_plot
        self.draw = figure.canvas.draw

