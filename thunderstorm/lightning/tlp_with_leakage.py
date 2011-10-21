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
import logging

class TLPFigureWithLeakage(object):
    """A simple TLP figure
    """
    def __init__(self, figure, tlp_curve_data, leakage_evol, title=""):
        tlp_plot = figure.add_subplot(111)
        tlp_plot.grid(True)
        tlp_plot.set_xlabel("Voltage (V)")
        tlp_plot.set_ylabel("Current (A)")
        tlp_plot.set_title(title + "TLP curve")
        tlp_plot.plot(tlp_curve_data[0], tlp_curve_data[1], '-o')

        if (leakage_evol == None
            or len(leakage_evol) == 0
            or np.alltrue(leakage_evol == 0)):
            log = logging.getLogger('thunderstorm.lightning')
            log.warn("Leakage evolution cannot be plotted, no data")
        else:
            fig_leak_evol = tlp_plot.twiny()
            fig_leak_evol.set_navigate(False)
            fig_leak_evol.semilogx(leakage_evol, tlp_curve_data[1],
                               'g-o',
                               markersize=2)
        self.plot = tlp_plot
        self.draw = figure.canvas.draw

