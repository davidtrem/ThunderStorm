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

""" Viewing data
"""

from matplotlib.pyplot import figure
from thunderstorm.lightning.leakage_std import LeakFigure
from thunderstorm.lightning.simple_plots import TLPFigure
from thunderstorm.lightning.pulse_observer import TLPPulsePickFigure
import matplotlib
matplotlib.interactive(True)


class View(object):

    def __init__(self, experiment):
        self.experiment = experiment

    def __repr__(self):
        message = "View of "
        message += str(self.experiment)
        return message

    def raw_tlp(self):
        fig = figure()
        self.raw_tlp_fig = TLPFigure(fig,
                                     self.experiment.raw_data.tlp_curve,
                                     self.experiment.exp_name,
                                     self.experiment.raw_data.leak_evol)
    def pulse_observer(self):
        fig = figure()
        self.pickfig = TLPPulsePickFigure(fig,
                                          self.experiment.raw_data,
                                          self.experiment.exp_name)

    def leak(self):
        if self.experiment.raw_data.iv_leak == []:
            raise RuntimeError("No leakage curves available")
        fig = figure()
        self.leak_fig = LeakFigure(fig, "test",
                                   self.experiment.raw_data.iv_leak)



