#Utilitary script

import datetime, time
from dateutil.tz import tzutc, tzlocal
from Tkinter import *
#import tkinter.messagebox as messagebox
import tkMessageBox as messagebox

def popupmsg(title, body):
	try:
		root=Tk()
		messagebox.showinfo(title,body)
		root.mainloop()
	except:
		return


def getNowUTCsecs():
	val = ( datetime.datetime.utcnow() - datetime.datetime(1970, 1, 1) ).total_seconds()
	return float(val)
	
	
def getNowLOCALsecs():

	val = ( datetime.datetime.now() - datetime.datetime(1970, 1, 1) ).total_seconds()
	return float(val)
	
def getNowUTCstr():
	val = datetime.datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S')
	return val
	
def getNowUTCstrms():
	val = datetime.datetime.utcnow().strftime('%Y-%m-%dT%H:%M:%S.%f')
	return val[:-3]+'Z'
	
	
def getNowLOCALstr():
	val = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
	return val

def timestamp2datetime(seconds):
	#input must be a float
	dt = datetime.datetime.fromtimestamp(seconds).strftime('%Y-%m-%d %H:%M:%S')
	return dt

def UTCtimestamp2UTCdatetime(seconds):
	#input can be float or int
	deltaSecs = time.timezone
	seconds = seconds + deltaSecs
	dt = datetime.datetime.fromtimestamp(seconds).strftime('%Y-%m-%d %H:%M:%S.%f')
	return dt

def datetime2timestamp(strdt):
	#The input has to be in the next format:
	# Year-Month-DayThour:minute:second.floatZ
	# for example "2021-06-21T14:36:52.2545Z"
	try:
		val = datetime.datetime.strptime(strdt,'%Y-%m-%dT%H:%M:%S.%fZ')
		return float((val - datetime.datetime(1970, 1, 1)).total_seconds())
	except Exception as e:
		print e
		return 0

def UTCdtstr2LOCALdtstr(strdtUTC):
	#this will convert the UTC date and time string as an input format %Y-%m-%dT%H:%M:%S.%fZ
	#to local date and time string as an output format %Y-%m-%d %H:%M:%S
	utc = datetime.datetime.strptime(strdt,'%Y-%m-%dT%H:%M:%S.%fZ')
	utc = utc.replace(tzinfo = tzutc() )
	local = utc.astimezone( tzlocal() )
	return local.strftime("%Y-%m-%d %H:%M:%S") 

def UTCdatetime2LocalTime(strdtUTC):
	utc = datetime.datetime.strptime(strdt,'%Y-%m-%dT%H:%M:%S.%fZ')
	utc = utc.replace(tzinfo = tzutc() )
	local = utc.astimezone( tzlocal() )
	return local.strftime("%H:%M:%S") 
		
def UTCdatetime2LocalDate(strdtUTC):
	utc = datetime.datetime.strptime(strdt,'%Y-%m-%dT%H:%M:%S.%fZ')
	utc = utc.replace(tzinfo = tzutc() )
	local = utc.astimezone( tzlocal() )
	return local.strftime("%T-%m-%d") 
	
