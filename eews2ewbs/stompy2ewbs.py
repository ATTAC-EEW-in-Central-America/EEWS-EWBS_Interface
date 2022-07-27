#!/usr/bin/env python
"""
#!c:/Python27/python.exe
Send a test message to an AMQ broker.
Created on Mar 10, 2014

@author: behry

Change Log:
23/06/2021      Added XML parser, logging, and a class for EWBSconsole.
                Every alert msg is logged into a JSON file with different timestamps.
                Clean up the code and using open Process instead of os.system call
                to get the stdout response and stderr for errors.
                - Billy Burgoa Rosso

12/08/2021      Added Thread and Lock option to avoid locking the main
                thread whenever any message (alert or heartbeat type) is received.
                Every message is processed by a thread so there won't be mainly any missing heartbeat. 
                It is also added an option to disconnect and reconnect (also subscribe)
                to AMQ broker message when there is more than X minutes (configurable at AMQConnection class self.reconnectTimeout)
                that any HB is not received.
                - Billy Burgoa Rosso
"""

import sys, time, datetime, os, subprocess
import socket
#import util
import datetime
#import json
import platform
#import time

import lib
#

OS = platform.uname()[0]

if OS== 'Windows':
    os.system('cls')
else:
    os.system('clear')

if __name__ == '__main__':
    
    
    #log level
    info = 'info'
    warning = 'warning'
    error = 'error'
    
    #starting reading the configuration file
    cfg = lib.Configuration()
    
    
    #stating a log object
    l = lib.Log(cfg.countryName)
    
    #
    #Starting the information
    tmpmsg = "\n**************************\nStarting the script AMQ to EWBS....\n**************************\n"
    l.write(tmpmsg,'hb',info,False)
    l.write(tmpmsg,'evt',info,False)
    l.write(tmpmsg,'sys',info,True)
    
    if cfg.ewbsconsolehost.lower() == 'localhost':
        cfg.ewbsconsolehost = socket.gethostname()
        l.write('The hostname for localhost is: %s' % cfg.ewbsconsolehost,'sys',info, False)
    l.write("AMQ: host: %s, port: %s, user: ****, Password: ****, topic:%s, typeConnection: %s" % \
            (cfg.host, cfg.port, cfg.topic, cfg.typeConnection),  'sys',info, False )
    
    try:
        ewbsconnection = lib.EWBSConsoleConnection(cfg)
    except Exception as e:
        l.write("Error instancing the ewbsconnection object",'sys',error, True)
        l.write("Please check the configuration values and ewbsconsole is in the env. variables", 'sys', error, True)
        l.write(repr(e),'evt',error,False)
        l.write(repr(e),'hb',error,True)
        sys.exit(1)
        
    l.write("EWBSCONSOLE: host: %s, message duration: %s" % \
    (cfg.ewbsconsolehost, cfg.msgtime),  'sys',info, False)

    if cfg.staticmsg:
        l.write("The alert Msg is:\n %s" % cfg.alertmsg,'sys',info, False)
    
    try:
        client = lib.AMQConnection(cfg)
       
        #setting the ewbsconnection
        client.ewbsconnection = ewbsconnection
    
    except Exception as e:
        l.write("Error instancing the AMQConnection object",'sys',error, True)
        l.write("Please check the configuration values", 'sys', error, True)
        l.write(repr(e),'evt',error,False)
        l.write(repr(e),'hb',error,True)
        sys.exit(1)

    if cfg.typeConnection == 'receiver':
        l.write('Checking if the red terminal is reachable at %s from this script' % ewbsconnection.ewbsconsolehost, 'sys', info, True)
        tmp = ewbsconnection.CheckConnection()
        tmp  = 0 if cfg.dryrun else tmp
        if tmp == -1 or tmp == 1:
            l.write('not possible to connect to red terminal', 'sys', error, True)
            #util.popupmsg("ERROR DE CONEXION","La terminal Roja no esta funcionando.\nPRIMERO Inicie la interfaz grafica.\nLUEGO cierre esta ventana")
            numattempts = 0
            import time
            while numattempts < 11:
                numattempts += 1
                tmp = ewbsconnection.CheckConnection()
                if tmp == -1 or tmp == 1:
                    l.write( 'not possible to connect to red terminal. Attempt: %s'  % numattempts, 'sys', error, True)
                    #util.popupmsg("ERROR DE CONEXION","La terminal Roja todavia no responde. Inicie la interfaz grafica y cierre esta ventana")
                    l.write("sleeping for 3 seconds", 'sys', info, True)#hardcoded
                    time.sleep(3)
                elif tmp == 0:
                    l.write("The red terminal is working!", 'sys', info, True)
                    break

                if numattempts == 10:
                    l.write("The red terminal is not running. it was attempted %s times a connection but did not work" % numattempts,"sys",error,True)
                    l.write("The red terminal does not work. exiting",'sys',error,True)
                    l.write("The red terminal does not work. exiting",'evt',error,False)
                    l.write("The red terminal does not work. exiting",'hb',error,False)
                    
                    #Send an email
                    if cfg.emailReport:
                        re = lib.ErrorReport(cfg)
                        re.sendEmail(2,'',0)
                    #sys.exit(1)
        elif tmp == 0:
            l.write("The red terminal is working and reachable from this script",'sys',info,False)
    
        l.write('starting the main loop as a receiver client', 'sys', info, True)
        client.receive()


    else:
        if sys.version_info.major == 2:
            print "'type' has to be either 'receiver', 'sender' or 'heartbeat'"
        else:
            print ("'type' has to be either 'receiver', 'sender' or 'heartbeat'")
