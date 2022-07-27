from Log import Log
import subprocess
from ErrorReport import ErrorReport 
class EWBSConsoleConnection:

    def __init__(self, cfg):

        self.ewbsconsolehost = cfg.ewbsconsolehost
        
        #logging levels
        self.cfg = cfg
        self.log = Log(cfg.countryName)
        self.info = 'info'
        self.warning = 'warning'
        self.error = 'error'
        self.er = ErrorReport(self.cfg)
        
    def BroadcastMsg(self, msg = None, msgalivetime = 20):
        self.log.write("Preparing to broadcast a message through EWBSConsole",'evt',self.info,True)
        cmd = 'ewbsconsole send -i ' + self.ewbsconsolehost + ' -a 064 -m "'+ msg + '" -t ' + str(msgalivetime)

        try:
            self.log.write("Starting subprocess with message to be broadcasted....",'evt',self.info,True)
            output = subprocess.Popen(cmd,stdout = subprocess.PIPE, stderr = subprocess.STDOUT)
            self.log.write("End of the execution of the subprocess. Checking results",'evt',self.info,True)
        except Exception as e:
            self.log.write("The red terminal could not be running. Please check the error message:",'evt',self.error,True)
            self.log.write(repr(e),'evt',self.error,True)
            self.log.write(repr(e),'sys',self.error,True)
            if self.cfg.emailReport:
                self.er.sendEmail(3,'',0)
            return [-1]

        if output.stderr != None:
            self.log.write("The message was not broadcasted. There was an error:",'evt',self.error,True)
            self.log.write(output.stderr,'evt',self.error,True)
            if self.cfg.emailReport:
                self.er.sendEmail(3,'',0)
            return [-1]

        self.log.write("Reading response from the server",'sys',self.info,False)
        r = output.stdout.read()
        r = r.lower()

        self.log.write("response was read. Closing the open process",'sys',self.info, False)
        output.stdout.close()

        if r.find("start") > 0 and r.find("stop") > 0:
            self.log.write("The message was broadcasted successfully", 'evt',self.info,True)
            retMsg = {}
            lineNum = 0
            for line in r.split('\n'):
                try:
                    tmp = line.split(': ')[0].upper()
                except:
                    tmp = 0

                if lineNum == 0:
                    retMsg['startConsole'] = tmp
                    self.log.write('EWBSCONSOLE: Start console time was: %s' % tmp,'evt',self.info,False)

                if line.find('start') > 0:
                    retMsg['startTransmission'] = tmp
                    self.log.write('EWSCONSOLE: Start transmission time was: %s' % tmp,'evt',self.info,False)

                if line.find('stop') > 0:
                    retMsg['stopTransmission'] = tmp
                    self.log.write('EWBSCONSOLE: Stop transmission time was: %s' % tmp,'evt',self.info,False)

                if lineNum == 3:
                    retMsg['stopConsole'] = tmp
                    self.log.write('EWBSCONSOLE: Stop console time was: %s' % tmp,'evt',self.info,False)

                lineNum += 1
            
            if 'startTransmission' not in retMsg:
                retMsg['startTransmission'] = retMsg['startConsole']
                self.log.write('EWBSCONSOLE: there was no start transmission time. Setting the value of start console instead','evt',self.info, False)
            if 'stopTransmission' not in retMsg:
                retMsg['stopTransmission'] = retMsg['stopConsole']
                self.log.write('EWBSCONSOLE: there was no stop transmission time. Setting the value of stop console instead','evt',self.info, False)
            
            return [0, retMsg]

        elif r.find("exception") > 0:
            self.log.write("The messages WAS NOT BROASCASTED through the EWCONSOLE",'evt',self.error, True)
            self.log.write(r,'evt',self.error, True)
            return [-1]

        else:
            self.log.write("not well known exception or error ocurred",'evt',self.error, True)
            return [-1]
            
    def stopBroadcast(self):
        cmd = 'ewbsconsole STOP -i ' + self.ewbsconsolehost
        try:
            self.log.write("Stopping broadcasting an ongoing broadcasting...",'evt',self.info,True)
            output = subprocess.Popen(cmd,stdout = subprocess.PIPE, stderr = subprocess.STDOUT)
            self.log.write("End of the execution of the subprocess. Checking results",'evt',self.info,True)
        except Exception as e:
            self.log.write("The red terminal could not be running. Please check the error message:",'evt',self.error,True)
            self.log.write(repr(e),'evt',self.error,True)
            self.log.write(repr(e),'sys',self.error,True)
            sys.exit(1)
            
        if output.stderr != None:
            self.log.write("There was an error stoppping an ongoing broadcast:",'sys',self.error,True)
            self.log.write(output.stderr,'sys',self.error,True)
            return [-1]

        self.log.write("Reading response from the server",'sys',self.info,False)
        r = output.stdout.read()

        self.log.write("response was read: %s" % r ,'sys',self.info, False)
        output.stdout.close()
        return
        
    def CheckConnection(self):
        self.log.write("Checking if the ewbsconsole can acccess to the red terminal that runs at : %s " % self.ewbsconsolehost,\
        'sys',self.info, True)
        cmd = 'ewbsconsole check -i ' + self.ewbsconsolehost
        self.log.write("Start checking connection...",'sys',self.info, True)
        try:
            output = subprocess.Popen(cmd, stdout = subprocess.PIPE, stderr = subprocess.STDOUT)
        except Exception as e:
            self.log.write('not possible to open a process. Check the error below:','sys',self.error,True)
            self.log.write(repr(e),'sys',self.error, True)
            return -1

        if output.stderr != None:
            self.log.write("There is an error while checking the connection:",'sys',self.error, True)
            self.log.write(output.stderr,'evt',self.error, True)
            return 1

        self.log.write("Reading response from the server:",'sys',self.info, True)
        r = output.stdout.read()
        r = r.lower()
        output.stdout.close() #closing Popen

        if r.find("timespan diff") > 1:
            self.log.write("The red terminal is up and running",'sys',self.info, True)
            return 0

        elif r.find("refused") > 0:
            self.log.write("The red terminal running at %s is not working. Check the error:" % self.ewbsconsolehost,'sys',self.error, True)
            self.log.write((r), 'sys',self.error, True)
            return -1

        else:
            self.log.write("unknown error. Check the output:",'sys',self.error, True)
            self.log.write(r,'evt',self.error, True)
            return -1

    def StartConnection(self):
        self.log.write("Starting the connection to the red terminal at %s" % self.ewbsconsolehost,'sys',self.info, True)
        cmd = 'ewbsconsole connect -i ' + self.ewbsconsolehost
        self.log.write("Starting the connection...",'sys',self.info, True)
        outout = subprocess.Popen(cmd, stdout = subprocess.PIPE, stderr = subprocess.STDOUT)
        self.log.write("End of the connection process",'sys',self.info, True)

        if output.stderr != None:
            self.log.write("There was an error:",'sys',self.error, True)
            self.log.write(output.stderr,'sys',self.error, True)
            return -1

        self.log.write("Reading response from the server",'sys',self.info, True)
        r = output.stdout.read()
        r = r.lower()
        output.stdout.close() #closing Popen

        if r.find("timespan diff") > 1:
            self.log.write("Successfully connected to the red terminal", 'sys',self.info, True)
            return 0

        elif r.find("refused") > 0:
            self.log.write("No possible to connect to the red terminal. Check the error:",'sys',self.error, True)
            self.log.write(r,'sys',self.error, True)
            return -1

        else:
            self.log.write("unknown error. Check the output:",'sys',self.error, True)
            self.log.write(r,'sys',self.error, True)
            return -1
