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
Tools to observe leakage curves corresponding to TLP points
"""

import numpy as np

from .tlp_observer import TLPPickFigure


class TLPLeakagePickFigure(TLPPickFigure):
    """
    TLP picking tool showing leakage ivs
    """
    def __init__(self, figure, raw_data, title=""):
        # init tlp pick plot
        TLPPickFigure.__init__(self, figure, raw_data, title)
        # init leak-curves plot
        leak_plot = figure.add_axes((0.62, 0.1, 0.35, 0.8))
        leak_plot.set_title("DC Leakage Curves")
        leak_plot.grid(True)
        leak_plot.set_xlabel("Voltage (V)")
        leak_plot.set_ylabel("Current (A)")
        # init object attributes
        self.iv_leak = raw_data.iv_leak
        self.leak_plot_lines = None
        self.leak_plot = leak_plot
        #Plot the very first leakage curve
        leak_plot.plot(self.iv_leak[0][0],
                       self.iv_leak[0][1],
                       '--k')

    def update(self):
        leak_plot = self.leak_plot
        selected_flag = self.selected_flag
        if self.leak_plot_lines is not None:
            for line in self.leak_plot_lines:
                line.remove()
        if not((-selected_flag).all()):  # if at least one true...
            indexes = np.linspace(0, 1, selected_flag.sum())
            colors = self.color_map(indexes)
            leak_plot.axes.set_color_cycle(colors)
            #Do not forget the very first leakage curve
            #is always visible
            data = self.iv_leak[1:][selected_flag].T
            self.leak_plot_lines = leak_plot.plot(data[:, 0],
                                                  data[:, 1])
        else:
            self.leak_plot_lines = None
            #Should print something on the graph to say "please select
            # a point on TLP plot"
