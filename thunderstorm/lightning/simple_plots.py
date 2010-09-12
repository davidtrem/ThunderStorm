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
Simple typical TLP curves plot
"""

import numpy as np
import warnings

class PulsesFigure(object):
    def __init__(self, figure, pulses, title=""):
        time = np.arange(pulses.pulses_length) * pulses.delta_t
        offseted_time = pulses.offsets_t + time[:,np.newaxis]
        offseted_time = offseted_time * 1e9
        # time in nanosecond
        # V curves
        v_pulse_plot = figure.add_subplot(211)
        v_pulse_plot.grid(True)
        v_pulse_plot.set_ylabel("Voltage")
        v_pulse_plot.set_title(title)
        v_pulse_plot.plot(offseted_time, pulses.voltage.T)
        # I curves
        i_pulse_plot = figure.add_subplot(212, sharex=v_pulse_plot)
        i_pulse_plot.grid(True)
        i_pulse_plot.set_xlabel("time (ns)")
        i_pulse_plot.set_ylabel("Current")
        i_pulse_plot.set_title(title)
        i_pulse_plot.plot(offseted_time, pulses.current.T)

        self.v_plot = v_pulse_plot
        self.i_plot = i_pulse_plot
        figure.canvas.draw()



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
        tlp_plot.plot(tlp_curve_data[0], tlp_curve_data[1], '-o')

        if (leakage_evol == None
            or len(leakage_evol) == 0
            or np.alltrue(leakage_evol == 0)):
            warnings.warn("No proper leakage evolution available\n" +
                          "Leakage evolution will not be plotted",
                          RuntimeWarning)
        else:
            self.leak_evol_state = [True, False, False]
            self.init_leak_evol(tlp_plot, tlp_curve_data, leakage_evol)
            figure.canvas.mpl_connect('key_press_event',
                                      self.on_key_press)
        self.draw = figure.canvas.draw
        self.draw()
        
    def init_leak_evol(self, tlp_plot, tlp_curve_data, leakage_evol):
        leak_evol_with_v = tlp_plot.twinx()
        leak_evol_with_v.semilogy(tlp_curve_data[0],
                                  leakage_evol,
                                  'g-o',
                                  markersize=2)
        leak_evol_with_i = tlp_plot.twiny()
        leak_evol_with_i.semilogx(leakage_evol,
                                  tlp_curve_data[1],
                                  'g-o',
                                  markersize=2)
        leak_evol_with_i.set_navigate(False)
        leak_evol_with_v.set_navigate(False)
        leak_evol_with_v.set_visible(False)
        self.leak_evol_state = [True, False, False]
        self._leak_evol_with_v = leak_evol_with_v
        self._leak_evol_with_i = leak_evol_with_i     
        
    def on_key_press(self, event):
        if event.inaxes:
            if event.key == 'l':
                leak_state = self.leak_evol_state
                leak_state.insert(0, leak_state.pop())
                self._leak_evol_with_i.set_visible(leak_state[0])
                self._leak_evol_with_v.set_visible(leak_state[1])
                self.draw()
