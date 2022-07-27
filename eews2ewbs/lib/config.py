import sys, os

version = sys.version_info.major

class Configuration:
   
    def __init__(self):
        
        #User provides input information from a file
        if sys.version_info.major == 2:
            print "User configuration file 'stompy2ewbs.cfg'"
        else:
            print("User configuration file 'stompy2ewbs.cfg'")
        
        self.host = None
        self.port = None
        self.user = None
        self.password = None
        self.topic = None
        self.typeConnection = None
        self.ewbsconsolehost = None
        self.msgtime = 20
        self.hblog = False
        self.evtlog = True
        self.jsonlog = False
        self.loghbstdout =False
        self.maxtime = 30
        self.staticmsg = False
        self.capsmsg = True
        self.dryrun = False
        self.language = 'es-US'
        self.countryName = ''
        self.alertmsg = ''
        self.magDiff = 1.0
        self.emailReport = False
        self.emailSender = ''
        self.emailUser = ''
        self.emailPassword = ''
        self.smtp = ''
        self.smtpPort = 587

        import ConfigParser
        
        config = ConfigParser.RawConfigParser()
        try:
            self.configFilePath = r'stompy2ewbs.cfg' #hardcoded and it must be in the same folder as the stompy2ewbs.py script
            config.read(self.configFilePath)
        except Exception as e:
            if sys.version_info.major == 2:
                print "Not possible to open the stompy2ewbs.cfg"
                print "exiting...."
            else:
                print("Not possible to open the stompy2ewbs.cfg")
                print ("exiting....")
            sys.exit(1)
            
        try:
            self.host = config.get('AMQ-CONNECTION', 'host')
            self.port = config.get('AMQ-CONNECTION', 'port')
            self.user = config.get('AMQ-CONNECTION', 'user')
            self.password = config.get('AMQ-CONNECTION', 'password')
            self.topic = config.get('AMQ-CONNECTION', 'topic')
            self.typeConnection = config.get('AMQ-CONNECTION', 'typeConnection')
            self.ewbsconsolehost = config.get('EWBS-CONSOLE', 'ewbsconsolehost')
            self.msgtime = config.getint('EWBS-CONSOLE', 'msgtime')
            self.hblog = config.getboolean('LOGGING', 'hblog')
            self.evtlog = config.getboolean('LOGGING', 'evtlog')
            self.jsonlog = config.getboolean('LOGGING', 'jsonlog')
            self.loghbstdout = config.getboolean('LOGGING', 'loghbstdout')
            self.maxtime = config.getint('EQ-FILTER-REPORT','maxtime')
            self.staticmsg = config.getboolean('ALERT-MESSAGE','staticmsg')
            self.capsmsg = config.getboolean('ALERT-MESSAGE', 'capsmsg')
            self.dryrun = config.getboolean('TESTING','dryrun')
            self.language = config.get('ALERT-MESSAGE','language')
            if self.staticmsg:
                self.alertmsg = config.get('ALERT-MESSAGE','msg')
            self.countryName = config.get('LOGGING','countryName')
            
            self.magDiff = config.getfloat('ALERT-MESSAGE', 'magDiff')
            self.emailReport = config.getboolean('EMAIL-REPORT','emailReport')
            if self.emailReport:
                self.emailSender =  config.get('EMAIL-REPORT','emailSender')
                self.emailUser =  config.get('EMAIL-REPORT','emailUser')
                self.emailPassword =  config.get('EMAIL-REPORT','emailPassword')
                self.smtp =  config.get('EMAIL-REPORT','smtp')
                self.smtpPort =  config.getint('EMAIL-REPORT','smtpPort')
        except Exception as e:
            if sys.version_info.major == 2:
                print "An error has ocurred parsing the configuration file:%s" % e
            else:
                print("An error has ocurred parsing the configuration file:%s" % e)
            
            sys.exit(1)  
