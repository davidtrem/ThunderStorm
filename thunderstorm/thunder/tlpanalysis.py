# -*- coding: utf-8 -*-

# Copyright (C) 2012 Trémouilles David

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
Analysis of TLP data
Orignal code from Pascal Salome 2012
"""

import os
import glob
import shutil

from thunderstorm.thunder.analysis.tlp_analysis import TLPAnalysis
from thunderstorm.thunder.analysis.report_analysis import TLPReporting


class RawTLPdataAnalysis(object):
    """Provide analysis on raw measurement data
    """

    def __init__(self, raw_data):
        """
        Parameters
        ----------
        raw_data: RawTLPdata
            RawTLPdata instance
        """
        self.has_report = False

        file_path = raw_data.original_file_name
        tlp_curve = raw_data.tlp_curve
        leak_evol = raw_data.leak_evol
        ## PSA thi is a trial to integrate the data analysis
        baseDir = os.path.dirname(file_path)

        devName = os.path.splitext(os.path.basename(str(file_path)))[0]

        if not os.path.exists(os.path.join(baseDir, 'report_analysis')):
            os.mkdir(os.path.join(baseDir, 'report_analysis'))

        self.spot_v = 0.5    # default value for leakage extraction : 0.5V
        self.fail_perc = 15  # default value for failure level 15%
        self.seuil = -0.4    # default for triggering point extraction: -0.4V

        my_tlp_analysis = TLPAnalysis(tlp_curve)
        my_tlp_analysis.set_threshold(self.seuil)

        if self.has_leakage_ivs:
            my_tlp_analysis.set_leak_analysis(self._iv_leak_data)
            my_tlp_analysis.set_spot(self.spot_v)
            my_tlp_analysis.set_fail(self.fail_perc)

        elif self.has_leakage_evolution:
            my_tlp_analysis.set_evol_analysis(leak_evol)
            my_tlp_analysis.set_fail(self.fail_perc)

        my_tlp_analysis.set_device_name(devName)
        my_tlp_analysis.set_base_dir(baseDir)

        my_tlp_analysis.update_analysis()

        self.myOfile = baseDir + os.sep + devName + '_report.html'
        self.css = os.path.abspath("." + os.sep + "ESDAnalysisTool.css")

        self.report = TLPReporting()
        self.report.set_css_format(self.css)

        self.has_report = self.report.create_report(my_tlp_analysis)
        self.report.save_report(self.myOfile)

        self.my_tlp_analysis = my_tlp_analysis
########### end of addon by PAS July 2nd, 2012

    def update_analysis(self):
        #print "analysis running an update"
        self.my_tlp_analysis.set_spot(self.spot_v)
        self.my_tlp_analysis.set_fail(self.fail_perc)
        self.my_tlp_analysis.set_threshold(self.seuil)
        self.my_tlp_analysis.update_analysis()

        if self.has_report:
            self.report.clear_report()
            self.has_report = self.report.create_report(self.my_tlp_analysis)
            self.report.save_report(self.myOfile)

    def update_style(self):
        self.report.clear_report()
        self.report.set_css_format(self.css)
        self.has_report = self.report.create_report(self.my_tlp_analysis)
        self.report.save_report(self.myOfile)

    def save_analysis(self, save_name):
        if self.has_report:
            self.report.clear_report()
            self.has_report = self.report.create_doc(self.my_tlp_analysis)
            f = open(save_name, "w")
            f.write(self.report.output)
            f.close()

            baseDir = os.path.dirname(self.myOfile)
            pathName = os.path.dirname(save_name)
            rep = os.path.join(baseDir, 'report_analysis')
            #names=os.listdir(rep)
            names = glob.glob(rep + os.sep + "*.png")
            #print rep+"/*.png",names
            for item in names:
                (mypath, myname) = os.path.split(item)
                dest = pathName + os.sep + myname
                shutil.copy(item, dest)