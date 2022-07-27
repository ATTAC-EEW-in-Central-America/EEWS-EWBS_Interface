import datetime
import pandas as pd
import platform, os, sys
import logging
#from ciso8601 import parse_datetime # faster but installing this library is a kind of pain
from dateutil.tz import tzutc, tzlocal
import logging

logging.basicConfig(level=logging.DEBUG)
logIdentifier = 'LOGPARSER'

onlyAMQ = False
onlyJSON = False
fullUpdate = False
#Windows or Linux
OS = platform.uname()[0]

#### Read data Method #####
#this method reads data for a defined amount of days
#from hb.log and reports.json files
#The input arguments are: 
#
#numDays 
#baseFolder (where to start looping for example CostaRica\)
#
#and returns a pd.Dataframe from json file and a string from log text file
def readLogs(numDays,baseFolder):
	now = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S') # for logging purposes
	
	if fullUpdate == True:
		numDays = 365
	log('reading JSON and HB log information for %s days and from the base folder: %s' % (numDays,baseFolder) )
	endDT = datetime.datetime.utcnow()					#today is the end Date and Time
	startDT = endDT -  datetime.timedelta(days=numDays)	#the starting day... 30 days ago
	stringData = '' 									#an empty string
	jsonData = pd.DataFrame() 								#an empty DataFrame
	
	for singleDay in (startDT + datetime.timedelta(n) for n in range(numDays+1)):
		
		year = singleDay.strftime("%Y")
		month = singleDay.strftime("%m")
		day = singleDay.strftime("%d")
		
		#cheking the OS type to verify folders
		if OS== 'Windows':
			folder = baseFolder+'\\'+year+'\\'+month+'\\'+day+'\\'
		else:
			folder = baseFolder+'/'+year+'/'+month+'/'+day+'/'
		
		#Checking if the folder exists
		if os.path.exists(folder): # as reference where this script runs
			#good, so let's see if the files exist, too
			
			#hb log
			if not onlyJSON:
				if os.path.exists(folder+'hb.log'):
					#great!
					tmp = ''
					f = open(folder+'hb.log','r')
					tmp = f.read()
					f.close()
					if len(tmp)> 0:
						stringData += tmp

			#reports json
			if not onlyAMQ:
				if os.path.exists(folder+'reports.json'):
					#nice
					try:
						f = pd.read_json(folder+'reports.json')
						#print f.size
						if f.size > 0:
							#print f.size 
							#Concat df and new data in the f dataframe
							jsonData = pd.concat([jsonData,f])
					except Exception as e:
						log( 'there were an error reading data in %s' % folder+'reports.json' )
						log(repr(e) )
						
	now = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
	
	if len(stringData) > 0:
		log(' read: %s lines from HB logs and %s size of JSON file' % (len(stringData.split("\n")), jsonData.size) )
	else:
		log(' read: 0 lines from HB logs and %s size of JSON file' %  jsonData.size )
	return stringData, jsonData

#### Parse HB log file #####
def parseHBlog(stringFile):
	x = [] #datetime objects for plotting purpose
	y = [] #Delta values received - hb datetime in seconds
	histHb = [] #this contains delta times but only less than 5 seconds - TODO: Check if this is still logic
	
	now = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
	
	log(': Parsing HB information from %s lines' % len(stringFile.split('\n') ) )
	
	for line in stringFile.split("\n"):
		if 'hbtime' in line:
			lineSplit = line.split(',')
			try:
				
				tmp = lineSplit[0].split('hbtime:')[1]
				hbTime = datetime.datetime.strptime(tmp, '%Y-%m-%dT%H:%M:%S.%fZ').replace(tzinfo = tzutc())
				#hbTime =  parse_datetime(tmp)
				recMsg =  lineSplit[1].split("receiveTime:")[1]
				recMsg = datetime.datetime.strptime(recMsg, '%Y-%m-%dT%H:%M:%S.%fZ').replace(tzinfo = tzutc())
				#recMsg = parse_datetime(lineSplit[1].split("receiveTime:")[1])
				
				if 'deltaVal' in line:
					valDiff = float(lineSplit[2].split('deltaVal:')[1])
				else:
					valDiff = (recMsg - hbTime).total_seconds()	
				
				if valDiff < 1 and valDiff>-1:
					x.append(recMsg) 
					y.append(valDiff)
					histHb.append(valDiff)
			
			except Exception as e:
				log( 'not possible to parse the next line:')
				log( lineSplit )
				log( repr(e) )
	
	dataframe = pd.DataFrame([x,y]).transpose()
	dataframe.columns = ['dtObj','deltaAMQ']
	
	deltaAMQ = pd.DataFrame([histHb]).transpose()
	deltaAMQ.columns = ['deltaAMQ']
	
	now = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
	
	log(' Create a dataframe of %s size for deltaAMQ timeline and %s size of deltaAMQ for histogram' % (dataframe.size,deltaAMQ.size) )
	return dataframe, deltaAMQ
	

#### Parse JSON file ####
def parseJSON(jsonData):
	
	deltaSC = []
		
	deltaSCx = []
	deltaSCy = []	
	magValSC = []
	ortimeSC = []
	evtidSC = []
	
	deltaEWBS = []		
						
	deltaEWBSy = []		
	deltaEWBSx =  []
	magValEWBS = [] 	
	transTimeEWBS = []
	evtidEWBS = []
	
	deltaEWBSupdatex = [] 
	deltaEWBSupdatey = []
	magValEWBSupdate = []
	
	otTransmittedFTx = [] 
	otTransmittedFTy = [] 
						
	otTransmittedUpx = [] 
	otTransmittedUpy = [] 
						
	otNotTransmitttedx = []
	otNotTransmitttedy = []
	
	
	#the next y value will be the difference between received alert time and OriginTime
	deltaNotTransEWBSx = [] # gray light
	deltaNotTransEWBSy = [] # gray light
	magValEWBSnotTrans = []
	
	now = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
	
	log( ' parsing a dataframe of %s size obtained from JSON files' % jsonData.size )
	
	#going through the json data
	#TODO - Improve this code using PANDAS
	for index,row in jsonData.iterrows():
		#transmitted for the first time
		try:
			dtOT = datetime.datetime.strptime(row['originTime'], '%Y-%m-%dT%H:%M:%S.%fZ').replace(tzinfo = tzutc()) #from str to datetime obj
		except:
			log( 'Origin Time: not possible to obtain a datetime object for %s' % row['originTime'] )
			continue
		recAlertTimeSecs =   datetime2timestamp(row['receivedAlertTime'])
		if recAlertTimeSecs == 0:
			log( 'error to obtain receive alert time from %s' % row['receivedAlertTime'] )
			continue
			
		#DeltaSeisComP
		try:
			magCreationTime = row['magnitudeCreation'].split('.')[0]+'.'+row['magnitudeCreation'].split('.')[1][:-3]+'Z'
			dtMagCreationTime = datetime.datetime.strptime(magCreationTime, '%Y-%m-%dT%H:%M:%S.%fZ').replace(tzinfo = tzutc())
			magCreationTimeSecs =  datetime2timestamp(magCreationTime)
			otSecs = datetime2timestamp(row['originTime'])
			magVal = row['magnitude']
			#DELTA SEISCOMP!
			#if row['firstTime'] == 1 and row['broadcasted'] == 1:
			if row['broadcasted'] == 1 and row['firstTime'] == 1:
				deltaSCval = magCreationTimeSecs - otSecs
				deltaSC.append(deltaSCval)
				deltaSCx.append(dtMagCreationTime)
				deltaSCy.append(deltaSCval)
				magValSC.append(magVal)
				ortimeSC.append(row['originTime'])
				evtidSC.append(row['id'])
				
		except Exception as e:
			log( 'There was an error while obtaining delta SC values. see below\n' )
			log( repr( e ) )
			#deltaSC.append(-1) # error
		
		if row['broadcasted'] == 1:
			
			startTransmission = row['startTransmission'].split('.')[0]+'.'+row['startTransmission'].split('.')[1][:-3]+'Z'
			
			startTransSecs =  datetime2timestamp(startTransmission)
			
			if startTransSecs == 0:
				log( 'error to obtain Start Transmission Time from %s' % row['startTransmission'] )
				continue
			
			try:
				transTime = datetime.datetime.strptime(startTransmission, '%Y-%m-%dT%H:%M:%S.%fZ').replace(tzinfo = tzutc())
			except:
				log( 'not possible to obtain the start transmission time from string for %s' % startTransmission )
				continue
			deltaVal = startTransSecs - recAlertTimeSecs
				
			#First Time transmitted
			if row['firstTime'] == 1:
				
				otTransmittedFTx.append(dtOT) #adding dtOT to otTransmittedx
			
				otTransmittedFTy.append(5) #appending a fixed time
			
				deltaEWBSy.append(deltaVal)
			
				deltaEWBS.append(deltaVal) #for the Histogram
			
				deltaEWBSx.append(transTime)
				
				magValEWBS.append(magVal)
				
				transTimeEWBS.append(row['startTransmission'])
				
				evtidEWBS.append(row['id'])
		
			#updated transmission broadcasted but not the first time
			elif row['firstTime'] == 0:
				otTransmittedUpx.append(dtOT)
				
				otTransmittedUpy.append(5) #appending a fixed time
				
				deltaEWBSupdatey.append(deltaVal) #obtaining deltaEWBSy
				
				deltaEWBS.append(deltaVal)
			
				deltaEWBSupdatex.append(transTime)
				
				magValEWBSupdate.append(magVal)
		else:
			
			try:
				tmp = datetime.datetime.strptime(row['receivedAlertTime'], '%Y-%m-%dT%H:%M:%S.%fZ').replace(tzinfo = tzutc())
			except:
				log( 'receivedAlertTime: not possible to obtain datetime obj for %s' % row['receivedAlertTime'] )
				continue
			
			otNotTransmitttedx.append(dtOT)	#adding dtOT to otTransmittedx
			
			otNotTransmitttedy.append(5)	#appending a fixed time
			
			recAlertTimeSecs =   datetime2timestamp(row['receivedAlertTime']) #obtaining deltaEWBSy
			
			ot =  datetime2timestamp(row['originTime'])
			
			deltaVal = recAlertTimeSecs - ot
			
			deltaNotTransEWBSy.append(deltaVal)
			
			deltaNotTransEWBSx.append(tmp)
			
			magValEWBSnotTrans.append(magVal)
	
	dfList = []		#dataframe for all the lists related to Delta EWBS
	dfDeltaSC = []	#dataframe for all the lists related to DeltaSeisComP
	
	temp = pd.DataFrame([deltaSC]).transpose()
	temp.columns = ['deltaSC']
	dfDeltaSC.append(temp)
	
	temp = pd.DataFrame([deltaSCx, deltaSCy, magValSC, ortimeSC, evtidSC]).transpose()
	temp.columns = ['dtObj', 'deltaSC','magnitude','ortime','evtid']
	#saving a datetime object
	temp["ortime"] = pd.to_datetime(temp['ortime'], format="%Y-%m-%dT%H:%M:%S.%fZ")
	dfDeltaSC.append(temp)
	
	
	temp = pd.DataFrame([deltaEWBS]).transpose()
	temp.columns = ['deltaEWBS']
	dfList.append(temp)
	
	temp = pd.DataFrame([deltaEWBSx, deltaEWBSy, magValEWBS, transTimeEWBS,evtidEWBS]).transpose()
	temp.columns = ['dtObj', 'deltaEWBS','magnitude','transTime','evtid']
	temp["transTime"] = pd.to_datetime(temp['transTime'], format="%Y-%m-%dT%H:%M:%S.%fZ")
	dfList.append(temp)
	
	temp = pd.DataFrame([deltaEWBSupdatex, deltaEWBSupdatey]).transpose()
	temp.columns = ['dtObj', 'deltaEWBSupdate']
	dfList.append(temp)
	
	temp = pd.DataFrame([otTransmittedFTx, otTransmittedFTy]).transpose()
	temp.columns = ['dtObj', 'otTransmittedFT']
	dfList.append(temp)
	
	temp = pd.DataFrame([otNotTransmitttedx, otNotTransmitttedy]).transpose()
	temp.columns = ['dtObj', 'otNotTransmittted']
	dfList.append(temp)
	
	temp = pd.DataFrame([deltaNotTransEWBSx, deltaNotTransEWBSy]).transpose()
	temp.columns = ['dtObj', 'deltaNotTransEWBS']
	dfList.append(temp)
	now = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
	
	log(' obtained a %s size from deltaSC and a %s size for deltaEWBS' % (dfDeltaSC[0].size, dfList[0].size) )
	return dfDeltaSC,dfList
	
init = datetime.datetime(1970, 1, 1)
init = init.replace(tzinfo = tzutc())
#Datetime String to Unix timestamp in seconds (float)
def datetime2timestamp(strdt):
	try:
		val = datetime.datetime.strptime(strdt,'%Y-%m-%dT%H:%M:%S.%fZ').replace(tzinfo = tzutc())
		#val = parse_datetime(strdt)
		#return float((val - datetime.datetime(1970, 1, 1)).total_seconds())
		return float((val - init).total_seconds())
	except Exception as e:
		log( repr( e ) )
		return 0
		
def log(msg):
	now = datetime.datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S(UTC)')
	try:
		logging.debug(now+' - '+logIdentifier+": %s" % msg)
	except Exception as e:
		logging.debug("error in logging!: %s" % e)
