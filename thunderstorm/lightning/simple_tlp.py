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

class PulsesFigCanvas(object):
    def __init__(self, figure, pulses, title=""):
        pulse_plot = figure.add_subplot(111)
        pulse_plot.grid(True)
        pulse_plot.set_xlabel("index")
        pulse_plot.set_ylabel("Voltage")
        #also need to add currents
        pulse_plot.set_title(title)
        pulse_plot.plot(pulses.voltage)
        self.plot = pulse_plot
        self.draw = figure.canvas.draw

