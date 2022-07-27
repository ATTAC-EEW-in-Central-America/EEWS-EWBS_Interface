'''	This class deals with reading, storing, and updating Pickle files that contain delta time values.
	All the information is collected from log files
'''

import json, os, sys, platform
import datetime, pytz
import bz2, pickle
import pandas as pd
import logging

logging.basicConfig(level=logging.DEBUG)
logIdentifier = 'PKLMANAGER'

#Windows or Linux
OS = platform.uname()[0]
print(OS)
# This is one example of the filenames are for Costa Rica:
#
# hb2021014CostaRica for today's hb (in UTC)
# hbYdaCostaRica for yesterday's hb
# hbLastWeekCostaRica for the last week hb (no today's nor yesterday's hb)
# hbCostaRica for the last month hb (no last week, nor the prior hb)
# scCostaRica for the last 30 days 
# ewbsCostaRica for the least 30 days


class PickleDataManage:
	
	def __init__(self, mainPickleFolder='pickledata\\'):
		if not OS ==  'Windows':
			mainPickleFolder = 'pickledata/'
	
		self.mainPickleFolder = mainPickleFolder
		
	
	def getAvailability( self, countryName ):
		#read a json file to find out the 
		#data availability
		#returns an object with the date and time of the last update
		sCountry = ('').join(countryName.split(' '))
		f = self.mainPickleFolder+sCountry+'.json'
		self.log('Last Date and Time of data availability for %s ' % countryName)
		
		if os.path.exists(f):
			try:
				f = open(f,'r')
				data = json.load(f)
			except Exception as e:
				self.log('ERROR loading the json file')
				print(e)
				return -1
			for dic in data:
				if dic['country'] == countryName:
					return dic
			return 1 #all went fine but there is no such country in the JSON file :(
		else:
			self.log('ERROR in json file. %s does not exist' % f )
			return -1


	
	def setAvailability(self, dtLastUpdate, countryName):
		#this method will write the information
		#about data availability in a JSON file 
		
		self.log( 'setting availability for %s' % countryName)
		
		sCountry = ('').join(countryName.split(' '))
		f = self.mainPickleFolder+sCountry+'.json'
		
		if os.path.exists(f):
			try:
				fData = open(f,'r')
				data = json.load(fData)
				fData.close()
			except Exception as e:
				self.log( 'error loading the json file' )
				self.log( e )
				return -1
			
			tmp = False
			
			for dic in data:
				if dic['country'] == countryName:
					dic['updateDatetime'] = dtLastUpdate.strftime('%Y-%m-%dT%H:%M:%S.%fZ')
					tmp=True
			if tmp == False:
				self.log(  'Adding a new object into the JSON file of %s'% countryName )
				tmpObj = {
				'country': countryName,
				'updateDatetime': dtLastUpdate.strftime('%Y-%m-%dT%H:%M:%S.%fZ')
				}
				data.append(tmpObj)

			fData = open(self.mainPickleFolder+sCountry+'.json', "w")
			json.dump(data, fData)
			fData.close()
			return
		
		else:
			self.log( 'error in json file. %s does not exist' % f )
			self.log( 'creating a new one...' )
			tmpFile = open(f,'w')
			tmpData = []
			tmpObj = {
				'country': countryName,
				'updateDatetime': dtLastUpdate.strftime('%Y-%m-%dT%H:%M:%S.%fZ')
			}
			
			tmpData.append(tmpObj)
			
			json.dump(tmpData, tmpFile)
			
			tmpFile.close()
			self.log( 'succesfully created a new JSON file' )
			return
	
	
	def setData( self, df, filename ):
		# Method to save data in compressed bz2 
		# input values are: dataframe and a filename
		# if the file exists, then this method will merge
		# avoiding repeated rows. Otherwise, the file will be created 
		
		self.log( 'saving data of ~%s bytes in a compressed file' % sys.getsizeof(df) )
		tmp = self.mainPickleFolder + filename
		if os.path.exists(tmp):
			self.log( 'This file: %s exists. It will be updated with the new data' % tmp )
			
			dfOld = self.bz2todf(tmp)
			
			if dfOld.size == 0 :
				
				self.log( 'The file does not contain data. It is empty. Saving the dataframe now' )
				self.dftobz2(df, tmp)
				return
			
			else:
				
				self.log( 'merging the two dataframes...' )

				try:
					df = pd.concat([dfOld,df], sort=True).drop_duplicates().reset_index(drop=True)
					self.log( '...merged' )
					self.dftobz2(df,tmp)
				except Exception as e:
					self.log( 'ERROR while merging the old and new dataframes' )
					return -1
		
		else:
			self.log( 'This file: %s does not exist. Saving a new one' % tmp )
			self.dftobz2(df,tmp)
		
		return 0	
				
				
		#saving in gz2file
		try:
			
			self.setAvailability( dfFrom, dtEnd, countrName, dtUpdateTime )
		except Exception as e:
			self.log( 'error while setting the data into a bz file or other further step. See the error below:' )
			self.log( repr(e) )
			return -1
		
		return 0
			
	def dftobz2(self, df, filename):
		
		self.log( 'dataframe to bz2 file' )
		self.log( 'storing the dataframe in a bz2 file named: %s' % filename)
		
		try:
			bzfile = bz2.BZ2File(filename, 'wb')
			pickle.dump(df,bzfile)
			bzfile.close()
		except Exception as e:
			self.log( 'something went wrong while saving in a bz2 file. See below for more details:\n' )
			self.log( repr( e ) )
			print('\n')
			return -1
		
		self.log( 'saved successfully' )
		return 0
			
	def bz2todf(self, f, encoding="latin1"):
		self.log( 'opening bz2 file: %s' % f )
		try:
			tmp = bz2.BZ2File(f,'rb')
			if sys.version_info.major > 2:
				dfData = pickle.load(tmp, encoding=encoding)
			else:
				dfData = pickle.load(tmp)
			return dfData
		except Exception as e:
			self.log( 'error loading the file: %s' % f )
			self.log( repr(e) )
			df = pd.DataFrame()
			df['dtObj'] = ''
			return df
		
	
	def removeData( dtReference, filename ):
		#method that removes data based on start and end datetime obj and country name.
		#The removed data is on a pickle file and it won't be today's data
		#dtFrom and dtEnd are to exclude data
		self.log( 'Opening compressed file...' )
		df = self.bz2todf(filename)
		self.log( 'selecting date more than the reference datetime: %s' % dtReference )
		
		df = df.loc[ df['dtObj'] > dtReference.strftime('%Y-%m-%dT%H:%M:%S.%fZ')]
		
		log( 'saving a new file with the information' )
		self.dftobz2(df,filename)
		
		return
	
	
	def getData( self, dtFrom, dtEnd, countryName ):
		#method to read bz2 file and provide dataframe
		#from dtFrom to dtEnd for the countryName
		#returns dataframes for deltaAMQ, deltaSC and deltaEWBS
		#for histograms and dfAMQ, dfSC and dfEWBS for timelines in dataframes, too
		
		now = datetime.datetime.utcnow()
		
		today = now.strftime('%Y%m%d')
		endDate = dtEnd.strftime('%Y%m%d')
		startDate = dtFrom.strftime('%Y%m%d')
		
		self.log( 'reading the data for country %s from %s to %s ' %  (countryName, dtFrom, dtEnd) )
		
		daysAgo = ( now.date() - dtFrom.date() ).days
		daysAgoEnd = (  now.date() - dtEnd.date() ).days
		
		if  daysAgo == 0 :
			self.log( 'opening today\'s file' )
			fileName = self.mainPickleFolder+'hb'+now.strftime("%Y%j")+('').join(countryName.split(' '))
			df = self.bz2todf(fileName)		
			
		elif daysAgo == 1 :
			self.log( 'opening today and yesterday file' )
			filename = self.mainPickleFolder+'hb'+now.strftime("%Y%j")+('').join(countryName.split(' ') )
			tmp1 = self.bz2todf(filename)
 
			filename = self.mainPickleFolder+'hbYda'+('').join(countryName.split(' ') )
			tmp2 = self.bz2todf(filename)
			
			df = pd.concat( [ tmp1, tmp2 ], sort=True ).drop_duplicates().reset_index(drop=True)
			
			tmp1 = tmp2 = None
		
		elif daysAgo >= 2 and daysAgo <= 6:	
			self.log( 'opening data from today up to 6 days ago' )
			filename = self.mainPickleFolder+'hb'+now.strftime("%Y%j")+('').join(countryName.split(' ') )
			tmp1 = self.bz2todf(filename)
 
			filename = self.mainPickleFolder+'hbYda'+('').join(countryName.split(' ') )
			tmp2 = self.bz2todf(filename)
			
			filename = self.mainPickleFolder+'hbLw'+('').join(countryName.split(' ') )
			tmp3 = self.bz2todf(filename)
			
			df = pd.concat( [ tmp1, tmp2, tmp3 ], sort=True ).drop_duplicates().reset_index(drop=True)
			
			df = self.resampleData(df, '120s')
			
			tmp1 = tmp2 = tmp3 = None
		
		elif daysAgo >= 7 and daysAgoEnd >= 2 and daysAgo <= 30 :
			self.log( 'opening data from lastweek and last month...' )
			filename = self.mainPickleFolder+'hbLw'+('').join(countryName.split(' ') )
			tmp1 = self.bz2todf(filename)
			
			filename = self.mainPickleFolder+'hbLm'+('').join(countryName.split(' ') )
			tmp2 = self.bz2todf(filename)
			
			df = pd.concat( [ tmp1, tmp2 ], sort=True ).drop_duplicates().reset_index(drop=True)
			
			df = self.resampleData(df, '180s')
			
			tmp1 = tmp2 = None
			
		else:
			self.log( 'Open data for the last year ...' )

			filename = self.mainPickleFolder+'hb'+now.strftime("%Y%j")+('').join(countryName.split(' ') )
			tmp1 = self.bz2todf(filename)
 
			filename = self.mainPickleFolder+'hbYda'+('').join(countryName.split(' ') )
			tmp2 = self.bz2todf(filename)
			
			filename = self.mainPickleFolder+'hbLw'+('').join(countryName.split(' ') )
			tmp3 = self.bz2todf(filename)
			
			filename = self.mainPickleFolder+'hbLm'+('').join(countryName.split(' ') )
			tmp4 = self.bz2todf(filename)
			
			filename = self.mainPickleFolder+'hbLy'+('').join(countryName.split(' ') )
			tmp5 = self.bz2todf(filename)
			
			df = pd.concat( [ tmp1, tmp2, tmp3, tmp4, tmp5 ], sort=True ).drop_duplicates().reset_index(drop=True)
			
			df = self.resampleData(df, '300s')
			
			tmp1 = tmp2 = tmp3 = tmp4 = tmp5 = None
		
		self.log('data returned contains %s of rows and %s of columns' % ( len(df.index), df.columns.size ) )
			
		self.log( 'applying filter based on datetime start and end' )
		dfHB = pd.DataFrame()
		if df.size > 0:
			self.log('Applying the date and time filter....')
			dfHB = df.loc[ ( df['dtObj'] >= dtFrom ) & ( df['dtObj'] <= dtEnd ) ]
		else:
			dfHB['dtObj'] = ''
			dfHB['deltaAMQ'] = ''
		
		self.log('After Applying date and time filter the returned data contains %s rows and %s columns' % ( len(dfHB.index), dfHB.columns.size ) )
		
		dfAMQ = pd.DataFrame()
		
		dfAMQ = dfHB[['dtObj','deltaAMQ']]
			
		self.log('Resampled data contains %s rows and %s columns' % ( len(dfAMQ.index), dfAMQ.columns.size ) )	
			
		#setting the values of deltaAMQ as the simple column of the HB dataframe
		self.log( 'setting delta AMQ column for histogram' )
		
		if dfHB.size > 0:
			deltaAMQ = pd.DataFrame(dfHB['deltaAMQ'])
			deltaAMQ.astype(float)
			self.log('data for deltaAMQ histogram has a size of %s' %  deltaAMQ.size )
		
		else:
			deltaAMQ = pd.DataFrame()
			deltaAMQ['deltaAMQ'] = ''
			self.log( 'no data for deltaAMQ' )
		
		########## JSON ################
		dfSC = pd.DataFrame()
		dfEWBS= pd.DataFrame()
		
		#delta SC and delta EWBS are in one file each since the data are a relative small in size
		
		self.log( 'Loading Delta SC data...')
		
		filename = self.mainPickleFolder+'sc'+('').join(countryName.split(' ') )
		dfSCf = self.bz2todf(filename) # dataframe only contains dtObj and deltaSC values
		
		self.log('data returned contains %s of rows and %s of columns' % ( len(dfSCf.index), dfSCf.columns.size ) )
		
		self.log( 'applying datetime filter to delta SC' )
		
		if dfSCf.size > 1:
			dfSC = dfSCf.loc[ ( dfSCf['dtObj'] >= dtFrom ) & ( dfSCf['dtObj'] <= dtEnd ) ]
		else:
			dfSC = pd.DataFrame()
			dfSC['dtObj'] = ''
			dfSC['deltaSC'] = ''
		
		self.log('After Applying date and time filter the dataframe contains %s rows and %s columns' % ( len(dfSC.index), dfSC.columns.size ) )	
		self.log( 'setting delta SC column for histogram' )
		
		deltaSC = pd.DataFrame(dfSC['deltaSC'])
		
		deltaSC.columns = ['deltaSC']
		deltaSC.astype(float)
		self.log('deltaSC for histogram contains a size of %s' % deltaSC.size )
		
		
		self.log( 'Loading Delta EWBS data...' )
		
		filename = self.mainPickleFolder+'ewbs'+('').join(countryName.split(' ') )
		dfEWBSf = self.bz2todf(filename) # dataframe only contains dtObj and deltaEWBS values
		self.log('data returned contains %s of rows and %s of columns' % ( len(dfEWBSf.index), dfEWBSf.columns.size ) )
		
		self.log( 'applying date and time filter to delta EWBS...' )
		
		dfEWBS = dfEWBSf.loc[ dfEWBSf['dtObj'].between( dtFrom, dtEnd, inclusive=True )]
		self.log('After Applying date and time filter the dataframe contains %s rows and %s columns' % ( len(dfEWBS.index), dfEWBS.columns.size ) )	
		
		self.log( 'setting deltaEWBS column for histogram' )
		
		deltaEWBS = pd.DataFrame(dfEWBS['deltaEWBS'])
		deltaEWBS.columns = ['deltaEWBS']
		deltaEWBS.astype(float)
		self.log('deltaEWBS for histogram contains a size of %s' % deltaEWBS.size )
		
		#it will returning only resampled data or not resampled data if the amount of lines for AMQ is less than 1440 samples
		
		self.log('dfSC: %s, dfAMQ: %s, dfEWBS: %s, deltaSC: %s, deltaAMQ: %s, deltaEWBS: %s' % (dfSC.size, dfAMQ.size, dfEWBS.size, deltaSC.size, deltaAMQ.size, deltaEWBS.size) )
		dfSC = dfSC.drop_duplicates().dropna().sort_values(by='dtObj')
		dfAMQ = dfAMQ.drop_duplicates().dropna().sort_values(by='dtObj')
		dfEWBS = dfEWBS.dropna().drop_duplicates().sort_values(by='dtObj')
		deltaSC = deltaSC.dropna()
		deltaAMQ = deltaAMQ.dropna()
		deltaEWBS = deltaEWBS.dropna() 
		
		retDic = {
			'dfSC': dfSC,
			'dfAMQ': dfAMQ,
			'dfEWBS': dfEWBS,
			'deltaSC': deltaSC,
			'deltaAMQ': deltaAMQ,
			'deltaEWBS': deltaEWBS
		}
		
		return retDic
		
	
	def log(self, msg ):
		now = datetime.datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S(UTC)')
		logging.debug(now+' - '+logIdentifier+": "+msg)
		
	def resampleData( self, df, resamplingTime = '60s' ):
		dfnew = pd.DataFrame()
		dfnew['dtObj'] = ''
		dfnew['deltaAMQ'] = ''
		
		#Few data cannot be resampled
		if len(df.index) < 72: #6 minutes
			self.log( 'Data is less than 6 minutes. Resampling not applied' )
			dfnew = df[['dtObj','deltaAMQ']]
		
		elif len(df.index) >= 72:	
			self.log( 'applying resampling each 60 seconds' )
			
			dfnew = df[['dtObj','deltaAMQ']]
			dfnew = dfnew.set_index(['dtObj'])
			dfnew['deltaAMQ'] = dfnew['deltaAMQ'].apply(pd.to_numeric, errors='coerce')
			dfnew = dfnew.resample(resamplingTime).mean()
			dfnew = dfnew.reset_index()	
		else:
			self.log( 'dataframe for AMQ is empty' )
		
		return dfnew
	
	def getMinMaxFromDf(self, df):
		self.log('obtaining the earliest date and time from \'dtObj\' column')
		
		if 'dtObj' in df.columns:
			col = df['dtObj']
			minVal = col.min()
			maxVal = col.max()
			return [minVal, maxVal]
		else:
			self.log('the dtObj column does not exist')
			return -1
		
