'''Handling and reporting errors for eews2ewbs interface'''
# -*- encoding: utf-8 -*-
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText  
from string import Template 
import util
from Log import Log
# set up the SMTP server

class ErrorReport:
    
    def __init__(self, cfg ):
        self.cfg = cfg
        self.emailSender = cfg.emailSender
        self.user = cfg.emailUser
        self.password = cfg.emailPassword
        self.smtp = cfg.smtp
        self.smtpPort = cfg.smtpPort
        #self.contactFilename = contactFilename
        self.log = Log(cfg.countryName)
        self.info = 'info'
        self.warning = 'warning'
        self.error = 'error'
        #attribute to control when the error was reported
        #unix timestamp
        self.lastHbErrorReport = 0.0 
        self.lastRedTermErrorReport = 0.0 
        self.lastTransErrorReport = 0.0
    def connectSmtp(self):
        s = None
        try:
            s = smtplib.SMTP(host=self.smtp, port=self.smtpPort,
                                 timeout=5)
            #s.connect()
            #s.ehlo()
        except Exception as e:
            self.log.write("It cannot connnect to the smtp server %s " % self.smtp,'sys', "error" , False)
            return
        try:
            s.starttls()
            s.login(self.user, self.password)
        except Exception as e:
            self.log.write('Email could not be sent: %s' % e, 'sys',"error", False)
        return s
    def sendEmail(self, msgType, msgStr, lastingTime = 0):
        '''
        method to send email based on msgType (hb error == 1, red terminal error == 2 or tranmission error == 3)
        lastingTime is only for heartbeat.
        it uses template files to send the email
        '''
        try:
            emails = self.get_contacts()
        except Exception as e:
            self.log.write("Not possible to read contacts. Not sending any email.",'sys', "info", False)
            return
        #template
        if msgType == 1:
            message_template = self.read_template('heartbeatErrorTemplate.txt')
        elif msgType == 2:
            message_template = self.read_template('redTerminalErrorTemplate.txt')
        elif msgType == 3:
            message_template = self.read_template('transmissionErrorTemplate.txt')
        elif msgType == 4:
            message_template = self.read_template('unknownErrorTemplate.txt')
        timeStr = ''
        if msgType == 1:
                
                days = lastingTime/86400
                
                resDays = lastingTime%86400
                
                hours = resDays/3600
                
                resHours = resDays % 3600
                
                minutes = resHours/60
                
                seconds = resHours%60
                
                timeStr = "%s dias, " % days if days>0 else ""
                timeStr += "%s horas, " % hours if hours > 0 else ""
                timeStr += "%s minutos, " % minutes if minutes > 0 else ""
                timeStr += "%s segundos" % seconds if seconds > 0 else ""
                if timeStr[-2:] == ", ":
					timeStr = timeStr[:-2]
        s = self.connectSmtp()
        if not s:
            return
        
        msg = MIMEMultipart()       # create a message
        
        # setup the parameters of the message
        msg['From']=self.emailSender
        msg['To']=','.join(emails)
        country = self.cfg.countryName
        dtlocal = util.getNowLOCALstr()
        dtutc = util.getNowUTCstr()
        
        if msgType == 1 :
            msg['Subject']= "[EWBS] Error de Heartbeat en %s" % country
            message = message_template.substitute( TIMESTR= timeStr,COUNTRY = country, DATETIME = dtlocal, DATETIMEUTC = dtutc)
        elif msgType == 2:
            msg['Subject']= "[EWBS] Error Con Terminal Roja en %s " % country
            message = message_template.substitute( COUNTRY = country, DATETIME = dtlocal, DATETIMEUTC = dtutc)
        elif msgType == 3:
            msg['Subject']= "[EBWS] Error de transmision en %s" % country
            message = message_template.substitute( COUNTRY = country, DATETIME = dtlocal, DATETIMEUTC = dtutc)
        elif msgType == 4: #unknown type and only sending the 
            msg['Subject']= "[EBWS] Error Desconocido en %s" % country
            message = message_template.substitute(ERRORMSG = msgStr, COUNTRY = country, DATETIME = dtlocal, DATETIMEUTC = dtutc )
        
        
        # add in the message body
        msg.attach(MIMEText(message, 'plain', 'utf-8'))
        
        try:
            s.sendmail(self.emailSender, emails, msg.as_string())
        except Exception as e:
            self.log.write("Error: %s" % e,'sys', "info", False)
        del msg
        try:
            s.quit()  
        except Exception as e:
            self.log.write("Error quiting smtp conexion: %s" % e,'sys', "info", False)
            
    def get_contacts( self ):
        filename = "contacts.txt";
        #names = []
        emails = ''
        f = open(filename, mode='r')
        tmp = f.read()
        emails = tmp.split('\n')
        return emails
    
    def read_template( self, filename ):
        with open(filename, 'r') as template_file:
            template_file_content = template_file.read()
        return Template(template_file_content)
