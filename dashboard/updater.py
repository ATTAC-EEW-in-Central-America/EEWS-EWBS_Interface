#
#this program should be run as a service for updating information
#from log files to compressed dataframes bz2
#
# the heartbeats are resampled to one sample each 60 seconds (all the heartbeat samples within 60 seconds are averaged)
# with the purpose to save disk space and mainly processing time
#
import parselog
import pklmanage
import datetime, pytz
import platform
import pandas as pd
import os, sys
import logging
import glob


logging.basicConfig(level=logging.DEBUG)
logIdentifier = 'UPDATER'

#Windows or Linux
OS = platform.uname()[0]
#######USER CONFIG ###########
#
countries = ['El Salvador','Costa Rica','Nicaragua']

#set the name according to the OS (mainly taking care of using \ for windows and / for linux)
# folderpkl is where the compressed bz2 data is stored
# folderlog is where the logs are stored. In this case it is assumed that after
# folderlog is the countryname for example: log\CostaRica\
if OS == 'Windows':
	folderpkl = 'pickledata\\'
	userFolder = os.getenv('userprofile')
	folderlog = userFolder+'\ewbs-converter\eews2ewbs\log\\'
else:
	folderpkl = 'pickledata/'
	folderlog = 'log/'
####### End User Config ##########

pklmanager = pklmanage.PickleDataManage(folderpkl)

def log(msg):
	now = datetime.datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S(UTC)')
	logging.debug(now+' - '+logIdentifier+": "+msg)

def updateAll(countryName):
	#this function is called once per day
	#with the idea to remove data out of the
	#limits of dates that are meant to contain.
	#for the hb (heartbeats):
	#
	#files are today, yesterday, last week (starting from 
	#the day before yesterday up to 7 days ago)
	#and the complementary days until 30 days.
	#
	#example of file for a country:
	# 1. hb2021025CostaRica (today - year and julian day)
	# 2. hbYdaCostaRica (yesterday data)
	# 3. hbLwCostaRica (contains since 2 days ago to 7 days ago)
	# 4. hbCostaRica (since 7 days to 30 days ago)
	#
	#For EWBS and SC the filenames are:
	#
	# scCostaRica (SC)
	# ewbsCostaRica (EWBS)
	#
	
	log('Starting the full data update...')
	
	dtNow = datetime.datetime.utcnow().replace(tzinfo=pytz.UTC)
	dtToday = datetime.datetime( dtNow.year, dtNow.month, dtNow.day ).replace(tzinfo=pytz.UTC)
	delta = datetime.timedelta(days=1)
	tmp = (dtNow - delta).replace(tzinfo=pytz.UTC)
	dtYda = datetime.datetime( tmp.year, tmp.month, tmp.day ).replace(tzinfo=pytz.UTC)
	delta = datetime.timedelta(days=5)
	dtLastWeek = (dtYda - delta).replace(tzinfo=pytz.UTC)
	delta = datetime.timedelta(days=23)
	dtLastMonth = (dtLastWeek - delta).replace(tzinfo=pytz.UTC)
	delta =  datetime.timedelta(days=335)
	dtLastYear = (dtLastMonth - delta).replace(tzinfo=pytz.UTC)
	
	sCountry = ('').join(countryName.split(' '))
	
	#daily files. In case for old daily data 
	day = 'hb'+dtYda.strftime('2*')+ sCountry
	daysArr = glob.glob(folderpkl+day)
	today = 'hb'+dtNow.strftime('%Y%j')+ sCountry
	yda = 'hbYda'+sCountry
	lastWeek = 'hbLw'+sCountry
	lastMonth = 'hbLm'+sCountry
	lastYear = 'hbLy'+sCountry 
	
	log('opening the data files for HB')
	dfDay = pd.DataFrame()
	for d in daysArr:
		tmpDay = pklmanager.bz2todf(d)
		dfDay = pd.concat([dfDay,tmpDay], sort=True).drop_duplicates().reset_index(drop=True)
	dfYda = pklmanager.bz2todf(folderpkl+yda)
	dfLastWeek = pklmanager.bz2todf(folderpkl+lastWeek)
	dfLastMonth = pklmanager.bz2todf(folderpkl+lastMonth)
	dfLastYear = pklmanager.bz2todf(folderpkl+lastYear)
	
	log('Concatenating all the data files')
	#df = pd.concat([dfDay,dfYda,dfLastWeek,dfLastMonth], sort=True).drop_duplicates().reset_index(drop=True)
	df = pd.concat([dfDay,dfYda,dfLastWeek,dfLastMonth,dfLastYear], sort=True).drop_duplicates().reset_index(drop=True)
	#applying date filter
	log('Applying date filter: today, yesterday, lastweek, lastmonth and lastyear...')
	dfToday = df.loc[ df['dtObj'] >= dtToday ]
	dfYda = df.loc[ ( df['dtObj'] >= dtYda ) & ( df['dtObj'] < dtToday )]
	dfLastWeek = df.loc[ ( df['dtObj'] >= dtLastWeek ) & ( df['dtObj'] < dtYda )]
	dfLastMonth = df.loc[ ( df['dtObj'] >= dtLastMonth ) & ( df['dtObj'] < dtLastWeek )]
	dfLastYear = df.loc[ ( df['dtObj'] >= dtLastYear ) & ( df['dtObj'] < dtLastMonth )]
	
	log('Saving for today file: %s rows and %s columns' % ( len(dfToday.index), dfToday.columns.size ) )
	log('Saving for yesterday file: %s rows and %s columns' % ( len(dfYda.index), dfYda.columns.size ) )
	log('Saving for lastweek file: %s rows and %s columns' % ( len(dfLastWeek.index), dfLastWeek.columns.size ) )
	log('Saving for lastmonth file: %s rows and %s columns' % ( len(dfLastMonth.index), dfLastMonth.columns.size ) )
	log('Saving for lastyear file: %s rows and %s columns' % ( len(dfLastYear.index), dfLastYear.columns.size ) )
	for d in daysArr:
		if os.path.exists(d):
			log('removing '+d)
			os.system('del '+d)
		
	#saving data
	log('Saving the data for HB')
	tmp = pklmanager.dftobz2( dfToday, folderpkl+today )
	tmp = pklmanager.dftobz2( dfYda, folderpkl+yda )
	tmp = pklmanager.dftobz2( dfLastWeek, folderpkl+lastWeek )
	tmp = pklmanager.dftobz2( dfLastMonth, folderpkl+lastMonth )
	tmp = pklmanager.dftobz2( dfLastYear, folderpkl+lastYear )
	
	#cleaning up SC and EWBS data
	log('loading data of SC')
	scFile = 'sc'+sCountry
	dfSC = pklmanager.bz2todf(folderpkl+scFile)
	
	if dfSC.size > 0 :
		dfSC = dfSC.loc[ dfSC['dtObj'] >= dtLastYear ]
	log('Saving dfSC with: %s rows and %s columns' % ( len(dfSC.index), dfSC.columns.size ) )
	tmp = pklmanager.dftobz2( dfSC, folderpkl+ scFile)

	log('loading data of EWBS')	
	ewbsFile = 'ewbs'+sCountry
	dfEWBS = pklmanager.bz2todf(folderpkl+ewbsFile)
	
	if dfEWBS.size > 0:
		dfEWBS = dfEWBS.loc[ dfEWBS['dtObj'] >= dtLastYear ]
	log('Saving dfEWBS with: %s rows and %s columns' % ( len(dfEWBS.index), dfEWBS.columns.size ) )	
	tmp = pklmanager.dftobz2( dfEWBS, folderpkl+ ewbsFile)
	
	
		

if __name__ == "__main__":
#reading the availability
	for country in countries:
		
		now = datetime.datetime.utcnow()
		sCountry = ('').join(country.split(' '))
		dic = pklmanager.getAvailability(country)
		firstTime = False
		
		if not os.path.exists(folderlog+sCountry):
			log(country + " folder does not exist. Continue with the next country..")
			continue
			
		if dic != 1 and dic != -1:
			updateDatetime = datetime.datetime.strptime(dic['updateDatetime'],'%Y-%m-%dT%H:%M:%S.%fZ')
			delta = now - updateDatetime
		else:
			log( sCountry+'.json files does not exist')
			delta =  datetime.timedelta(days=365)
			firstTime = True
		
		
		
		if not firstTime:
			#checking if today's file exists
			filename = folderpkl+'hb'+now.strftime('%Y%j')+ sCountry
			
			if not os.path.exists(filename):
				log('Current date and time does not exists. Running the full data update for country: %s' % country)
				updateAll(country)
		
		strData = ''
		jsonDf = pd.DataFrame()
		
		if delta.days >= 1:
			#updating the amount of days in delta.days
			#reading the log files
			if delta.days <= 365:
				strData, jsonDf = parselog.readLogs(delta.days, folderlog + sCountry)
			else:
				strData, jsonDf = parselog.readLogs(365,folderlog + sCountry )
			
		else:
			#only today's data
			strData, jsonDf = parselog.readLogs(0,folderlog+sCountry)
		
		#parsing both the string info for HB and JSON data from reports.json files
		if len(strData) > 0: 
			dfAMQ, deltaAMQ = parselog.parseHBlog(strData)
		
			log('after parsing:')
			log('dfAMQ has %s rows of data' % len(dfAMQ.index))
			
			dtNow = datetime.datetime.utcnow().replace(tzinfo=pytz.UTC)
			dtToday = datetime.datetime( dtNow.year, dtNow.month, dtNow.day ).replace(tzinfo=pytz.UTC)
			delta = datetime.timedelta(days=1)
			tmp = (dtNow - delta).replace(tzinfo=pytz.UTC)
			dtYda = datetime.datetime( tmp.year, tmp.month, tmp.day ).replace(tzinfo=pytz.UTC)
			delta = datetime.timedelta(days=5)
			dtLastWeek = (dtYda - delta).replace(tzinfo=pytz.UTC)
			delta = datetime.timedelta(days=23)
			dtLastMonth = (dtLastWeek - delta).replace(tzinfo=pytz.UTC)
			delta = datetime.timedelta( days = 335)
			dtLastYear =  (dtLastMonth - delta).replace(tzinfo=pytz.UTC)
			
			#filtering based on date and time
			dfToday = dfAMQ.loc[ dfAMQ['dtObj'] >= dtToday ]
			dfYda = dfAMQ.loc[ ( dfAMQ['dtObj'] >= dtYda ) & ( dfAMQ['dtObj'] < dtToday )]
			dfLastWeek = dfAMQ.loc[ ( dfAMQ['dtObj'] >= dtLastWeek ) & ( dfAMQ['dtObj'] < dtYda ) ]
			dfLastMonth = dfAMQ.loc[ ( dfAMQ['dtObj'] >= dtLastMonth ) & ( dfAMQ['dtObj'] < dtLastWeek ) ]
			dfLastYear = dfAMQ.loc[ ( dfAMQ['dtObj'] >= dtLastYear ) & ( dfAMQ['dtObj'] < dtLastMonth ) ]
			
			log('Today has %s rows and %s columns' % ( len(dfToday.index), dfToday.columns.size ) )
			log('Yesterday has %s rows and %s columns' % ( len(dfYda.index), dfYda.columns.size ) )
			log('Last week has %s rows and %s columns' % ( len(dfLastWeek.index), dfLastWeek.columns.size ) )
			log('Last month has %s rows and %s columns' % ( len(dfLastMonth.index), dfLastMonth.columns.size ) )
			log('Last year has %s rows and %s columns' % ( len(dfLastYear.index), dfLastYear.columns.size ) )
			
			if dfToday.size > 0:
				dfToday = pklmanager.resampleData(dfToday).drop_duplicates()
				tmpFile = 'hb'+dtNow.strftime('%Y%j')+sCountry
				tmp = pklmanager.setData( dfToday, tmpFile )
			
			if dfYda.size > 0:
				dfYda = pklmanager.resampleData(dfYda).drop_duplicates()
				tmpFile = 'hbYda'+sCountry
				tmp = pklmanager.setData( dfYda, tmpFile )
			
			if dfLastWeek.size > 0:
				dfLastWeek = pklmanager.resampleData(dfLastWeek).drop_duplicates()
				tmpFile = 'hbLw'+sCountry
				tmp = pklmanager.setData( dfLastWeek, tmpFile )
			
			if dfLastMonth.size > 0:
				dfLastMonth = pklmanager.resampleData(dfLastMonth).drop_duplicates()
				tmpFile = 'hbLm'+sCountry
				tmp = pklmanager.setData( dfLastMonth, tmpFile )
			
			if dfLastYear.size > 0:
				dfLastYear = pklmanager.resampleData(dfLastYear).drop_duplicates()
				tmpFile = 'hbLy'+sCountry
				tmp = pklmanager.setData( dfLastYear, tmpFile )
		else:
			dfAMQ =  pd.DataFrame()
		dfSCfull, dfEWBSfull = parselog.parseJSON(jsonDf)
		log('after parsing:')
		log('dfSC has %s rows of data' % len(dfSCfull[1].index))
		log('dfEWBS has %s rows of data' % len(dfEWBSfull[1].index))
		
		dfSC = dfSCfull[1]
		dfEWBS = dfEWBSfull[1]	
		
		#saving the JSON info
		tmpFile = 'sc'+('').join( country.split(' ') )	
		tmp = pklmanager.setData( dfSC, tmpFile )
		
		tmpFile = 'ewbs'+('').join( country.split(' ') )
		tmp = pklmanager.setData( dfEWBS, tmpFile )
		
		log('dfSC has %s rows and %s columns' % ( len( dfSC.index ), dfSC.columns.size ) )
		log('dfEWBS has %s rows and %s columns' % ( len( dfSC.index ), dfSC.columns.size ) )
		
		#setting the new date and time for the updateDatetime in the json availability file
		if dfAMQ.size>0:
			maxDt = datetime.datetime.utcnow()
			tmp =pklmanager.getMinMaxFromDf(dfAMQ)
			
			if tmp != -1:
				maxDt = tmp[1]
			
			pklmanager.setAvailability(maxDt,country)
		
