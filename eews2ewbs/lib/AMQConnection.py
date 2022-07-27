from stompy.simple import Client
from threading import Thread, Lock
import threading
import Log
import sys, time, datetime, os, subprocess
import util
import xml.etree.ElementTree as ET
import json
import platform
import time
from Log import Log
from ErrorReport import ErrorReport 

OS = platform.uname()[0]

class AMQConnection:

    def __init__(self, cfg):
        #Variables
        self.cfg = cfg
        self.topic = '/topic/' + cfg.topic
        self.username = cfg.user
        self.password = cfg.password
        self.host = cfg.host
        self.port = int(cfg.port)
        self.lasthb = 0
        self.events = []
        self.stomp = None
        self.reconnectTimeout = 120 #in seconds
        
        self.ongoingEvtTransmission = False #evt id for the current one being transmitted
        self.ongoingEvtId = None
         
        self.lock = Lock()                      # just to avoid race condition in the new and updated transmission
        self.maxthreads = 10000
        self.pool_sema = threading.Semaphore(value=self.maxthreads)
        
        #logging levels
        self.info = 'info'
        self.warning = 'warning'
        self.error = 'error'

        
        self.alertns = '{urn:oasis:names:tc:emergency:cap:1.2}'
        self.ewbsconnection = None
        
        self.log = Log(cfg.countryName)
        
        if self.cfg.emailReport:
            self.er = ErrorReport( self.cfg )
        
        
    #Connection to AMQ server but NOT subscribing to any topic!
        try:
            self.stomp = Client(host=self.host, port=self.port)
            self.log.write("Connection successful to AMQ",'sys', self.info, True)
            self.stomp.connect(username=self.username, password=self.password)
            self.log.write("username and password accepted for this connection",'sys', self.info, True)
        except:
            self.log.write("there was a problem to connect and/or subscribe to AMQ",'sys',self.error, True)
            self.log.write("Please check if the input values for AMQ are correct or ask the Seismological Agency if the AMQ is running",'sys',self.error,True)

    def connectAMQ(self):

        try:
            self.stomp = Client(host=self.host, port=self.port)
            self.log.write("Connection successful to AMQ",'sys', self.info, True)
            self.stomp.connect(username=self.username, password=self.password)
            self.log.write("username and password accepted for this connection",'sys', self.info, True)

        except:
            self.log.write("there was a problem to connect and/or subscribe to AMQ",'sys',self.error, True)
            self.log.write("Please check if the input values for AMQ are correct or ask the Seismological Agency if the AMQ is running",'sys',self.error,True)
            return -1
        self.log.write('subscribing to the topic...','sys',self.info, True )
        try:
            self.stomp.subscribe(self.topic)
            self.log.write('...subscribed', 'sys',self.info,True)
        except:
            self.log.write("ERROR: It was not possible to subscribe to the topic: %s." % self.topic, 'sys',self.error,True)
            self.log.write('Either AMQ is not running or there is a network issue','sys',self.error, True)
            self.log.write('Exiting from this script....','sys',self.error,True)
            return -1

    def disconnectAMQ(self):
        try:
            self.log.write('Discconneting from AMQ msg broker','sys',self.info, True)
            self.stomp.unsubscribe(self.topic)
            self.stomp.disconnect()
        except:
            self.log.write('Error while unsubscribing from topic or disconnecting from AMQ', 'sys',self.error, True)
            return -1

    def saveJSON(self,jsoninfo):
        #Saving JSON information for each event: new or updated ones
        tmp = self.log.outfile()
        
        fn = tmp+"reports.json"

        self.log.write( 'file name for json output: %s' % fn,'sys',self.info, False )
        if os.path.exists(fn):
            self.log.write('Appending json into: %s file' % fn,'sys',self.info, False )
            file = open(fn, 'r')
            try:
                data = json.load(file)
                file.close()
            except:
                self.log.write('the file exists but it is empty. Filling with this new json information','sys',self.info,True)
                file.close()
                data=[]
            try:
                data.append(jsoninfo)
                file = open(fn, 'w+')
                json.dump(data,file)
            except Exception as e:
                self.log.write('Error in dumping json data into file: %s' % e,'sys',self.info,True)
            file.close()
        else:
            #New file
            self.log.write('creating new file: %s' % fn, 'sys',self.info,False )
            data = []
            file = open(fn, 'w')
            try:
                data.append(jsoninfo)
                json.dump(data,file)
            except Exception as e:
                self.log.write('Error in dumping json data into file: %s' % e,'sys',self.info,True)
            file.close()

    def XmlParser(self, xmlstr ):

        try:
            xml = ET.fromstring(xmlstr)
        except Exception as e:
            self.log.write("an unknown error has occurred while parsing the next xml string:",'sys',self.error,True)
            self.log.write(xmlstr,'sys',self.error, True)
            rval = {}
            rval['type'] = 'unknown'
            return rval
        if xml.tag.find("hb") > 0:
            #this is a heartbeat
            #logger.info('Heartbeat Message. Parsing information')
            xml.attrib['type'] = 'hb'
            if self.cfg.hblog:
                if self.cfg.loghbstdout:
                    self.log.write(xmlstr,'hb',self.info,True)
                else:
                    self.log.write(xmlstr,'hb',self.info, False)
            else:
                if self.cfg.loghbstdout:

                    self.log.write(xmlstr,None,self.info, False)
            
            return xml.attrib

        elif xml.tag.find("alert") > 0:

            # this is a CAP message
            self.log.write("Alert Message Received at: %s" % util.getNowUTCstr(), 'evt',self.info, True)
            #Saving the xml string into evt log file if True
            if self.cfg.evtlog:
                self.log.write( "---------------------------------------------------------------",'evt',self.info,False)
                self.log.write( xmlstr, 'evt',self.info, False )
                self.log.write( "---------------------------------------------------------------",'evt',self.info,False)
            event = {} #temporary event object

            event['type'] = 'alert'
            try:
                # Checking if the event is already in the events array
                event['id'] = xml.find(self.alertns+'identifier').text
                self.log.write( "event ID: %s" % event['id'], 'evt', self.info, True )
                infos = xml.findall(self.alertns+'info')
                if len(infos)>1 and self.cfg.language is not None:
                    info = filter(lambda x: x.find(self.alertns+'language').text == self.cfg.language, infos)[0]
                elif len(infos) == 1:
                    info = infos[0]#filter(lambda x: x.findall(self.alertns+'language')[0].text == self.language, infos)
                
                parameters = info.findall(self.alertns+'parameter')
                magparam = filter( lambda x: x.find(self.alertns+'valueName').text == 'magnitude', parameters)[0]
                magnitude = round( float(magparam.find(self.alertns+'value').text), 1 )
                event['magnitude'] = magnitude
                headline = info.find(self.alertns + 'headline' ).text
                try:
                    event['headline'] = headline.encode('latin1')
                except Exception as e:
                    self.log.write('Forcing to be ASCII:  %s' %e, 'sys',self.error, True)
                    event['headline'] = headline.encode('ascii', 'ignore' )
                originTime = filter( lambda x: x.find(self.alertns+'valueName').text == 'originTime', parameters)[0]
                originTime = originTime.find(self.alertns + 'value').text
                event['originTime'] = originTime
                
                magnitudeCreation = filter( lambda x: x.find(self.alertns+'valueName').text == 'magnitudeCreationTime', parameters)[0]
                magnitudeCreation = magnitudeCreation.find(self.alertns + 'value').text
                event['magnitudeCreation'] = magnitudeCreation
                instruction = info.find( self.alertns + 'instruction' ).text
                event['instruction'] = instruction 
                
                self.log.write( "Origin Time: %s (%s), Magnitude: %s" % (event['originTime'], util.datetime2timestamp(event['originTime']), event['magnitude']), 'evt', self.info, True )
                self.log.write( "Event Instructions: %s" % event['instruction'], 'evt', self.info, False)
                if 'headline' in event:
                    self.log.write( "Headline: %s " % event['headline'],'evt',self.info,True)
                else:
                    log ( "This alert msg does not contain 'headline' information", 'evt',self.info,True )
            except Exception as e:
                self.log.write("Not possible to parse alert:\n%s" % e, 'sys', self.error, True )
                return {'type': 'unknown'}
            
            return event

        else:
            self.log.write("Not well known xml string",'sys',self.info, True)
            self.log.write(xmlstr,'sys',self.info,False)
            return {'type': 'unknown'}

    def send(self, msg):
        try:
            self.stomp.put(msg, destination=self.topic)
        except Exception, e:
            raise Exception('Cannot reconnect to server: %s' % e)
    
    def msgProcess(self, msg):
        '''
        Processing either alert or hearbeat messages
        '''    
        #
        receivedMsgTime =util.getNowUTCsecs()
        recMsgStr = util.getNowUTCstrms()
        try:
            response = self.XmlParser(msg)
        except:
            self.log.write( 'An error reading the message %s' % msg,'sys', self.error, False )
            return
        
        #Alert messages
        if response['type'] == 'alert':
            #locking the thread
            try:
                self.pool_sema.acquire()
                self.lock.acquire()
                self.log.write("Thread locked", 'sys',self.info, False)
            except Exception as e:
                self.log.write("thread was not locked: %s" % e, 'sys',self.error, False)
            
            try:
                origintimeUTC = util.datetime2timestamp(response['originTime'])
            except:
                self.log.write("ERROR: Not origin time for %s event!" % response['id'], 'sys',self.error, True )
                origintimeUTC = 0.0
            
            try:
                magCreationTimeUTC = util.datetime2timestamp(response['magnitudeCreation'])
            except:
                self.log.write("ERROR: Not possible to obtain timestamp for magnitude creation time", 'sys',self.error, True )
                try:
                    self.pool_sema.acquire()
                    self.lock.acquire()
                    self.log.write("Thread locked", 'sys',self.info, False)
                except Exception as e:
                    self.log.write("thread was not locked: %s" % e, 'sys',self.error, False)
            
            #Checking if there is an evt object with response['id']
            tmpAlert = filter(lambda x: x['id'] == response['id'], self.events)

            #New event check
            if len(tmpAlert) == 0 :
                #No, there is no this event in self.events.
                #New event!
                self.log.write("Creating a new Event Alert Object...", 'sys',self.info, False)
                
                #creating a new evt object
                evt = {} # empty obj to contain information for the new event
                
                evt['id'] = response['id']
                evt['magnitude'] = response['magnitude']
                evt['originTime'] = response['originTime']
                evt['creationTime'] = util.getNowUTCsecs()
                evt['bc'] = 0 #not transmitted yet
                
                self.log.write("ID: %s, Mag: %s, orTime: %s" %( evt['id'], evt['magnitude'], evt['originTime'] ), 'sys',self.info, False)
                self.log.write('NEW EVENT with ID: %s has been received' % evt['id'] , 'evt',self.info, True)
                self.log.write("Appending %s into events list" % evt['id'], 'sys',self.info, False)
                self.events.append(evt)

                nowutc = util.getNowUTCsecs()
                deltaTime = nowutc - origintimeUTC
               
                self.log.write("%s seconds has passed since the ORIGIN TIME" % deltaTime, 'evt', self.info, True)

                #is there an ongoing transmission?
                if not self.ongoingEvtId:
                    #NO, there is not an ongoing transmission
                    
                    #starting a new tranmission
                    self.log.write( "No ongoing transmission.", 'sys',self.info, False )
                    
                    #Reported Magnitude is the current mag
                    evt['reportedMagnitude'] = response['magnitude']
                    #setting the evt['id'] into the ongoingEvtId
                    self.ongoingEvtId = evt['id']
                    
                    #requesting transmission
                    tmp = self.transmit( response, evt, True, recMsgStr )
                    
                else:
                    #YES, there is one ongoing transmission
                    #okay, so, time to check the mag for the event that is currently on transmission
                    
                    #getting the ID for the ongoing evt tranmission
                    tmpEvtId = self.ongoingEvtId
                    
                    ongoingEvt = None
                    try:
                        ongoingEvt = filter(lambda x: x['id'] == tmpEvtId, self.events )[0]
                    except:
                        self.log.write("not possible to obtain information for ongoing evt with ID: %s" % tmpEvtId, 'sys',self.info, False)
                        try:
                            self.lock.release()
                            self.pool_sema.release()
                        except:
                            pass
                        
                        self.ongoingEvtId = None
                        return
                            
                    self.log.write("An ongoing transmission for event %s" % tmpEvtId, 'sys',self.info, False)
                    
                    magDiff = evt['magnitude'] - ongoingEvt['reportedMagnitude']
                   
                    if magDiff >= self.cfg.magDiff:
                        #so this is a new event and it has a magnitude larger than the one that is transmitted now
                        
                        #stopping the transmission and start this new one
                        self.log.write("STOPPING TRANSMISSION: ongoing event mag is %s lower than new event mag" % self.cfg.magDiff,'evt',self.info, True)
                        self.ewbsconnection.stopBroadcast()
                        self.ongoingEvtId = None
                        
                        self.log.write("STARTING A NEW EVENT: start broadcast at: %s (localtime) or %s (UTC)" % \
                                    (util.getNowLOCALstr(),util.getNowUTCstr()),'evt',self.info, True)
                        
                        self.ongoingEvtId = evt['id']
                        evt['reportedMagnitude'] = evt['magnitude']
                        
                        #new transmission requested
                        tmp = self.transmit(response, evt, True, recMsgStr) 
                    
                    else:
                        startBroadcastTime = 0
                        endBroadcastTime = 0
                         
                        self.log.write("There is an ongoing transmission. Saving basic information for this event...", 'evt',self.info,True)
                        
                        self.log.write("No reporte will be broadcasted", 'evt', self.info, True)
                        evt['reportedTime'] = util.getNowUTCsecs()
                        evt['reportedMagnitude'] = response['magnitude']
                        
                        evt['creationTime'] = util.getNowUTCsecs()
                        
                        #self.events.append(evt) ->Mistake! already appended
                        
                        jsoninfo = self.jsonDic(response, [], recMsgStr, startBroadcastTime, endBroadcastTime, True, False)
                        
                        if self.cfg.jsonlog and len(jsoninfo) > 0 :
                            self.saveJSON(jsoninfo)
                        
                        elif len(jsoninfo) == 0:
                            if self.cfg.jsonlog:
                                self.log.write('Error writing json information into report.json file', 'sys', self.error, True)
                        
                        try:
                            self.lock.release()
                            self.pool_sema.release()
                        except Exception as e:
                            self.log.write("thread was not released: %s" % e, 'sys',self.error, False)
            
            #is the event already in self.events?
            elif len( tmpAlert ) == 1 :
                #An event already registered in self.events
                
                #collecting information fo the registered event
                regEvt =  tmpAlert[0]
                regEvt['originTime'] = response['originTime']
                regEvt['magitude'] = response['magnitude']
                self.log.write("There is an event already registered. ID: %s, Mag: %s, orTime: %s" % ( regEvt['id'], regEvt['magnitude'], regEvt['originTime'] ), 'sys',self.info, False)
                regEvt['magnitude'] = response['magnitude']
                
                if not self.ongoingEvtId:
                    #No ongoing transmission
                    magDiff = regEvt['magnitude'] - regEvt['reportedMagnitude']
                    
                    self.log.write("There is NO an ongoing transmission...", 'sys',self.info, False)
                    
                    self.log.write("Mag difference: %s" % round(magDiff,1), 'sys',self.info, False)
                    self.log.write("Times broadcasted: %s" % regEvt['bc'], 'sys',self.info, False)
                    #TODO: add a variable in user config for magDiff
                    #potential bug ?
                    
                    #start a transmission if it has only transmitted once o zero times 
                    # and magnitude difference between what the new magnitude
                    # and it has been transmitted in greater or equal than 1.
                    if (regEvt['bc'] < 2 and magDiff >= self.cfg.magDiff ): 
                        #self.log.write("UPDATE: start broadcast at: %s (localtime) or %s (UTC)" % \
                        #            (util.getNowLOCALstr(),util.getNowUTCstr()),'evt',self.info, True)
                        
                        regEvt['reportedMagnitude'] = response['magnitude']
                        self.ongoingEvtId = response['id']
                        
                        #starting the tranmission
                        tmp = self.transmit(response, regEvt, False, recMsgStr) 
                    
                    else:
                        if regEvt['bc'] == 2: 
                            self.log.write("This event was broadcasted twice. No more transmissions", 'evt',self.info,True)
                        if magDiff < self.cfg.magDiff:
                            #todo: add a new variable
                            self.log.write("The mag difference for this update is less than %s" % self.cfg.magDiff, 'evt',self.info,True)
                        jsoninfo = self.jsonDic(response, [], recMsgStr, 0, 0, False, False)
                        
                        if self.cfg.jsonlog and len(jsoninfo) > 0 :
                            self.saveJSON(jsoninfo)
                        
                        elif len(jsoninfo) == 0:
                            if self.cfg.jsonlog:
                                self.log.write('Error writing json information into report.json file', 'sys', self.error, True)
                        
                        try:
                            self.lock.release()
                            self.pool_sema.release()
                        except Exception as e:
                            self.log.write("thread was not released: %s" % e, 'sys',self.error, False)
                else:
                    #there is an ongoing transmission!
                    
                    #okay, so, time to check the mag for the event that is currently on transmission
                    self.log.write("There is an ongoing transmission...", 'sys',self.info, False)
                   
                    tmpEvtId = self.ongoingEvtId
                    ongoingEvt =  None
                    try:
                        ongoingEvt = filter(lambda x: x['id'] == tmpEvtId, self.events )[0]
                    except:
                        self.log.write("not possible to obtain information for ongoing evt with ID: %s" % tmpEvtId, 'sys',self.info, False)
                        try:
                            self.lock.release()
                            self.pool_sema.release()
                        
                            return
                        except:
                            pass
                        self.ongoingEvtId = None
                        return
                            
                    magDiff = regEvt['magnitude'] - ongoingEvt['reportedMagnitude']
                    
                    self.log.write("Mag difference: %s" % round(magDiff,1), 'sys',self.info, False)
                    
                    if magDiff >= self.cfg.magDiff:
                        #so this is a new event and it has a magnitude larger than the one that is transmitted now
                        
                        #stopping the transmission and start this new one
                        self.log.write("STOPPING TRANSMISSION: ongoing event mag is %s lower than new event mag" % self.cfg.magDiff,'evt',self.info, True)
                        self.ewbsconnection.stopBroadcast()
                        self.ongoingEvtId = False
                        
                        self.log.write("UPDATED EVENT: start broadcast at: %s (localtime) or %s (UTC)" % \
                                    (util.getNowLOCALstr(),util.getNowUTCstr()),'evt',self.info, True)
                        
                        regEvt['reportedMagnitude'] = response['magnitude']
                        self.ongoingEvtId = response['id']
                        tmp = self.transmit(response, regEvt, False, recMsgStr) 
                    
                    else:
                        
                        self.log.write("There is an ongoing transmission. Saving basic information for this event...", 'evt',self.info,True)
                        
                        self.log.write("No reporte will be broadcasted", 'evt', self.info, True)
                        
                        jsoninfo = self.jsonDic(response, [], recMsgStr, 0, 0, False, False)
                        
                        if self.cfg.jsonlog and len(jsoninfo) > 0 :
                            self.saveJSON(jsoninfo)
                        
                        elif len(jsoninfo) == 0:
                            if self.cfg.jsonlog:
                                self.log.write('Error writing json information into report.json file', 'sys', self.error, True)
                        
                        try:
                            self.lock.release()
                            self.pool_sema.release()
                        except Exception as e:
                            self.log.write("thread was not released: %s" % e, 'sys',self.error, False)
            
            else:
                self.log.write("There are %s times events with ID: %s" % ( len( tmpAlert), response['id'] ) , 'sys',self.error,False )
                try:
                    self.lock.release()
                    self.pool_sema.release()
                except:
                    pass
                        
            #clean up the events array
            now = util.getNowUTCsecs()
            if len(self.events) > 0:
                newList = list( filter(lambda x: ( now - x['creationTime'] ) < 7200, self.events) )
                self.events = newList
            #########

        elif response['type'] == 'hb':
            #
            #compare the created time and received time!
            # more than 1 second or negative = Problem!
            # write problematic hb into JSON
            #

            currenthb = util.datetime2timestamp(response['timestamp'])
            if currenthb - self.lasthb > 5.5:
                self.log.write("The connection to AMQ message broker was reestablished after %s seconds" % (currenthb - self.lasthb), 'hb',self.error,False )
                if sys.version_info.major == 2:
                    print "\nThe connection to AMQ message broker was reestablished after %s seconds\n" % (currenthb - self.lasthb),
                    sys.stdout.flush()
                    print '\r',
                    self.lasthb = currenthb
                else:
                    print ("\nThe connection to AMQ message broker was reestablished after %s seconds\n" % (currenthb - self.lasthb),)
                    sys.stdout.flush()
                    print ('\r',)
                    self.lasthb = currenthb
                return
            else:
                self.lasthb = currenthb
                diffTime =  receivedMsgTime - currenthb
            
            self.log.write('hbtime:%s,receiveTime:%s,deltaVal:%s' % (response['timestamp'],recMsgStr, diffTime),'hb',self.info,False)
            if OS == 'Windows':
                os.system('title '+"CURRENT HEARTBEAT: "+response['timestamp'].split('.')[0]+ "(UTC) ("+util.getNowLOCALstr().split('.')[0]+" Local)")
            if sys.version_info.major == 2:
                print "CURRENT HEARTBEAT: "+response['timestamp'].split('.')[0]+ "(UTC) ("+util.getNowLOCALstr().split('.')[0]+" Local)",
                sys.stdout.flush()
                print "\r",
            else:
                print ("CURRENT HEARTBEAT: "+response['timestamp'].split('.')[0]+ "(UTC) ("+util.getNowLOCALstr().split('.')[0]+" Local)",)
                sys.stdout.flush()
                print ("\r",)
    
    def transmit(self, response, evt, isNewEvt, msgReceivedTime ):
        
        startTransmissionTime = util.getNowUTCstrms()
    
        if isNewEvt:
            self.log.write("NEW: start broadcast at: %s (localtime) or %s (UTC)" % \
                        (util.getNowLOCALstr(),util.getNowUTCstr()),'evt',self.info, True)
        else:
            self.log.write("UPDATE: start broadcast at: %s (localtime) or %s (UTC)" % \
                        (util.getNowLOCALstr(),util.getNowUTCstr()),'evt',self.info, True)
        
        try:
            self.lock.release()
            self.pool_sema.release()
            self.log.write('Lock and semaphore released.', 'evt',self.info, False)
        except Except as e:
            self.log.write('There was a problem while releasing the lock and semaphore: %s' % e, 'sys',self.info, True)
            pass

        tmp = []
        if self.cfg.dryrun:
            self.log.write('not broadcasting. dryrun enabled. Sleeping for 10 seconds', 'evt',self.info, True)
            time.sleep(10)
        
        elif self.cfg.capsmsg:
        
            if 'headline' in response:
                tmp = self.ewbsconnection.BroadcastMsg(response['headline'], self.cfg.msgtime)
            else:
                self.log.write("Using a static message for event %s because there is no headline" % response['id'], 'sys',self.info, False)
                tmp = self.ewbsconnection.BroadcastMsg(self.cfg.alertmsg, self.cfg.msgtime)
    
        elif self.cfg.staticmsg:
            tmp = self.ewbsconnection.BroadcastMsg(self.cfg.alertmsg, self.cfg.msgtime)
        else:
            if self.cfg.language == 'es-US':
                msg = "Magnitud %s ocurrido a las %s. " % (response['magnitude'],util.UTCdatetime2LocalTime(response['originTime']))
                msg += "%s" % response['instruction']
            else:
                msg = "Magnitude %s, Date and Time: %s. " % (response['magnitude'],util.UTCdatetime2LocalTime(response['originTime']))
                msg += "%s" % response['instruction']
            
            tmp = self.ewbsconnection.BroadcastMsg(msg, self.cfg.msgtime)

        stopTransmissionTime = util.getNowUTCstrms()
                    
        self.log.write("End of broadcasted message for event %s at: %s (localtime) or %s (UTC)" % \
                                        ( response['id'],util.getNowLOCALstr(), util.getNowUTCstr() ), 'evt', self.info, True )
                                        
        if isNewEvt:
            evt['creationTime'] = util.getNowUTCsecs()
        
        jsoninfo = {}
        
        if len(tmp) == 2:
            self.log.write("Status: SUCCESSFUL",'evt',self.info, True)
            if isNewEvt:
                jsoninfo = self.jsonDic(response, tmp, msgReceivedTime, startTransmissionTime, stopTransmissionTime, isNewEvt, True)
            else:
                jsoninfo = self.jsonDic(response, tmp, msgReceivedTime, startTransmissionTime, stopTransmissionTime, False, True)
            
            evt['reportedTime'] = util.getNowUTCsecs()
            evt['reportedMagnitude'] = response['magnitude']
            evt['bc'] += 1
        
        else:
            self.log.write("Status: ERROR", 'evt',self.error, True )
            if isNewEvt:
                jsoninfo = self.jsonDic(response, tmp, msgReceivedTime, startTransmissionTime, stopTransmissionTime, isNewEvt, False)
            else:
                jsoninfo = self.jsonDic(response, tmp, msgReceivedTime, startTransmissionTime, stopTransmissionTime, False, False)
            
            evt['reportedTime'] = 0
            evt['reportedMagnitude'] = 0.0
        
        if self.cfg.jsonlog and len(jsoninfo)> 0:
            self.saveJSON(jsoninfo)
        
        elif len(jsoninfo) == 0:
            if self.cfg.jsonlog:
                self.log.write('Error writing json information into report.json file', 'sys', self.error, True)
        
        self.ongoingEvtId = None
        
    def receive(self):

        self.lasthb = util.getNowUTCsecs()
        try:
            self.stomp.subscribe(self.topic)
        except:
            self.log.write("ERROR: It was not possible to subscribe to the topic: %s." % self.topic, 'sys',self.error,True)
            self.log.write('Either AMQ is not running or there is a network issue','sys',self.error, True)
            self.log.write('Exiting from this script....','sys',self.error,True)
            sys.exit(1)

        errorRep = False
        
        while True:

            #
            try:
                message = self.stomp.get_nowait()
                errRep = False
            except Exception as e:
                now = util.getNowUTCsecs()
                if self.lasthb >0:
                    diff = int(now) - int(self.lasthb)
                    if diff>0 and diff%10 == 0: #every 10 seconds a message of error is presented in the console
                        os.system('title '+"ERROR: heartbeat last report was: "+ util.timestamp2datetime(self.lasthb)+"(Local Time) -  Current date and Time: "+util.getNowLOCALstr().split('.')[0] + "(Local)")
                        if sys.version_info.major == 2:
                            print "ERROR: heartbeat last report was: "+util.timestamp2datetime(self.lasthb)+"(Local Time) -  Current date and Time: "+util.getNowLOCALstr().split('.')[0] + "(Local)",
                            sys.stdout.flush()
                            print "\r",
                        else:
                            print ("ERROR: heartbeat last report was: "+util.timestamp2datetime(self.lasthb)+"(Local Time) -  Current date and Time: "+util.getNowLOCALstr().split('.')[0] + "(Local)",)
                            sys.stdout.flush()
                            print ("\r",)
                        if errorRep==False:#this is just to register this error in system log only once
                            self.log.write("Error: The last heartbeat was %s seconds ago. See potential problems with the AMQ message broker.\n" % diff,'sys',self.error, False)
                            errorRep = True
                            
                    if self.cfg.emailReport:
                        if diff > 0 and diff % self.reconnectTimeout == 0 and self.er.lastHbErrorReport == 0.0:
                            self.log.write("Reporting through email because the last hb was %s seconds ago and reonnect timeout was reached" % diff,'sys',self.error, True)
                            #send email
                            self.er.sendEmail(1,'',diff)
                            self.er.lastHbErrorReport = now
                        elif diff > 0 and diff % (60*60*6) == 0:
                            self.log.write("Reporting through email because the last hb was %s seconds ago" % diff,'sys',self.error, True)
                            self.er.sendEmail(1,'',diff)
                            self.er.lastHbErrorReport = now
                            
                            
                    time.sleep(0.05)
                    if diff > 0 and diff % self.reconnectTimeout == 0 : #Every 2 minutes it will disconnect and reconnect to AMQ msg broker
                        self.log.write('Disconnecting from AMQ message broker.','sys',self.info, True)
                        ret = self.disconnectAMQ()
                        self.log.write('Connecting to AMQ message broker','sys',self.info,True)
                        ret = self.connectAMQ()
                        time.sleep(1) #just to avoid a quick disconnection within less than a second
                continue
                
            #starting a thread
            try:
                worker = Thread(target=self.msgProcess, args=(message.body,))
                worker.start()
            except RuntimeError as e:
                 self.log.write("Failed at %s thread" % len(threading.enumerate()),'sys',self.error, True)
                 self.log.write(str(e), 'sys',self.error, True)
                 self.ongoingEvtId = None
                 if self.lock.locked():
                     self.lock.release()
                 if self.pool_sema.locked():
                     self.pool_sema.release()
                 if self.cfg.emailReport:
                     self.er.sendEmail(4,str(e),0)
        self.stomp.unsubscribe(self.topic)
        self.stomp.disconnect()
    
    def jsonDic(self, response, ewbscmdres, recTime, startBc, stopBc, firstTimeBc, wasBroadcasted ):
        #this method creates the json dictionary
        #using as input the event info, the time that broadcast started and stopped
        #and if this is the first time it was broadcasted
        
        jsoninfo = {}
        
        #using the information from the alert msg    
        jsoninfo['id'] = response['id']
        jsoninfo['originTime'] = response['originTime']
        jsoninfo['magnitude'] = response['magnitude']
        jsoninfo['magnitudeCreation'] = response['magnitudeCreation']
        #the time that the msg was received
        jsoninfo['receivedAlertTime'] = recTime
        
        #was this msg broadcasted? 1: yes, 0: no
        jsoninfo['broadcasted'] = 1 if wasBroadcasted else 0
        
        #response from the ewbsconsole
        if len(ewbscmdres)>0: 
        
            jsoninfo['startConsole'] = ewbscmdres[1]['startConsole']
            jsoninfo['startTransmission'] = ewbscmdres[1]['startTransmission']
            jsoninfo['stopTransmission'] = ewbscmdres[1]['stopTransmission']
            jsoninfo['stopConsole'] = ewbscmdres[1]['stopConsole']
        
        else:
        
            jsoninfo['startConsole'] = 0
            jsoninfo['startTransmission'] = 0
            jsoninfo['stopTransmission'] = 0
            jsoninfo['stopConsole'] = 0
            
        jsoninfo['startBroadcast'] = startBc
        jsoninfo['endBroadcast'] = stopBc
        jsoninfo['firstTime']= 1 if firstTimeBc else 0
        
        return jsoninfo
        
