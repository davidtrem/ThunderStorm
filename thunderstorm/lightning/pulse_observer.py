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

class TLPFigure(object):
    """A simple TLP figure
    """
    def __init__(self, figure, tlp_curve_data, title="",
                 leakage_evol=None):
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
        tlp_plot.plot(volt[selected_flag], curr[selected_flag], 'ro')
        figure.canvas.mpl_connect('pick_event', self.onpickevent)
        figure.canvas.draw()
        
    def onpickevent(self, event):
        if event.mouseevent.button == 1:
            ax1.set_autoscale_on(False)
            ind = event.ind
            selected_flag[ind] = not selected_flag[ind]
            print x[selected_flag]
            print 'onpick3 scatter:', ind, np.take(x, ind), np.take(y, ind)
            selected_point.set_data(x[selected_flag], y[selected_flag])
            fig.canvas.draw()        