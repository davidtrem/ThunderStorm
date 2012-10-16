# -*- coding: utf-8 -*-

# Copyright (C) 2012 SALOME Pascal

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
Utils to report the TLP analysis
"""


import os
import markdown as md


class TLPReporting(object):
    """Utils to report data analysis
    """
    def __init__(self):
        self.has_css = False
        self.output_css = ""
        self.clear_report()

    def clear_report(self):
        self.wBody = []
        self.report_name = ""

        self.headers = """<!DOCTYPE html>
        <html lang=\"en\">
        <head>
        <meta charset=\"utf-8\">
        <style type=\"text/css\">
        """

        self.endHeaders = """
        </style>
        </head>
        <body>
        """
        self.has_body = False
        self.output_body = ""
        self.endBody = """</body>
        </html>
        """

    def set_css_format(self, cssFileName):
        if os.path.isfile(cssFileName):
            cssin = open(cssFileName)
            self.output_css = cssin.read()
            self.has_css = True

    def read_mdown_file(self, mdownFileName):
        if os.path.isfile(mdownFileName):
            mkin = open(mdownFileName)
            self.output_body = md.markdown(mkin.read(), extensions=['extra'])
            self.has_body = True

    def set_body_text(self, mkin):
        self.output_body = md.markdown(mkin, extensions=['extra'])
        self.has_body = True

    def generate_report(self):
        output = self.headers
        output += self.output_css
        output += self.endHeaders
        output += self.output_body
        output += self.endBody
        self.output = output
        return output

    def set_deviceName(self, strName):
        self.title = "# Device: " + strName
        self.wBody.append(self.title)
        self.wBody.append("")

    def save_report(self, reportName):
        self.report_name = reportName
        outfile = open(reportName, "w")
        outfile.write(self.output)
        outfile.close()

    def set_template(self, dev_name, abstract_data):
        wbody_appnd = self.wBody.append
        wbody_appnd("## Device: " + dev_name)
        wbody_appnd("")
        wbody_appnd("\tabstract: this part describes the behavior"
                    + "of the device named {0}.".format(dev_name)
                    + " Leakage and its evolution is first reviewed."
                    + " Then, TLP curve of the device is provided.")
        str_abst = " ".join(abstract_data)
        wbody_appnd("\t" + str_abst)
        wbody_appnd("")
        return self.wBody

    def set_dc_data(self):
        wbody_appnd = self.wBody.append
        wbody_appnd("### DC Characterization")
        wbody_appnd("")
        wbody_appnd("#### Main Leakage Graphs")
        wbody_appnd("")
        wbody_appnd(
            "\n" +
            '|Initial Leakage of the Cell | Leakage Evolution       |\n'
            + '|:--------------------------:|:--------------------------:|\n'
            + '|[<img src="./report_analysis/reference.png" width=352'
            + ' align="center" alt="reference">]'
            + '(./report_analysis/reference.html)  |'
            + ' [<img src=\"./report_analysis/evolution.png\"'
            + ' width=352 align=\"center\" alt=\"evolution\">]'
            + '(./report_analysis/evolution.html)|\n')
        return self.wBody

    def set_doc(self, dev_name, abstract_data):
        wbody_appnd = self.wBody.append
        wbody_appnd("## Device: " + dev_name)
        wbody_appnd("")
        wbody_appnd('\tabstract: this part describes the behavior of'
                    + ' the device named {0}.'.format(dev_name)
                    + ' Leakage and its evolution is first reviewed.'
                    + ' Then, TLP curve of the device is provided.')
        str_abst = " ".join(abstract_data)
        wbody_appnd("\t" + str_abst)
        wbody_appnd("")
        return self.wBody

    def set_dc_doc(self):
        wbody_appnd = self.wBody.append
        wbody_appnd("### DC Characterization")
        wbody_appnd("")
        wbody_appnd("#### Main Leakage Graphs")
        wbody_appnd("")
        wbody_appnd("|Initial Leakage of the Cell | Leakage Evolution       |")
        wbody_appnd("|:--------------------------:|" +
                    ":--------------------------:|")
        wbody_appnd('|<img src="./images/reference.png" width=352' +
                    'align="center" alt="reference">  | ' +
                    '<img src="./images/evolution.png" width=352 ' +
                    'align="center" alt="evolution">|\n')

        return self.wBody

    def set_spot_value(self, spot, fail_level):
        wbody_appnd = self.wBody.append
        wbody_appnd("#### Failure Assumption")
        wbody_appnd("")
        wbody_appnd("|Spot Value | Failure criterion|")
        wbody_appnd("|:---------:|:----------------:|")
        wbody_appnd("|{0:.2}V|{1}%".format(spot, fail_level))
        wbody_appnd("")

    def add_leakage_information(self, statistic, err_stat, soft_bool=False):
        str1 = ""
        str2 = ""
        str3 = ""
        wbody_appnd = self.wBody.append
        wbody_appnd("#### Additional Leakage Information")
        wbody_appnd("statistical information on leakage data taken at the " +
                    "spot value are provided in the table here below.")
        wbody_appnd("")
        t = "|Reference Value | Mean| Minimum | Maximum | Standard Deviation |"
        wbody_appnd(t)
        t = "|:--------------:|:---:|:-------:|:-------:|:------------------:|"
        wbody_appnd(t)
        wbody_appnd(statistic)
        wbody_appnd("")
        wbody_appnd("Statistics on leakage evolution are summarized in " +
                    "the table here below.")
        wbody_appnd("")
        wbody_appnd("|Error Mean| Minimum | Maximum | Standard Deviation |")
        wbody_appnd("|:--------:|:-------:|:-------:|:------------------:|")
        wbody_appnd(err_stat)
        wbody_appnd("")
        if soft_bool:
            str1 = " First Leakage evolution |"
            str2 = ":-----------------------:|"
            str3 = ('[<img src="./report_analysis/first_evolution.png"'
                    + ' width=352 align="center" alt="leakage_error">]'
                    + '(./report_analysis/first_evolution.html)')
        wbody_appnd("The leakage evolution during the TLP measurement is"
                    + " shown in the graph below.")
        wbody_appnd("")
        wbody_appnd("| Leakage evolution |" + str1)
        wbody_appnd("|:-----------------:|" + str2)
        wbody_appnd('[<img src="./report_analysis/leak_error.png" width=352 ' +
                    'align="center" alt="first_leakage">]' +
                    '(./report_analysis/leak_error.html) |' + str3)
        wbody_appnd("")

    def add_leakage_information_doc(self, statistic, err_stat,
                                    soft_bool=False):
        str1 = ""
        str2 = ""
        str3 = ""
        wbody_appnd = self.wBody.append
        wbody_appnd("#### Additional Leakage Information")
        wbody_appnd("statistical information on leakage data taken " +
                    "at the spot value are provided in the table here below.")
        wbody_appnd("")
        wbody_appnd("|Reference Value | Mean| Minimum |" +
                    " Maximum | Standard Deviation |")
        wbody_appnd("|:--------------:|:---:|:-------:|:-------:|" +
                    ":------------------:|")
        wbody_appnd(statistic)
        wbody_appnd("")
        wbody_appnd("Statistics on leakage evolution are summarized in the " +
                    "table here below.")
        wbody_appnd("")
        wbody_appnd("|Error Mean| Minimum | Maximum | Standard Deviation |")
        wbody_appnd("|:--------:|:-------:|:-------:|:------------------:|")
        wbody_appnd(err_stat)
        wbody_appnd("")
        if soft_bool:
            str1 = " First Leakage evolution |"
            str2 = ":-----------------------:|"
            str3 = ('<img src="./report_analysis/first_evolution.png" ' +
                    'width=352 align="center" alt="leakage_error">')
        wbody_appnd("The leakage evolution during the TLP measurement is " +
                    "shown in the graph below.")
        wbody_appnd("")
        wbody_appnd("| Leakage evolution |" + str1)
        wbody_appnd("|:-----------------:|" + str2)
        wbody_appnd('<img src="./report_analysis/leak_error.png" width=352 ' +
                    'align="center" alt="first_leakage">|' + str3)
        wbody_appnd("")

    def add_tlp_curves(self, zoom_bool=False):
        str1 = ""
        str2 = ""
        str3 = ""
        wbody_appnd = self.wBody.append
        wbody_appnd("")
        wbody_appnd("### Positive Current Injection: TLP Curve")
        wbody_appnd("")
        if zoom_bool:
            str1 = " Detailled View on Triggering|"
            str2 = ":---------------------------:|"
            str3 = (' [<img src="./report_analysis/TLP_B.png" width=352 ' +
                    'align="center" alt="Zooming">]' +
                    '(./report_analysis/TLP_B.html)|')

        wbody_appnd("|Full TLP Curve |" + str1)
        wbody_appnd("|:-------------:|" + str2)
        wbody_appnd('|[<img src=\"./report_analysis/TLP_A.png\" width=352 ' +
                    'align=\"center\" alt=\"full TLP\">]' +
                    '(./report_analysis/TLP_A.html) |' + str3)
        wbody_appnd("")
        wbody_appnd("Blue dots provide the leakage evolution taken at the " +
                    "spot value, while the red dots give the TLP curve.")
        wbody_appnd("")

    def add_tlp_curves_doc(self, zoom_bool=False):
        str1 = ""
        str2 = ""
        str3 = ""
        wbody_appnd = self.wBody.append
        wbody_appnd("")
        wbody_appnd("### Positive Current Injection: TLP Curve")
        wbody_appnd("")
        if zoom_bool:
            str1 = " Detailled View on Triggering|"
            str2 = ":---------------------------:|"
            str3 = (' <img src="./report_analysis/TLP_B.png" width=352 ' +
                    'align="center" alt="Zooming">|')
        wbody_appnd("|Full TLP Curve |" + str1)
        wbody_appnd("|:-------------:|" + str2)
        wbody_appnd('|<img src="./report_analysis/TLP_A.png" width=352 ' +
                    'align="center" alt="full TLP">|' + str3)
        wbody_appnd("")
        wbody_appnd("Blue dots provide the leakage evolution taken at the " +
                    "spot value, while the red dots give the TLP curve.")
        wbody_appnd("")

    def add_extraction_curves(self):
        wbody_appnd = self.wBody.append
        wbody_appnd("")
        wbody_appnd("### Data Extraction")
        wbody_appnd("")
        wbody_appnd("|Data Extraction Of The Cell |")
        wbody_appnd("|:-------------------------:|")
        wbody_appnd('[<img src="./report_analysis/TLP_C.png" width=352 ' +
                    'align="center" alt="Extraction"> ]' +
                    '(./report_analysis/TLP_C.html)|')
        wbody_appnd("")
        wbody_appnd("Blue line provide the data fitting while red dots " +
                    "give that data from the TLP curve for the holding region")
        wbody_appnd("")

    def add_extraction_curves_doc(self):
        wbody_appnd = self.wBody.append
        wbody_appnd("")
        wbody_appnd("### Data Extraction")
        wbody_appnd("")
        wbody_appnd("|Data Extraction Of The Cell |")
        wbody_appnd("|:-------------------------:|")
        wbody_appnd('<img src="./report_analysis/TLP_C.png" width=352 ' +
                    'align="center" alt="Extraction"> |')
        wbody_appnd("")
        wbody_appnd("Blue line provide the data fitting while red dots " +
                    "give that data from the TLP curve for the holding region")
        wbody_appnd("")

    def add_device_type(self, dev_type):
        wbody_appnd = self.wBody.append
        wbody_appnd("")
        wbody_appnd("|Curve Type|")
        wbody_appnd("|:------------:|")
        wbody_appnd("|{0}|".format(dev_type))
        wbody_appnd("")

    def add_triggering_information(self, trig_data):
        wbody_appnd = self.wBody.append
        wbody_appnd("")
        wbody_appnd("|Number|Triggering Voltage | Triggering Current|")
        wbody_appnd("|:----:|:-----------------:|:-----------------:|")
        self.wBody += trig_data
        wbody_appnd("")

    def add_fit_information(self, fit_data):
        wbody_appnd = self.wBody.append
        wbody_appnd("")
        wbody_appnd("|Number|Holding Voltage | ON Resistance|")
        wbody_appnd("|:----:|:--------------:|:------------:|")
        self.wBody += fit_data
        wbody_appnd("")

    def add_hard_information(self, hard_data):
        wbody_appnd = self.wBody.append
        wbody_appnd("")
        wbody_appnd("#### Hard Failure")
        wbody_appnd("")
        wbody_appnd("|Fail Voltage | Fail Current|")
        wbody_appnd("|:-----------:|:-----------:|")
        self.wBody += hard_data
        wbody_appnd("")

    def add_soft_information(self, soft_data):
        wbody_appnd = self.wBody.append
        wbody_appnd("")
        wbody_appnd("#### Soft Failure")
        wbody_appnd("")
        wbody_appnd("|Fail Voltage | Fail Current|")
        wbody_appnd("|:-----------:|:-----------:|")
        self.wBody += soft_data
        wbody_appnd("")

    def create_report(self, tlp_analysis):
        abstract_inf = []
        if tlp_analysis.is_snapback:
            abstract_inf.append("The device type is snapback.")
        else:
            abstract_inf.append("The device type is diode like.")

        if not (tlp_analysis.my_leak_analysis is None):
            if tlp_analysis.my_leak_analysis.has_failure:
                abstract_inf.append("device fails during the measurement")
            else:
                abstract_inf.append("No failure point is reported.")
        else:
            abstract_inf.append("No failure point is reported.")

        self.set_template(tlp_analysis.devName, abstract_inf)
        if not (tlp_analysis.my_leak_analysis is None):
            if tlp_analysis.has_leakage_ivs:
                self.set_dc_data()
            self.set_spot_value(tlp_analysis.my_leak_analysis.spot,
                                tlp_analysis.my_leak_analysis.fail)
            if tlp_analysis.has_leakage_ivs:
                self.add_leakage_information(
                    tlp_analysis.my_leak_analysis.str_stat,
                    tlp_analysis.my_leak_analysis.str_error_stat,
                    tlp_analysis.my_leak_analysis.has_soft_failure)
            else:
                self.add_leakage_information(
                    tlp_analysis.my_leak_analysis.str_stat,
                    tlp_analysis.my_leak_analysis.str_error_stat, False)

        self.add_tlp_curves(tlp_analysis.make_zoom)
        self.add_extraction_curves()

        if tlp_analysis.is_snapback:
            self.add_device_type("Snapback")
            if tlp_analysis.is_multi:
                self.wBody.append("...Multi Finger Triggering...")
            if len(tlp_analysis.trig_inf) == 0:
                tlp_analysis.trig_inf.append("| - | - |")
            self.add_triggering_information(tlp_analysis.trig_inf)
        else:
            self.add_device_type("Diode Like")
            self.wBody.append("No triggering point found")

        if len(tlp_analysis.fit_inf) == 0:
            tlp_analysis.fit_inf.append("| - | - |")
        self.add_fit_information(tlp_analysis.fit_inf)

        if not (tlp_analysis.my_leak_analysis is None):
            if len(tlp_analysis.my_leak_analysis.soft_inf) == 0:
                tlp_analysis.my_leak_analysis.soft_inf.append("| - | - |")
            self.add_soft_information(tlp_analysis.my_leak_analysis.soft_inf)

            if len(tlp_analysis.my_leak_analysis.hard_inf) == 0:
                tlp_analysis.my_leak_analysis.hard_inf.append("| - | - |")
            self.add_hard_information(tlp_analysis.my_leak_analysis.hard_inf)

        self.set_body_text('\n'.join(self.wBody))
        self.generate_report()

        return True

    def create_doc(self, tlp_analysis):
        abstract_inf = []
        if tlp_analysis.is_snapback:
            abstract_inf.append("The device type is snapback.")
        else:
            abstract_inf.append("The device type is diode like.")

        if tlp_analysis.my_leak_analysis.has_failure:
            abstract_inf.append("device fails during the measurement")
        else:
            abstract_inf.append("No failure point is reported.")

        self.set_doc(tlp_analysis.devName, abstract_inf)
        if not (tlp_analysis.my_leak_analysis is None):
            if tlp_analysis.has_leakage_ivs:
                self.set_dc_doc()
            self.set_spot_value(tlp_analysis.my_leak_analysis.spot,
                                tlp_analysis.my_leak_analysis.fail)

            if tlp_analysis.has_leakage_ivs:
                self.add_leakage_information_doc(
                    tlp_analysis.my_leak_analysis.str_stat,
                    tlp_analysis.my_leak_analysis.str_error_stat,
                    tlp_analysis.my_leak_analysis.has_soft_failure)
            else:
                self.add_leakage_information_doc(
                    tlp_analysis.my_leak_analysis.str_stat,
                    tlp_analysis.my_leak_analysis.str_error_stat, False)

        self.add_tlp_curves_doc(tlp_analysis.make_zoom)
        self.add_extraction_curves_doc()

        if tlp_analysis.is_snapback:
            self.add_device_type("Snapback")
            if tlp_analysis.is_multi:
                self.wBody.append("...Multi Finger Triggering...")
            self.add_triggering_information(tlp_analysis.trig_inf)
        else:
            self.add_device_type("Diode Like")
            self.wBody.append("No triggering point found")
        self.add_fit_information(tlp_analysis.fit_inf)

        if len(tlp_analysis.my_leak_analysis.soft_inf) == 0:
            tlp_analysis.my_leak_analysis.soft_inf.append("| - | - |")
        self.add_soft_information(tlp_analysis.my_leak_analysis.soft_inf)

        if len(tlp_analysis.my_leak_analysis.hard_inf) == 0:
            tlp_analysis.my_leak_analysis.hard_inf.append("| - | - |")
        self.add_hard_information(tlp_analysis.my_leak_analysis.hard_inf)

        self.set_body_text('\n'.join(self.wBody))
        self.generate_report()

        return True
