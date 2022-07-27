import util
import logging
import platform
import datetime
import util
import sys, os

#Logging
logger = logging.getLogger()
logger.setLevel(logging.DEBUG)
stdout_handler = logging.StreamHandler(sys.stdout)
logger.addHandler(stdout_handler)

#log level
info = 'info'
warning = 'warning'
error = 'error'

OS = platform.uname()[0]
    
class Log:
    #logging messages to be written into a files
    #and if enable, in the terminal
    
    def __init__(self, rootFolder):
        #generally country's name
        
        self.rootFolder = rootFolder
        self.logFolder = "log"
        if OS == 'Windows':
            if not os.path.exists('log'):
                os.system('mkdir log')
            #hardcoded
            self.logFolder = 'log'
        else:
            if not os.path.exists('log'):
                os.system('mkdir log')
            #hardcoded
            self.logFolder = 'log'
    
    #getting the folder structure string line
    
    def write(self, msg, typemsg, level, term = False ):
        
        msg = util.getNowUTCstrms() + "(UTC): "+msg
        tmp = self.outfile()
        
        if typemsg == 'hb':
            #adding the handler
            logger_file_handler = logging.FileHandler(tmp+"hb.log")
        elif typemsg == 'evt':
            logger_file_handler = logging.FileHandler(tmp+"evts.log")
        elif typemsg == 'sys':
            logger_file_handler = logging.FileHandler(tmp+"sys.log")
        else:
            logger_file_handler = None
    
        if logger_file_handler != None:
            if term:
                logger.addHandler(logger_file_handler)
                logger.addHandler(stdout_handler)
            else:
                logger.addHandler(logger_file_handler)
                logger.removeHandler(stdout_handler)
    
            if level == 'warning':
                logger.warning( msg )
            elif level == 'info':
                logger.info( msg )
            elif level == 'error':
                logger.error( msg )
            else:
                logger.info( msg )
    
            logger.removeHandler(logger_file_handler)
    
        else:
            #message to stdout only
            logger.addHandler(stdout_handler)
    
            if level == 'warning':
                logger.warning( msg )
            elif level == 'info':
                logger.info( msg )
            elif level == 'error':
                logger.error( msg )
            else:
                logger.info( msg )
    
    def outfile( self ):
        #this method is checking if the folder structure based on date
        #is set or it is needed to be created
        #checking the year
    
        year = "{:%Y}".format( datetime.datetime.utcnow() )
        month = "{:%m}".format( datetime.datetime.utcnow() )
        day = "{:%d}".format( datetime.datetime.utcnow() )
        strRootFolder = ('').join(self.rootFolder.split(' '))
        
        if OS == 'Windows':
        
            tmp = self.logFolder+"\\"+strRootFolder+'\\'+year+"\\"+month+"\\"+day+"\\"
            if not os.path.exists(self.logFolder+"\\"+strRootFolder+'\\'+year):
                cmd = "mkdir "+self.logFolder+"\\"+strRootFolder+'\\'+year
                os.system(cmd)
    
            if not os.path.exists(self.logFolder+"\\"+strRootFolder+'\\'+year+"\\"+month):
                cmd = "mkdir "+ self.logFolder+"\\"+strRootFolder+'\\'+year+"\\"+month
                os.system(cmd)
    
            if not os.path.exists(self.logFolder+"\\"+strRootFolder+'\\'+year+"\\"+month+"\\"+day):
                cmd = "mkdir "+self.logFolder+"\\"+strRootFolder+'\\'+year+"\\"+month+"\\"+day
                os.system(cmd)
        
        else:
        
            tmp = self.logFolder+"/"+strRootFolder+'/'+year+"/"+month+"/"+day+"/"
            if not os.path.exists(self.logFolder+"/"+strRootFolder+'/'+year):
                cmd = "mkdir "+self.logFolder+"/"+strRootFolder+'/'+year
                os.system(cmd)
    
            if not os.path.exists(self.logFolder+"/"+strRootFolder+'/'+year+"/"+month):
                cmd = "mkdir "+self.logFolder+"/"+strRootFolder+'/'+year+"/"+month
                os.system(cmd)
    
            if not os.path.exists(self.logFolder+"/"+strRootFolder+'/'+year+"/"+month+"/"+day):
                cmd = "mkdir "+self.logFolder+"/"+strRootFolder+'/'+year+"/"+month+"/"+day
                os.system(cmd)
    
        return tmp
