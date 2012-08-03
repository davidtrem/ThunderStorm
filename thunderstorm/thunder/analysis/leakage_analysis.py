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
Utils to analyse the leakage of a TLP measurement
"""

import numpy as np

import matplotlib
from matplotlib.backends.backend_agg import FigureCanvasAgg as FigureCanvas
from matplotlib.figure import Figure
import markdown as md
from datetime import datetime


class LeakageAnalysis(object):
	"""Utils to analyse leakage data
	"""
	spot=0.5
	fail=15
	
	def __init__(self, leakage_data):
		self.leakage_data = leakage_data
		self.rising=[]
		self.falling=[]
		self.has_failure=False
		self.has_soft_failure=False
		self.fail_index=-1
		self.trig_inf=[]
		self.hard_inf=[]
		self.soft_inf=[]
		self.spot=0.5
		self.fail=15


	def check_spot_value(self, spot):
		if spot > np.max(self.leakage_data[0][0]):
			return np.max(self.leakage_data[0][0])
		return spot
	
	def get_leak_value_from_voltage(self, leak_array, voltage=spot):
		x_array=leak_array[0]
		y_array=leak_array[1]
		if voltage <= x_array[0]:
			return y_array[0]
		for elem in range(len(x_array)):
			if x_array[elem]==voltage:
				return y_array[elem]
			if x_array[elem]>voltage:
				slope=(y_array[elem]-y_array[elem-1])/(x_array[elem]-x_array[elem-1])
				y_value=slope*(voltage-x_array[elem-1])+y_array[elem-1]
				return y_value	
		return y_array[-1]
	
	def get_leak_array_from_voltage(self, voltage=spot):
		leak_arr=[]
		for item in self.leakage_data:
			val=self.get_leak_value_from_voltage(item,voltage)
			leak_arr.append(val)
		self.leak_tab=np.array(leak_arr)
		self.str_stat="|{0}|{1}|{2}|{3}|{4}|".format(self.leak_tab[0], self.leak_tab.mean(), self.leak_tab.min(), self.leak_tab.max(), self.leak_tab.std())
		return self.leak_tab
		
	def set_leak_array_from_leak_evol(self, leak_evol):
		self.leak_tab=np.array(leak_evol)
		self.str_stat="|{0}|{1}|{2}|{3}|{4}|".format(self.leak_tab[0], self.leak_tab.mean(), self.leak_tab.min(), self.leak_tab.max(), self.leak_tab.std())
		return self.leak_tab

	def check_leak_array_from_percentage(self, leak_array, max_percent=fail):
		ref_value=leak_array[0]
		err_array=[]
		for item in leak_array:
			err=100.0*(item-ref_value)/ref_value
			err_array.append(err)
		self.err_tab=np.array(err_array)
		self.str_error_stat="|{0}|{1}|{2}|{3}|".format(self.err_tab.mean(), self.err_tab.min(), self.err_tab.max(), self.err_tab.std())
		return self.err_tab
		
	def get_failure_points(self, err_arr, fail_perc=fail):
		rising=self.rising
		falling=self.falling
		ind=np.where(np.abs(err_arr) >= fail_perc)
		if len(ind[0]) == 0:
			#print "No failure found"
			self.has_failure=False
			return rising,falling


		self.has_failure=True
		prev_elem=-1
		for elem in ind[0]:
			if prev_elem != -1:
				if (elem-prev_elem) != 1:
					rising.append(elem)
					falling.append(prev_elem)
			if elem==ind[0][0]:
				rising.append(elem)
				if elem < len(err_arr)-1 and len(ind[0])==1:
					falling.append(elem)
			prev_elem=elem

		##### removing noise from falling and rising
		remF=[]
		remR=[]
		for elem in rising:
			if elem in falling:
				remF.append(elem)
				remR.append(elem)	
			if (elem+1) in falling:
				remF.append(elem+1)
				remR.append(elem)
				
		for item in remF:
			falling.remove(item)
		for item in remR:
			rising.remove(item)
	
		if len(falling) != 0:
			print "Strange leakage behaviour, leakage is cooling down..."
		if len(rising) > 0:
			self.fail_index=rising[-1]
			if len(rising) > 1:
				self.has_soft_failure=True
		else:
			self.has_failure=False
			
		return rising,falling
		

	def set_fail(self,value):
		self.fail=value
		fail=value
		
	def set_spot(self,value):
		self.spot=self.check_spot_value(value)
		spot=value

	def set_device_name(self,str_name):
		self.devName=str_name
		
	def set_base_dir(self,str_dir):
		self.baseDir=str_dir

	def set_fail_str(self,tlp_table):

		if self.has_failure:
			self.fail_str="{0:.2}A".format(tlp_table[1][self.fail_index])
			self.prev_str="{0:.2}A".format(tlp_table[1][self.fail_index-1])
			self.hard_inf.append("{0:.4}V|{1:.2}A".format(tlp_table[0][self.fail_index-1],tlp_table[1][self.fail_index-1]))
			if len(self.rising) > 1:
				self.rise_str="{0:.2}A".format(tlp_table[1][self.rising[0]])
				self.prev_rise="{0:.2}A".format(tlp_table[1][self.rising[0]-1])

				for item in range(len(self.rising)-1):
					self.soft_inf.append("{0:.4}V|{1:.2}A".format(tlp_table[0][self.rising[item]-1],tlp_table[1][self.rising[item]-1]))
		else:
			self.fail_str="None"
			self.prev_str="None"
			self.hard_inf.append("None")
			self.soft_inf.append("None")


		
	def make_reference_plot(self,file_name):
		
		ref_fig=Figure()
		canvas = FigureCanvas(ref_fig)
		refFile=self.leakage_data[0]


		ref_plot = ref_fig.add_subplot(111)
		ref_plot.semilogy(refFile[0],np.abs(refFile[1]),'bo-')
		ref_plot.set_xlabel(r'Voltage [V]')
		ref_plot.set_ylabel(r'Current [A]')
		ref_plot.set_title(self.devName+"- Reference Curve - Leakage")
		ref_plot.grid(True)
		myaxis=ref_plot.axis()
		date_deb=datetime.now()
		ref_plot.axvline(self.spot,color='m', linestyle='-.', linewidth=2)
		ref_plot.text(1.05*self.spot,0.4*myaxis[3]," spot: {0:.4}V ".format(self.spot),color='m',rotation=270)
		ref_plot.text(myaxis[0],myaxis[2]*2," "+date_deb.ctime())
		ref_fig.savefig(file_name)
				
		textFile="[<img src=\"reference.png\" align=\"center\" alt=\"Reference\"> ](../"+self.devName+"_report.html)"
		text_output=md.markdown(textFile, extensions=['extra'])
		text_out=open(file_name[:-4]+".html","w")
		text_out.write(text_output)
		text_out.close()

		
	def make_evolution_plot(self,file_name):
		
		evol_fig=Figure()
		canvas = FigureCanvas(evol_fig)
		refFile=self.leakage_data[0]
		lastFile=self.leakage_data[-1]
		
		evol_plot = evol_fig.add_subplot(111)
		evol_plot.semilogy(refFile[0],np.abs(refFile[1]),'bs:',linewidth=2)
		evol_plot.hold(True)
		evol_plot.semilogy(lastFile[0],np.abs(lastFile[1]),'r.-')
		
		if not self.fail_index == -1:
			firstFail=self.leakage_data[self.fail_index]
			beforeFail=self.leakage_data[self.fail_index-1]
			evol_plot.semilogy(firstFail[0],np.abs(beforeFail[1]),'gx-')
			evol_plot.semilogy(firstFail[0],np.abs(firstFail[1]),'md-',markersize=4)  #m for magenta
			evol_plot.legend(["Initial","Last",self.prev_str,self.fail_str],'upper left')
		else:
			evol_plot.legend(["Initial","Last"],'upper left')

		X1=0.9*self.spot
		X2=1.1*self.spot
		Y1=abs(self.leak_tab[0])*(2.0) #increase of 100%
		Y2=abs(self.leak_tab[0])*(1.0-self.fail/100)

		evol_plot.fill([X1,X2,X2,X1],[Y1,Y1,Y2,Y2],'y',alpha=0.5,edgecolor='0.5')

		evol_plot.set_xlabel(r'Voltage [V]')
		evol_plot.set_ylabel(r'Current [A]')
		title_str=", Leakage Evolution, spot: {0:.2}V".format(self.spot)
		evol_plot.set_title(self.devName+title_str)
		evol_plot.grid(True)

		myaxis=evol_plot.axis()
		date_deb=datetime.now()

		evol_plot.text(myaxis[0],myaxis[2]*2," "+date_deb.ctime())
		evol_fig.savefig(file_name) 
		
		textFile="[<img src=\"evolution.png\" align=\"center\" alt=\"Reference\"> ](../"+self.devName+"_report.html)"
		text_output=md.markdown(textFile, extensions=['extra'])
		text_out=open(file_name[:-4]+".html","w")
		text_out.write(text_output)
		text_out.close()


	
	def make_first_evolution_plot(self,file_name):
		
		if len(self.rising) > 1:
				
			rising_fig=Figure()
			canvas = FigureCanvas(rising_fig)
			rising_plot = rising_fig.add_subplot(111)
			refFile=self.leakage_data[0]
			lastFile=self.leakage_data[-1]
			X1=0.9*self.spot
			X2=1.1*self.spot
			Y1=self.leak_tab[0]*(2.0) #increase of 100%
			Y2=self.leak_tab[0]*(1.0-self.fail/100)
			
			
			rising_plot.semilogy(refFile[0],np.abs(refFile[1]),'bs:',linewidth=2)
			rising_plot.hold(True)
			firstRise=self.leakage_data[self.rising[0]]
			beforeRise=self.leakage_data[self.rising[0]-1]
			rising_plot.semilogy(firstRise[0],np.abs(beforeRise[1]),'gx-')
			rising_plot.semilogy(beforeRise[0],np.abs(firstRise[1]),'md-',markersize=4)


			rising_plot.fill([X1,X2,X2,X1],[Y1,Y1,Y2,Y2],'y',alpha=0.5,edgecolor='0.5')

			rising_plot.legend(["Initial",self.prev_rise,self.rise_str],'upper left')
			rising_plot.set_xlabel(r'Voltage [V]')
			rising_plot.set_ylabel(r'Current [A]')
			rising_plot.set_title(self.devName+" Very first Leakage Evolution")
			rising_plot.grid(True)
			myaxis=rising_plot.axis()
			date_deb=datetime.now()
			rising_plot.text(myaxis[0],myaxis[2]*2," "+date_deb.ctime())
		
			rising_fig.savefig(file_name)    
			
			textFile="[<img src=\"first_evolution.png\" align=\"center\" alt=\"Reference\"> ](../"+self.devName+"_report.html)"
		 	text_output=md.markdown(textFile, extensions=['extra'])
			text_out=open(file_name[:-4]+".html","w")
			text_out.write(text_output)
			text_out.close()



	def make_error_plot(self,file_name):
		
		err_fig=Figure()
		canvas = FigureCanvas(err_fig)
		err_plot = err_fig.add_subplot(111)
		
		err_plot.plot(self.err_tab,'b-',linewidth=2)  
		err_plot.set_ylim(-100,100)
		err_plot.set_xlim(0,len(self.err_tab)-1)
		err_plot.set_xlabel('Acquisition number')
		err_plot.set_ylabel('leakage evolution [%]')
		err_plot.set_title(self.devName+' Change in electrical characteristic')
		err_plot.fill([0,len(self.err_tab)-1,len(self.err_tab)-1,0],[-self.fail,-self.fail,self.fail,self.fail],'g',alpha=0.2,edgecolor='g')
		err_plot.fill([0,len(self.err_tab)-1,len(self.err_tab)-1,0],[self.fail,self.fail,50.0,50.0],'y',alpha=0.2,edgecolor='y')
		err_plot.fill([0,len(self.err_tab)-1,len(self.err_tab)-1,0],[50.0,50.0,100.0,100.0],'r',alpha=0.2,edgecolor='r')
		err_plot.fill([0,len(self.err_tab)-1,len(self.err_tab)-1,0],[-self.fail,-self.fail,-50.0,-50.0],'y',alpha=0.2,edgecolor='y')
		err_plot.fill([0,len(self.err_tab)-1,len(self.err_tab)-1,0],[-50.0,-50.0,-100.0,-100.0],'r',alpha=0.2,edgecolor='r')
		err_plot.text(1,90,"Hard Failure Area",color='r')
		err_plot.text(1,40,"soft Failure Area",color='orange')
		date_deb=datetime.now()

		err_plot.text(1,-95.0,date_deb.ctime())
		chaine="Mean err={0:.2}%, Max err={1:.2}%".format(self.err_tab.mean(),max(np.abs(self.err_tab)))
		err_plot.text(len(self.err_tab)*0.5,-self.fail+(self.fail-50)*0.5,chaine,color='blue')
		err_fig.savefig(file_name)    
		
		textFile="[<img src=\"leak_error.png\" align=\"center\" alt=\"leakError\">](../"+self.devName+"_report.html)"
	 	text_output=md.markdown(textFile, extensions=['extra'])
		text_out=open(file_name[:-4]+".html","w")
		text_out.write(text_output)
		text_out.close()


	def update_leakage_analysis(self,tlp_table):

		self.rising=[]
		self.falling=[]
		self.has_failure=False
		self.has_soft_failure=False
		self.fail_index=-1
		#self.trig_inf=[]
		self.hard_inf=[]
		self.soft_inf=[]

		leak_tab=self.get_leak_array_from_voltage(self.spot)
		#self.str_stat="|{0}|{1}|{2}|{3}|{4}|".format(leak_tab[0], leak_tab.mean(), leak_tab.min(), leak_tab.max(), leak_tab.std())
		err_tab=self.check_leak_array_from_percentage(leak_tab,self.fail) 
		#self.str_error_stat="|{0}|{1}|{2}|{3}|".format(err_tab.mean(), err_tab.min(), err_tab.max(), err_tab.std())

		rising,falling=self.get_failure_points(err_tab,self.fail)
		fail_index=self.fail_index
		self.set_fail_str(tlp_table)
		
		self.make_reference_plot(self.baseDir+'/report_analysis/reference.png')
		self.make_evolution_plot(self.baseDir+'/report_analysis/evolution.png')
		self.make_first_evolution_plot(self.baseDir+'/report_analysis/first_evolution.png')
		self.make_error_plot(self.baseDir+'/report_analysis/leak_error.png')


	def update_evol_analysis(self,tlp_table):

			self.rising=[]
			self.falling=[]
			self.has_failure=False
			self.has_soft_failure=False
			self.fail_index=-1
			self.hard_inf=[]
			self.soft_inf=[]

			err_tab=self.check_leak_array_from_percentage(self.leak_tab,self.fail) 

			rising,falling=self.get_failure_points(err_tab,self.fail)
			fail_index=self.fail_index
			
			self.set_fail_str(tlp_table)
			self.make_error_plot(self.baseDir+'/report_analysis/leak_error.png')

