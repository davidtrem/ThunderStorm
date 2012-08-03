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
Utils to analyse the TLP data from a measurement
"""

import numpy as np

import matplotlib
from matplotlib.backends.backend_agg import FigureCanvasAgg as FigureCanvas
from matplotlib.figure import Figure
import markdown as md

from datetime import datetime
from thunderstorm.thunder.analysis.leakage_analysis import LeakageAnalysis


class TLPAnalysis(object):
	"""Utils to analyse leakage data
	"""
	def __init__(self, tlp_data):
		self.tlp_data = tlp_data
		self.volt=np.array(tlp_data[0])
		self.curr=np.array(tlp_data[1])
		self.is_snapback=False
		self.is_multi=False
		self.start_region=[]
		self.end_region=[]
		self.trig_inf=[]
		self.my_leak_analysis=None
		self.has_leakage_ivs=False
		self.has_leakage_evolution=False
		
	def get_voltage_array(self):
		return self.volt
	
	def get_current_array(self):
		return self.curr

	def data_smoothing(self, arr):
		smoothD=[]
		for val in range(len(arr)-3):
			point1=arr[val]
			point2=arr[val+1]
			point3=arr[val+2]
			smoothD.append((point1+point2+point3)/3.0)
		return smoothD

	def extract_triggering_point(self, threshold):
		if threshold==0.0:
			threshold=-0.5
		volt=self.volt
		curr=self.curr
		smoothV=self.data_smoothing(volt)
		#smoothI=self.data_smoothing(curr)
		dV=np.diff(smoothV)
		#dI=np.diff(smoothI)
		#der=np.divide(dI,dV)
		mytrip=np.where(dV <= threshold)
		self.dV=dV
###		if len(mytrip[0])==0 or True:   ### line commented to be placed somewhere else to manage the plot
###			derivative=pl.figure()     ### line commented to be placed somewhere else to manage the plot
###			pl.plot(dV)                 ### line commented to be placed somewhere else to manage the plot
			#pl.hold(True)
			#pl.plot(der)
###			pl.axhline(threshold,color='m', linestyle='-.', linewidth=2)    ### line commented to be placed somewhere else to manage the plot
		kInd=-1
		if len(mytrip[0]) > 0:
			#print mytrip
			self.is_snapback=True
			if len(mytrip[0]) > 1:
				self.is_multi=True
				prev_elem = -1
				for elem in mytrip[0]:
					if prev_elem != -1:
						if (elem-prev_elem) != 1:
							self.start_region.append(elem)
							self.end_region.append(elem-1)
					if elem==mytrip[0][0]:
						self.start_region.append(elem)
					prev_elem=elem
				
			##### adjusting the index found on the smoothed matrix
			
			kInd=self.adjust_index(mytrip[0][0])
			if len(self.start_region) <= 1:
				self.is_multi=False
			
#			if mytrip[0][0] >=2:
#				sInd=mytrip[0][0]-2
#			else:
#				sInd=0
#			kInd=sInd
#			for item in range(1,5):
#				if volt[kInd] < volt[sInd+item]:
#					kInd=sInd+item
			self.ext_table=mytrip
		self.kInd=kInd
		return self.kInd
		
	def adjust_index(self,valIndex):
		volt=self.volt
		
		if valIndex >=2:
			sInd=valIndex-2
		else:
			sInd=0
		kInd=sInd
		for item in range(1,5):
			if volt[kInd] < volt[sInd+item]:
				kInd=sInd+item		

		return kInd		
		
	def get_snapback_index(self,fromI):
		volt=self.volt
		prev_volt=volt[fromI]
		for elem in range(fromI+1,len(volt)):
			if volt[elem]>prev_volt:
				return elem
			prev_volt=volt[elem]
		return -1

	def get_start_index(self, currRef):
		if currRef==0.0:
			currRef=0.01
		volt=self.volt
		curr=self.curr
		mytab=np.where(curr >= currRef)
		if len(mytab[0])>0:
			return mytab[0][0]
		return -1
		
	def set_threshold(self,value):
		self.seuil=value
		
	def set_spot(self,value):
		if self.has_leakage_ivs :
			self.my_leak_analysis.set_spot(value)
			
	def set_base_dir(self,str_dir):
		self.baseDir=str_dir
		if self.has_leakage_ivs or self.has_leakage_evolution:
			self.my_leak_analysis.set_base_dir(str_dir)

	def set_fail(self,value):
		if self.has_leakage_ivs or self.has_leakage_evolution:
			self.my_leak_analysis.set_fail(value)

		
	def set_triggering_str(self):
		if self.is_snapback:
			self.trig_reg=1
			if self.is_multi:
				for item in self.start_region:
					affInd=self.adjust_index(item)
					self.trig_inf.append("|{2}|{0:.3}|{1:.3}|".format(self.volt[affInd],self.curr[affInd],self.trig_reg))
					self.trig_reg+=1
			else:
				self.trig_inf.append("|{2}|{0:.3}|{1:.3}|".format(self.volt[self.kInd],self.curr[self.kInd],1))
		return self.trig_inf
		
	def make_derivative_plot(self,file_name):	
		derivative_fig=Figure()
		canvas = FigureCanvas(derivative_fig)
		derivative_plot = derivative_fig.add_subplot(111)
		derivative_plot.plot(self.dV)                 
		derivative_plot.axhline(self.seuil,color='m', linestyle='-.', linewidth=2)    
		derivative_fig.savefig(file_name)
	
	def set_leak_analysis(self,leak_table):		
		self.my_leak_analysis=LeakageAnalysis(leak_table)
		if not len(leak_table) == 0:
			self.has_leakage_ivs=True
			
	def set_evol_analysis(self,leak_evol):	
		if not self.has_leakage_ivs :
			self.my_leak_analysis=LeakageAnalysis([])
			self.my_leak_analysis.set_leak_array_from_leak_evol(leak_evol)
			self.has_leakage_evolution=True


	def set_device_name(self,str_name):
		self.devName=str_name
		if not self.my_leak_analysis == None:
			self.my_leak_analysis.set_device_name(str_name)
			
	def get_fitting_data(self):
		x_val=[]
		y_val=[]
		x_val2=[]
		y_val2=[]
		p=[]
		p2=[]
		self.fit_inf=[]
		if self.is_snapback:
			sbIndex=self.get_snapback_index(self.kInd)
			#print kInd, sbIndex
			endPoint=len(self.volt)-1
			if not self.my_leak_analysis ==None:
				if len(self.my_leak_analysis.rising) > 0:
					endPoint=self.my_leak_analysis.rising[0]-1
			if 	self.is_multi:
				#### fit sur la derniere region non fail
				newTrigPoint=self.adjust_index(self.start_region[-1])
				newSbkIndex=self.get_snapback_index(newTrigPoint)
				newEndPoint=self.adjust_index(self.start_region[1])
				buff=endPoint
				endPoint=newEndPoint
				newEndPoint=buff
				if newEndPoint>newSbkIndex:
					p2=np.polyfit(self.curr[newSbkIndex:newEndPoint],self.volt[newSbkIndex:newEndPoint],1)
					x_val2=np.linspace(0,np.max(self.curr),50)
					y_val2=np.polyval(p2,x_val2)
					#print "Last fitting snapback",p2[0],p2[1]
					self.fit_inf.append("|{2}|{0:.3}|{1:.3}|".format(p2[1],p2[0],len(self.start_region)))
					fittingLast=True
				else:
					fittingLast=False
					
				self.fittingLast=fittingLast
				self.newSbkIndex=newSbkIndex
				self.newEndPoint=newEndPoint
				self.x_val2=x_val2
				self.y_val2=y_val2
				self.p2=p2
					
			if endPoint>sbIndex:
				p=np.polyfit(self.curr[sbIndex:endPoint],self.volt[sbIndex:endPoint],1)
				x_val=np.linspace(0,np.max(self.curr),50)
				y_val=np.polyval(p,x_val)
				#print "first fitting snapback",p[0],p[1]
				self.fit_inf.insert(0,"|{2}|{0:.3}|{1:.3}|".format(p[1],p[0],1))
				self.fitting=True
			else:
				self.fitting=False
		
		else:
			endPoint=len(self.volt)-1
			if not self.my_leak_analysis == None: 
				if len(self.my_leak_analysis.rising) > 0:
					endPoint=self.my_leak_analysis.rising[0]-1


			sbIndex=self.get_start_index(0.02) #get index for current above 20mA
			if sbIndex == -1:
				sbIndex=0
			if endPoint>sbIndex:
				p=np.polyfit(self.curr[sbIndex:endPoint],self.volt[sbIndex:endPoint],2)
				if np.max(self.curr) > 0:
					x_val=np.linspace(0,np.max(self.curr),50)
				else:
					x_val=np.linspace(0,np.min(self.curr),50)

				y_val=np.polyval(p,x_val)
				#print "fitting non snapback",p[0],p[1],p[2]
				self.fit_inf.insert(0,"|{2}|{0:.3}|{1:.3}|".format(p[2],p[1],1))
				self.fitting=True
			else:
				self.fitting=False
				
		self.sbIndex=sbIndex
		self.endPoint=endPoint
		self.x_val=x_val
		self.y_val=y_val
		self.p=p
		
		
	def make_tlp_plot(self,file_name):	
		tlp_fig=Figure()
		canvas = FigureCanvas(tlp_fig)
		tlpA_plot = tlp_fig.add_subplot(111)

		tlpA_plot.plot(self.tlp_data[0],self.tlp_data[1],'ro', markersize=3)
		tlpA_plot.set_xlabel(r'Voltage [V]')
		tlpA_plot.set_ylabel(r'Current [A]')
		myaxis=tlpA_plot.axis()
		date_deb=datetime.now()
		self.make_zoom=False
		if myaxis[3]>3.5:
			self.make_zoom=True
		tlpA_plot.text(myaxis[0],myaxis[3]*0.95," "+date_deb.ctime())
		tlpA_plot.text(myaxis[1]*0.4,myaxis[3]*0.95,self.devName+" TLP Curve", color='r')
		tlpA_plot.text(myaxis[1]*0.4,myaxis[3]*0.9,"Leakage Curve", color='b')
		tlpA_plot.grid(True)
		if np.max(self.tlp_data[0]) <= 0:
			tlpA_plot.set_xlim(myaxis[0],0)
		else:
			tlpA_plot.set_xlim(0,)
		if np.max(self.tlp_data[1]) <= 0:
			tlpA_plot.set_ylim(myaxis[2],0)
		else:
			tlpA_plot.set_ylim(0,)

		if not self.my_leak_analysis == None:
			if len(self.my_leak_analysis.rising) > 0:
				tlpA_plot.axhspan(self.tlp_data[1][self.my_leak_analysis.fail_index-1], myaxis[3], facecolor='r', alpha=0.5)
			if len(self.my_leak_analysis.rising) > 1:
				for item in range(len(self.my_leak_analysis.falling)):
					tlpA_plot.axhspan(self.tlp_data[1][self.my_leak_analysis.rising[item]], self.tlp_data[1][self.my_leak_analysis.falling[item]], facecolor='y', alpha=0.5)
			if not self.my_leak_analysis.leak_tab.shape[0] < self.tlp_data[1].shape[0]:
				tlpA2=tlpA_plot.twiny()
				if self.my_leak_analysis.leak_tab.shape[0] > self.tlp_data[1].shape[0]:
					leak_abs=np.array(self.my_leak_analysis.leak_tab[1:])
					tlpA2.semilogx(np.abs(leak_abs),self.tlp_data[1],'bs', markersize=3)
				else:
					leak_abs=np.array(self.my_leak_analysis.leak_tab)
					tlpA2.semilogx(np.abs(leak_abs),self.tlp_data[1],'bs', markersize=3)
					tlpA2.set_xlabel(r'Leakage Current [A]')

				tlpA2.set_ylim(0,)
		tlp_fig.savefig(file_name+"_A.png")
		
		textFile="[<img src=\"TLP_A.png\" align=\"center\" alt=\"TLPA\"> ](../"+self.devName+"_report.html)"
	 	text_output=md.markdown(textFile, extensions=['extra'])
		text_out=open(file_name+"_A.html","w")
		text_out.write(text_output)
		text_out.close()

		
		if self.make_zoom:
			zoom_fig=Figure()
			canvas = FigureCanvas(zoom_fig)
			zoom_plot = zoom_fig.add_subplot(111)

			zoom_plot.plot(self.tlp_data[0],self.tlp_data[1],'ro', markersize=3)
							
			zoom_plot.set_xlabel(r'Voltage [V]')
			zoom_plot.set_ylabel(r'Current [A]')
			if np.max(self.tlp_data[0]) <= 0:
				zoom_plot.set_xlim(myaxis[0],0)
			else:
				zoom_plot.set_xlim(0,)
			if np.max(self.tlp_data[1]) <= 0:
				zoom_plot.set_ylim(-2,0)
			else:
				zoom_plot.set_ylim(0,2)

			myaxis=zoom_plot.axis()
			date_deb=datetime.now()
			zoom_plot.text(myaxis[0],myaxis[3]*0.95," "+date_deb.ctime())
			zoom_plot.text(myaxis[1]*0.4,myaxis[3]*0.95,"TLP Curve", color='r')
			zoom_plot.text(myaxis[1]*0.4,myaxis[3]*0.9,"Leakage Curve", color='b')
			zoom_plot.grid(True)

			if not self.my_leak_analysis == None:
				if not self.my_leak_analysis.leak_tab.shape[0] < self.tlp_data[1].shape[0]:
					if len(self.my_leak_analysis.rising) > 0:
						zoom_plot.axhspan(self.tlp_data[1][self.my_leak_analysis.fail_index-1], myaxis[3], facecolor='r', alpha=0.5)
						if len(self.my_leak_analysis.rising) > 1:
							zoom_plot.axhspan(self.tlp_data[1][self.my_leak_analysis.rising[0]], self.tlp_data[1][self.my_leak_analysis.falling[0]], facecolor='y', alpha=0.5)

						zoomb_plot=zoom_plot.twiny()
						zoomb_plot.set_ylim(0,2)

						if self.my_leak_analysis.leak_tab.shape[0] > self.tlp_data[1].shape[0]:
							leak_abs=np.array(self.my_leak_analysis.leak_tab[1:])

							zoomb_plot.semilogx(np.abs(leak_abs),self.tlp_data[1],'bs', markersize=3)
						else:
							leak_abs=np.array(self.my_leak_analysis.leak_tab)

							zoomb_plot.semilogx(np.abs(leak_abs),self.tlp_data[1],'bs', markersize=3)

						zoomb_plot.set_xlabel(r'Leakage Current [A]')
			zoom_fig.savefig(file_name+"_B.png") 
			
			textFile="[<img src=\"TLP_B.png\" align=\"center\" alt=\"TLPB\"> ](../"+self.devName+"_report.html)"
		 	text_output=md.markdown(textFile, extensions=['extra'])
			text_out=open(file_name+"_B.html","w")
			text_out.write(text_output)
			text_out.close()

			
	def make_extraction_plot(self,file_name):
		extract_fig=Figure()
		canvas = FigureCanvas(extract_fig)
		ext_plot = extract_fig.add_subplot(111)
	
		ext_plot.plot(self.tlp_data[0],self.tlp_data[1],'ro', markersize=3)
		myaxis=ext_plot.axis()
		ext_plot.hold(True)
		
		if self.is_snapback and self.fitting:
			ext_plot.plot(self.y_val,self.x_val)
			ext_plot.axhspan(self.tlp_data[1][self.sbIndex], self.tlp_data[1][self.endPoint], facecolor='b', alpha=0.2)
			sb_str=" Vsb:{0:.2}V, Ron:{1:.3}".format(self.p[1],self.p[0])
			annotI=(self.endPoint-self.sbIndex)/2+self.sbIndex
			ext_plot.annotate(sb_str,xy=(self.volt[annotI],self.curr[annotI]),xytext=(0,self.curr[annotI]), 			arrowprops=dict(width=1,frac=0,headwidth=0,color='blue',shrink=0.05),color='b')
		if self.is_multi and self.fittingLast:
			ext_plot.plot(self.y_val2,self.x_val2)
			ext_plot.axhspan(self.tlp_data[1][self.newSbkIndex], self.tlp_data[1][self.newEndPoint], facecolor='g', alpha=0.2)
			sb_str=" Vsb:{0:.2}V, Ron:{1:.3}".format(self.p2[1],self.p2[0])
			annotI=(self.newEndPoint-self.newSbkIndex)/2+self.newSbkIndex
			ext_plot.annotate(sb_str,xy=(self.volt[annotI],self.curr[annotI]),xytext=(0,self.curr[annotI]), 			arrowprops=dict(width=1,frac=0,headwidth=0,color='green',shrink=0.05),color='g')
		if not self.is_snapback and self.fitting:
			ext_plot.plot(self.y_val,self.x_val)
			pfit=np.poly1d([self.p[1],self.p[2]])
			#x_val=np.linspace(0,np.max(curr),50)
			y_fit=np.polyval(pfit,self.x_val)
			ext_plot.plot(y_fit,self.x_val,':')
			ext_plot.axhspan(self.tlp_data[1][self.sbIndex], self.tlp_data[1][self.endPoint], facecolor='b', alpha=0.2)
			sb_str=" Vsb:{0:.4}V, Ron:{1:.4}".format(self.p[2],self.p[1])
			annotI=(self.endPoint-self.sbIndex)/2+self.sbIndex
			ext_plot.annotate(sb_str,xy=(self.volt[annotI],self.curr[annotI]),xytext=(0,self.curr[annotI]), 			arrowprops=dict(width=1,frac=0,headwidth=0,color='blue',shrink=0.05),color='b')


		ext_plot.set_xlabel(r'Voltage [V]')
		ext_plot.set_ylabel(r'Current [A]')
		
		if np.max(self.tlp_data[0]) <= 0:
			ext_plot.set_xlim(myaxis[0],0)
		else:
			ext_plot.set_xlim(0,myaxis[1])
		if np.max(self.tlp_data[1]) <= 0:
			ext_plot.set_ylim(myaxis[2],0)
		else:
			ext_plot.set_ylim(0,myaxis[3])

		date_deb=datetime.now()
		ext_plot.text(myaxis[0],myaxis[3]*0.95," "+date_deb.ctime())
		if self.is_snapback:
			if self.curr[self.kInd]>myaxis[2]:
				ext_plot.axhline(self.curr[self.kInd], color='m')
				ext_plot.text(myaxis[0],self.curr[self.kInd]," {0:.3}A".format(self.curr[self.kInd]),color='m')
			ext_plot.axvline(self.volt[self.kInd],color='m')
			ext_plot.text(self.volt[self.kInd],0.95*myaxis[3],"{0:.4}V ".format(self.volt[self.kInd]),color='m',rotation=270)
		ext_plot.grid(True)
		ext_plot.set_title(self.devName+" Extraction Data from TLP curve")
		extract_fig.savefig(file_name) 
		
		textFile="[<img src=\"TLP_C.png\" align=\"center\" alt=\"TLPC\"> ](../"+self.devName+"_report.html)"
	 	text_output=md.markdown(textFile, extensions=['extra'])
		text_out=open(file_name[:-4]+".html","w")
		text_out.write(text_output)
		text_out.close()
		
		
	def update_analysis(self):
		self.is_snapback=False
		self.is_multi=False
		self.start_region=[]
		self.end_region=[]
		self.trig_inf=[]		
		
		baseDir=self.baseDir
		if self.has_leakage_ivs:
			self.my_leak_analysis.update_leakage_analysis(self.tlp_data)

		if self.has_leakage_evolution:
			self.my_leak_analysis.update_evol_analysis(self.tlp_data)
			
		kInd=self.extract_triggering_point(self.seuil)

		trig_inf=self.set_triggering_str()
		self.get_fitting_data()

		
		self.make_derivative_plot(baseDir+'/report_analysis/derivative.png')

		self.make_tlp_plot(baseDir+'/report_analysis/TLP')
		
		
		self.make_extraction_plot(baseDir+'/report_analysis/TLP_C.png')


				