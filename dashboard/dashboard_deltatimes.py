#bokeh
from bokeh.io import curdoc
from bokeh.plotting import figure,output_file,save,show
from bokeh.layouts import row, column
# Widgets
from bokeh.models import Select
from bokeh.models.widgets import Div
from bokeh.models.widgets import Panel, Tabs
#
import datetime
import os, sys
import platform
from dateutil.tz import tzutc, tzlocal
#local
import pklmanage, graphgen
#logging
import logging

logging.basicConfig(level=logging.DEBUG)

########## USER CONFIG ################
showme = False
# A string to identify the log information of this script
logIdentifier = 'DASHBOARD'

#A list of countries. It can be just one.
countries  = ['Costa Rica','Nicaragua','El Salvador']

#The colors that represent to each country in a dictionary
#Please write the countries' name as it was written in the countries list
countryColor = {"Costa Rica":"blue", "Nicaragua":"orange", "El Salvador":"green"}

output_file('dashboard_deltatimes.html',title='dashboard DeltaTimes')


########## END USER CONFIG#############

#
html = False
if len(sys.argv) == 2:
	if sys.argv[1].lower() == 'html':
		html = True
	else:
		print('command line option: html')
		exit(0)
countryData = {} # the dataframes for each country
 

countryAval = {} # the datetime object to know the last updated date and time
layout_with_widgets = None
for country in countries:
	countryData[country] = None
	countryAval[country] = None
checkbox_options = countries 

manager= pklmanage.PickleDataManage() # instancing a PickleDataManage class
gg = graphgen.GraphGen()

#Windows or Linux
OS = platform.uname()[0]



#default values for screen width (sWidth) and height (sHeight)
sWidth = 1000
sHeight = 800
#histogram height and width
histHeight = int(0.7*sHeight)
histWidth = int(0.4*sWidth)
#timelines height and width
tlHeight = int(0.7*sHeight)
tlWidth = int(0.55*sWidth)


def setScreenSize(sWidth=sWidth,sHeight=sHeight):
	# This function will override the defined values for sWidth and sHeight and tlHeight and tlWidth
	# based on the screen size if no errors
	if OS == 'Windows':
		log('this is Windows OS')
		import ctypes
		sWidth = ctypes.windll.user32.GetSystemMetrics(0)
		sHeight = ctypes.windll.user32.GetSystemMetrics(1)
		log( 'screen width: %s, screen height: %s' % (sWidth, sHeight) )
	else :
		#linux or mac(?)
		log('this is Linux OS')
		import subprocess
		import re
		matchObj=False
		try:
			xrandrOutput = str(subprocess.Popen(['xrandr'], stdout=subprocess.PIPE).communicate()[0])
			matchObj = re.findall(r'current\s(\d+) x (\d+)', xrandrOutput)
		except:
			print('Cannot use xrandr')
		if matchObj:
			sWidth = int(matchObj[0][0])
			sHeight = int(matchObj[0][1])
		else:
			sWidth = 2560/1.7 #1000
			sHeight = 1600/5 #800

	#setting the global variables for the height and width for histograms and
	#timeline plots	
	histHeight = int(0.7*sHeight)
	histWidth = int(0.4*sWidth)
	
	tlHeight = int(0.7*sHeight)
	tlWidth = int(0.55*sWidth)
	
	log( 'histograms width and height are: %s and %s' % (histWidth, histHeight) )
	log( 'timelines width and height are: %s and %s' % (tlWidth, tlHeight) )
	
	return sWidth, sHeight, histWidth, histHeight, tlWidth, tlHeight
	
	

def log( msg ):
	#just logging information
	#it does not log anything if this is running with bokeh serve option
	now = datetime.datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S(UTC)')
	logging.debug(now+' - '+logIdentifier+": "+msg)
		


def readData(dtStart, dtEnd):
	# Based on a start and end datetime object, this function will request data
	# for each country listed in the countries list.
	for country in countries:
		
		
		#checking availability
		aval = manager.getAvailability(country)
		
		if aval == 1 or aval == -1 :
			#no availability information for this country
			#next country
			continue
		
		#setting date and time of availability
		countryAval[country] = datetime.datetime.strptime(aval['updateDatetime'], '%Y-%m-%dT%H:%M:%S.%fZ')
		
		#data for this country
		countryData[country] = manager.getData(dtStart, dtEnd, country)
	
	return countryData
		
drop_bar = Select(title="Data Period", value="Last 24 Hours",
                options=["Last 24 Hours", "Today", "Yesterday", "Last Week", "Last Month", "Last Year"])
                
def getGraphs(timePeriod):
	now = datetime.datetime.utcnow().replace( tzinfo = tzutc() )
	#endDt = datetime.datetime( now.year, now.month, now.day ).replace( tzinfo = tzutc() )
	startDt = 0
	endDt = 0
	if timePeriod == 'Today':
		endDt = now
		delta = datetime.timedelta( days = 0 )
		startDt = ( now  - delta)
		startDt = datetime.datetime(startDt.year, startDt.month, startDt.day).replace( tzinfo = tzutc() )
	#	countryData = readData(startDt, endDt)
			
	elif timePeriod == 'Last 24 Hours':
		endDt = now
		delta = datetime.timedelta( days = 1 )
		startDt = ( now  - delta).replace( tzinfo = tzutc() )
	#	countryData = readData(startDt, endDt)
			
	elif timePeriod == 'Yesterday':
		endDt = datetime.datetime(now.year, now.month, now.day).replace( tzinfo = tzutc() )
		delta = datetime.timedelta( days = 1 )
		startDt = (now - delta)
		startDt = datetime.datetime(startDt.year, startDt.month, startDt.day).replace( tzinfo = tzutc() )
	#	countryData = readData(startDt, endDt)
			
	elif timePeriod == 'Last Week':
		endDt = now
		delta = datetime.timedelta( days = 7 )
		startDt = (now - delta)
		startDt = datetime.datetime(startDt.year, startDt.month, startDt.day).replace( tzinfo = tzutc() )
	#	countryData = readData(startDt, endDt)
			
	elif timePeriod == 'Last Month':
		endDt = now
		delta = datetime.timedelta( days = 30 )
		startDt = (now - delta)
		startDt = datetime.datetime(startDt.year, startDt.month, startDt.day).replace( tzinfo = tzutc() )
	
	elif timePeriod == 'Last Year':
		endDt = now
		delta = datetime.timedelta( days = 365 )
		startDt = (now - delta)
		startDt = datetime.datetime(startDt.year, startDt.month, startDt.day).replace( tzinfo = tzutc() )
	
	countryData = readData(startDt, endDt)
		
	histSC = gg.histogramSC(countryData, histDimensions, countryColor)
	histAMQ = gg.histogramAMQ(countryData, histDimensions, countryColor)
	histEWBS = gg.histogramEWBS(countryData, histDimensions, countryColor)
	deltaSC_plot = gg.timelineSC(countryData, tlDimensions, countryColor, y_range=histSC.y_range)
	deltaAMQ_plot = gg.timelineAMQ(countryData, tlDimensions, countryColor, y_range=histAMQ.y_range, x_range=deltaSC_plot.x_range)
	deltaEWBS_plot = gg.timelineEWBS(countryData, tlDimensions, countryColor, y_range=histEWBS.y_range, x_range=deltaSC_plot.x_range)
	#Defining the last updated date and time
	updateText = '<small><p  style="text-align: right;"><b>Last update</b>:'
	keyMax = max(countryAval.keys(), key=(lambda k: countryAval[k]))
	keyMin = min(countryAval.keys(), key=(lambda k: countryAval[k]))
	
	diff = ( countryAval[keyMax] - countryAval[keyMin] ).total_seconds()
	
	if diff>30: #more than 30 seconds, then it presents the information for all countries
		tmp=[]
		for country in countries:
			tmp.append( country+': '+countryAval[country].strftime("%Y-%m-%d %H:%M:%S (UTC)") )
		
		updateText += (', ').join(tmp)
	else:#other wise the last updated country
		updateText += countryAval[keyMax].strftime("%Y-%m-%d %H:%M:%S (UTC)")
	
	updateText += '<p></small>'
	
	#Finally setting the title with the info for the last updated date and time
	#print 'the screen: '+ str(sWidth)
	#title = Div(text='<h1 style="text-align: center">Delta times for SC, AMQ and EWBS</h1>'+updateText, style={'width':'1200px','font-size': '100%', 'color': 'black'})
	return [histSC, histAMQ, histEWBS, deltaSC_plot, deltaAMQ_plot, deltaEWBS_plot]
	
def updateGraphs(attrname, old, new):
	retGraphs = getGraphs(drop_bar.value) 
	
	layout_with_widgets.children[2].children[0].children[0] = retGraphs[0]
	layout_with_widgets.children[2].children[0].children[1] = retGraphs[1]
	layout_with_widgets.children[2].children[0].children[2] = retGraphs[2]
	layout_with_widgets.children[2].children[1].children[0] = retGraphs[3]
	layout_with_widgets.children[2].children[1].children[1] = retGraphs[4]
	layout_with_widgets.children[2].children[1].children[2] = retGraphs[5]
	
	

################################################################################	

drop_bar.on_change("value", updateGraphs)

# defining the final dimensions for the graphs
sWidth, sHeight, histWidth, histHeight, tlWidth, tlHeight = setScreenSize()

histDimensions = {
	'width': histWidth,
	'height': histHeight
}

tlDimensions = {
	'width': tlWidth,
	'height': tlHeight
}

#obtaining the now dt object with UTC tzinfo 
now = datetime.datetime.utcnow().replace(tzinfo = tzutc())
delta = datetime.timedelta(days=1)
startDt = ( now - delta ).replace( tzinfo = tzutc() )

#reading the data
countryData = readData(startDt, now)

#calling the functions to generate the plots


#Defining the last updated date and time
updateText = '<small><p  style="text-align: right;"><b>Last update</b>: '
keyMax = max(countryAval.keys(), key=(lambda k: countryAval[k]))
keyMin = min(countryAval.keys(), key=(lambda k: countryAval[k]))

diff = ( countryAval[keyMax] - countryAval[keyMin] ).total_seconds()

if diff>30: #more than 30 seconds, then it presents the information for all countries
	tmp=[]
	for country in countries:
		tmp.append( country+': '+countryAval[country].strftime("%Y-%m-%d %H:%M:%S (UTC)") )
	
	updateText += (', ').join(tmp)
else:#other wise the last updated country
	updateText += countryAval[keyMax].strftime("%Y-%m-%d %H:%M:%S (UTC)")

updateText += '<p></small>'

#Finally setting the title with the info for the last updated date and time

title = Div(text='<h1 style="text-align: center">Delta times for SC, AMQ and EWBS</h1>'+updateText, style={'width':'1200px','font-size': '100%', 'color': 'black'})

graphs = getGraphs('Last 24 Hours')
histSC = graphs[0]
histAMQ = graphs[1]
histEWBS = graphs[2]
deltaSC_plot = graphs[3]
deltaAMQ_plot = graphs[4]
deltaEWBS_plot = graphs[5]
layout_with_widgets = column( row(title),row(drop_bar), row( column( histSC, histAMQ, histEWBS ), column( deltaSC_plot, deltaAMQ_plot, deltaEWBS_plot) ) )
#Widgets layout
if html:
	timePeriods = ['Last 24 Hours', 'Today', 'Yesterday', 'Last Week', 'Last Month', 'Last Year']
	tabList = []
	for tp in timePeriods:
		
		#tmpTap = Panel(child=layout_with_widgets, title=tp)
		#layout_with_widgets = column( row(title),row(drop_bar), row( column( histSC, histAMQ, histEWBS ), column( deltaSC_plot, deltaAMQ_plot, deltaEWBS_plot) ) )
	
		graphs = getGraphs(tp)
		histSC = graphs[0]
		histAMQ = graphs[1]
		histEWBS = graphs[2]
		deltaSC_plot = graphs[3]
		deltaAMQ_plot = graphs[4]
		deltaEWBS_plot = graphs[5]
		layout_with_widgets = column( row( column( histSC, histAMQ, histEWBS ), column( deltaSC_plot, deltaAMQ_plot, deltaEWBS_plot)) )
		tmpTab = Panel(child=layout_with_widgets, title=tp)
		tabList.append(tmpTab)
	
	
	tabs = Tabs(tabs=tabList)
	mydashboard=column(row(title),tabs)
	save(mydashboard)
	if showme:
		show(mydashboard)
        #show(layout_with_widgets)
else:	
	curdoc().add_root(layout_with_widgets)


