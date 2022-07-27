from bokeh.plotting import figure,output_file,show
from scipy.stats.kde import gaussian_kde
from numpy import histogram, linspace
import numpy as np
from bokeh.models import HoverTool

import datetime
#logging
import logging


logging.basicConfig(level=logging.DEBUG)

logIdentifier = 'GRAPHGEN'


class GraphGen:
	'''
		Graph Generator 
	'''
	
	def __init__(self):
		#the below atributes will only contain dictionaries
		#where keys will be country names and values dfs
		self.today = {}
		self.last24hours = {}
		self.yda = {}
		self.lastWeek = {}
		self.lastMonth = {}
		self.userSelectData = {}
	#
	# all the graphs method (histograms and timelines) 
	# receive as inputs
	# dfDic that is a dictionary where the key are country names
	# and the values are dataframes
	#
	
	def histogramAMQ(self, dfDic, dimension, colors):
		#histogram for deltaAMQ
		#the dfDic is a dictionary that contains the data for each country listed in countries
		#
		histAMQ = figure(plot_width = dimension['width'], plot_height = dimension['height'],title=u'\u0394 ActiveMQ - Histogram and Gaussian KDE')
		
		for country in dfDic:
			deltaAMQ = dfDic[country]['deltaAMQ']
			if dfDic[country]['deltaAMQ'].size > 1:
				values = deltaAMQ['deltaAMQ'].dropna().astype(float)
			else:
				log( 'No data for deltaAMQ histogram for ' + country )
				continue
			
			hist, edges = histogram(values, density=True, bins=20)
			histAMQ.quad(right=hist, left=0, bottom=edges[:-1], top=edges[1:], alpha=0.1,\
			fill_color=colors[country], line_color=colors[country],legend_label = country)
			
			minVal = np.percentile(values,1)
			maxVal = np.percentile(values,99)
			pdf = gaussian_kde(values)
			x = linspace(minVal,maxVal,64)
			histAMQ.line(pdf(x),x,line_color=colors[country],legend_label = country)
	
		
		histAMQ.x_range.flipped = True
		histAMQ.yaxis.axis_label = u'\u0394ActiveMQ [s]'
		histAMQ.xaxis.axis_label = u' '
		histAMQ.legend.location = "top_left"
		histAMQ.legend.click_policy="hide"
		
		return histAMQ
	
	def histogramEWBS(self, dfDic, dimension, colors):
		#Histogram for EWBS
		histEWBS = figure(plot_width = dimension['width'], plot_height = dimension['height'],title=u'\u0394EWBS - Histogram and Gaussian KDE')
	
		for country in dfDic:
			deltaEWBS = dfDic[country]['deltaEWBS']
			if dfDic[country]['deltaEWBS'].size > 3 :
				values = deltaEWBS['deltaEWBS'].dropna().astype(float)
			else:
				log( 'No enough data for deltaEWBS histogram for ' + country )
				continue
				
			hist, edges = histogram(values, density=True, bins=20)
			histEWBS.quad(right=hist, left=0, bottom=edges[:-1], top=edges[1:], alpha=0.1,\
			fill_color=colors[country], line_color=colors[country],legend_label = country)
			pdf = gaussian_kde(values)
			#minval = values.min()
			#maxval = values.max()
			minVal = np.percentile(values,1)
			maxVal = np.percentile(values,99)
			#interval = int((maxval -minval)*0.1)
			x = linspace(minVal,maxVal,64)
			histEWBS.line( pdf(x),x,line_color=colors[country],legend_label = country )
		
		histEWBS.x_range.flipped = True
		histEWBS.yaxis.axis_label = u'\u0394EWBS [s]'
		histEWBS.xaxis.axis_label = u' '
		histEWBS.legend.location = "top_left"
		histEWBS.legend.click_policy="hide"
		
		return histEWBS
	
	
	def histogramSC(self, dfDic, dimension, colors):
		#Histogram for deltaSC
		histSC = figure(plot_width = dimension['width'], plot_height = dimension['height'], title=u'\u0394SC - Histogram and Gaussian KDE')
		
		#
		for country in dfDic:
			#print dfDic[country]['deltaSC']['deltaSC'].dropna().astype(float), country
			deltaSC = dfDic[country]['deltaSC']
			if dfDic[country]['deltaSC'].size  > 3:
				values = deltaSC['deltaSC'].dropna().astype(float)
			else:
				log( 'No enough data for deltaSC histogram for ' + country )
				continue
			hist, edges = histogram(values, density=True, bins=20)
			histSC.quad(right=hist, left=0, bottom=edges[:-1], top=edges[1:], alpha=0.2,\
			fill_color=colors[country], line_color=colors[country],legend_label = country)
			
			pdf = gaussian_kde(values)
			
			#minval = values.min()
			#maxval = values.max()
			minVal = np.percentile(values,1)
			maxVal = np.percentile(values,99)
			#interval = int((maxval -minval)*0.1)
			x = linspace(minVal,maxVal,64)
			histSC.line(pdf(x),x,line_color=colors[country],legend_label = country)
		
		histSC.x_range.flipped = True
		histSC.yaxis.axis_label = u'\u0394SC [s]'
		histSC.xaxis.axis_label = u' '
		histSC.legend.location = "top_left"
		histSC.legend.click_policy="hide"
	
		return histSC
	
	def timelineEWBS(self, dfDic, dimension, colors, y_range, x_range=None):
		#timeline for deltaEWBS 
		tooltipsEnabled = False
		
		for country in dfDic:
			if dfDic[country]['dfEWBS'].columns.size == 2:
				tooltipsEnabled = False
				break
			elif dfDic[country]['dfEWBS'].columns.size > 2:
				tooltipsEnabled = True
		
		if tooltipsEnabled:
			hover = HoverTool(
			tooltips = [
					('Event ID', "@evtid"),
					('Magnitude', "@magnitude{0.0}"),
					('Trans. Time (UTC)', "@transTime{%Y-%m-%d %H:%M:%S}"),
					(u'\u0394 EWBS [s]', '@deltaEWBS{0.0}')
					],
			formatters={
					'@transTime': 'datetime'
					}
			)
			deltaEWBS_plot = figure(plot_width = dimension['width'], plot_height = dimension['height'], x_axis_type="datetime",
							title=u'\u0394EWBS - Timeline', y_range=y_range, x_range=x_range)
			deltaEWBS_plot.add_tools(hover)
		else:
			deltaEWBS_plot = figure(plot_width = dimension['width'], plot_height = dimension['height'], x_axis_type="datetime",
							title=u'\u0394EWBS - Timeline', y_range=y_range, x_range=x_range)
		
		for country in dfDic:
			dfEWBS = dfDic[country]['dfEWBS']
			if dfEWBS.size  == 0:
				log(  'No data for delta EWBS timeline for '+country )
				continue
			dfEWBS["magnitude"] = dfEWBS["magnitude"].astype(float).round(1)
			if dfDic[country]['dfEWBS'].columns.size == 2 or not tooltipsEnabled:
				deltaEWBS_plot.triangle(
								x='dtObj',y='deltaEWBS', size = 5,
								color=colors[country],
								legend_label = country,
								source= dfEWBS
								)
			else:
				deltaEWBS_plot.triangle(
								x='dtObj',y='deltaEWBS', size = 'magnitude',
								color=colors[country],
								legend_label = country,
								source= dfEWBS
								)
	
		deltaEWBS_plot.xaxis.axis_label = 'Date and Time'
		deltaEWBS_plot.yaxis.axis_label = u'\u0394EWBS [s]'
		
		deltaEWBS_plot.legend.location = "top_left"
		deltaEWBS_plot.legend.click_policy="hide"
	
		return deltaEWBS_plot
	
	def timelineSC(self, dfDic, dimension, colors, y_range, x_range=None):          
		tooltipsEnabled = False
		#timeline for deltaSC
		for country in dfDic:
			if dfDic[country]['dfSC'].columns.size == 2:
				tooltipsEnabled = False
				break
			elif dfDic[country]['dfSC'].columns.size > 2:
				tooltipsEnabled = True
		
		if tooltipsEnabled:
			hover = HoverTool(
			tooltips = [
					('Event ID', "@evtid"),
					('Magnitude', "@magnitude{0.0}"),
					('Origin Time (UTC)', "@ortime{%Y-%m-%d %H:%M:%S}"),
					(u'\u0394 SC [s]', '@deltaSC{0.0}')
					],
			formatters={
					'@ortime': 'datetime'
					}
			)
			deltaSC_plot = figure(plot_width = dimension['width'], plot_height = dimension['height'],x_axis_type="datetime",
							title=u'\u0394SC- Timeline', y_range=y_range, x_range=x_range)
			deltaSC_plot.add_tools(hover)
		else:
			deltaSC_plot = figure(plot_width = dimension['width'], plot_height = dimension['height'],x_axis_type="datetime",
							title=u'\u0394SC- Timeline', y_range=y_range, x_range=x_range)
					
		for country in dfDic:
			dfSC = dfDic[country]['dfSC']
			if 	dfSC.size  == 0:
				log(  'No data for delta SC timeline for '+country )
				continue
			if dfDic[country]['dfSC'].columns.size == 2 or not tooltipsEnabled:
				deltaSC_plot.circle(
								x='dtObj',y='deltaSC', size = 5,
								color=colors[country],
								legend_label = country,
								source= dfSC
								)
			else:
				deltaSC_plot.circle(
								x='dtObj',y='deltaSC', size = 'magnitude',
								color=colors[country],
								legend_label = country,
								source= dfSC
								)
				
				
		deltaSC_plot.xaxis.axis_label = 'Date and Time'
		deltaSC_plot.yaxis.axis_label = u'\u0394 SC [s]'
		
		deltaSC_plot.legend.location = "top_left"
		deltaSC_plot.legend.click_policy="hide"
			
		return deltaSC_plot
	
	def timelineAMQ(self, dfDic, dimension, colors, y_range, x_range=None):
		#timeline for deltaAMQ or heartbeats
		for country in dfDic:
			dfAMQ = dfDic[country]['dfAMQ']
		hover = HoverTool(
						tooltips = [
							('Date and Time', "$x{%Y-%m-%d %H:%M:%S}"),
							(u'\u0394ActiveMQ [s]','$y{0.00}')
						],
						formatters={
							'$x': 'datetime'
						}
						)
		
		deltaAMQ_plot = figure(plot_width = dimension['width'], plot_height = dimension['height'], x_axis_type="datetime",
							title=u'\u0394 ActiveMQ - Timeline', y_range=y_range, x_range=x_range)
		deltaAMQ_plot.add_tools(hover)
		
		for country in dfDic:
			dfAMQ = dfDic[country]['dfAMQ']
			
			if dfAMQ.size  == 0:
				log( 'No data for delta AMQ timeline for '+country )
				continue
			
			#deltaAMQ_plot.line(
			#				x='dtObj',y='deltaAMQ',
			#				line_width=0.5, line_color=colors[country],
			#				legend_label = country,
			#				source= dfAMQ,
			#				alpha=0.5
			#				)
			deltaAMQ_plot.circle(x='dtObj',y='deltaAMQ', 
								size=1.5, fill_color=colors[country], 
								line_color=colors[country], 
								line_width=1, 
								source= dfAMQ,
								legend_label = country )
									
		deltaAMQ_plot.xaxis.axis_label = 'Date and Time'
		deltaAMQ_plot.yaxis.axis_label = u'\u0394ActiveMQ [s]'
		deltaAMQ_plot.legend.location = "top_left"
		deltaAMQ_plot.legend.click_policy="hide"
		
		return deltaAMQ_plot
def log( msg ):
	#just logging information
	#it does not log anything if this is running with bokeh serve option
	now = datetime.datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S(UTC)')
	logging.debug(now+' - '+logIdentifier+": "+msg)
