
# SeisComP, ActiveMQ and EWBS Delays Dashboard

This is a dashboard that reports through graphs the time delays in three main stages that are part of an Integrated System for Alerting about Earthquakes through the Digital TV:

* Earthquake Early Warning System (EWBS) - Seismic Data Processing Delay.

* The Message Broker (ActiveMQ) - Message broker transport Delay

* Emergency Warning Broadcast System (EWBS) - Starting Transmission Delay on Digital TV

  

## Background

Whenever an earthquake occurs seismic waves are generated and travel through the earth's interior. These seismic waves can be detected and registered by a seismic sensors while they are passing by. The detected seismic waves are streamed in near realtime from the sensing site to a data center. In the data center, the data streams from different seismic sensors, located in different places, are acquired and processed in realtime. In the early warning context, an Earthquake Early Warning System - a seismological computational system with early warning algorithms devoted to detect, locate and estimate magnitude- performs the task of processing automatically the seismic data and provides alert messages in Common Alerting Protocol (CAP1.2) and QuakeML. The whole process of automatically detect an Earthquake, locate it and estimate its magnitude takes a time. Additionally, as new data arrives to the data center, the automatic solutions are constantly update. This process takes a time and for Earthquake Early Warning purposes this a delay and it is simbolized as **Δ**SC. 
Once a solution with its magnitude is ready, then this is inmidiately formatted in CAP XML and transported from the EEW System to the EWB System through a message broker called: [ActiveMQ](https://activemq.apache.org/). The time that takes the alert message to be transported from one side to the other is called **Δ** AMQ. 
On the EWBS the eews2ewbs interface is listening to incoming alert messages (also, heartbeats that help monitor if the EEWS system is alive) and once a new one is received this inmediately starts disseminating, and executes the command line interface CLI *ewbsconsole* which formats the emergency message and inserts this into the inserter in order to start broadcasting the message. The difference in time of receiving the alert messages by eews2ewbs interface and starting the transmission of the message through the Digital TV is called **Δ**EWBS.

## Technologies
The Dashboard was developed in Python 2.7 and it can also run on version 3. 
It consists of a group of python scripts for different purposes such as read and write data, create graph, parse log information and so. Thus, in order to have working all the scripts the python modules needed to have running the scripts are:

 - Bokeh
 - Pandas
 - bz2
 - pickle
 - numpy
 - scipy

## Modules
First, the EEW System (EEWS) runs in a Linux OS whereas the EWB System (EWBS) runs on a Windows OS. In order for the alert messages and heartbeats generated in the EEWS to be received on the Windows side, there is a script called *stompy2ewbs.py* which it will be called *the Interface*. 
Second, the interface receives the alert and heatbeat messages in a XML format  from EEWS through ActiveMQ. It processes the information and registers relevant information into log files.  
Third, the log information is stored in the next levels:   
 1. Heartbeats (hb.log)
 2. Events or alerts (evts.log)
 3. System information (sys.log)
 4. JSON report of the alerts that were and not transmitted (report.json)

For the dashboard ony heartbeat and JSON report files are used to collect date and time information and other relevant parameters.
### parselog script (parselog.py) 
This script is meant to read ascii files of the heartbeats and json reports within a defined start and end time and to parse the information. It produces DataFrames of the parsed files.
### Pickle data Manager (pklmanage.py)
This is a class with methods to:

 - Read and Write data
 - Resample heartbeat data
 - set and get availability of data
It decompress and compress files from/to bz2. The format file that is used to handle the data is [Pickle](https://docs.python.org/3/library/pickle.html)
### Update Data (updater.py)
This script basically uses the previous mentioned scripts (parselog and pklmanage) in order to create compressed or decompressed files and set the last updated date and time . The files that this script creates for heartbeats are:
 - Today (for example hb2021025CostaRica)
 - Yesterday (hbYdaCostaRica)
 - Lastweek (hbLwCostaRica)
 - LastMonth (hbLmCostaRica)
 - LastYear (hbLyCostaRica)
Whereas for the Received Alerts from EEWS only one file (for example *scCostaRica*). For the alerts that were or not broadcasted another file (for example *ewbsCostaRica*)
### Graph Generator (graphgen.py)

This script generates timelines and histograms with the data. It is mainly called by dashboard_deltatimes.py script.
### Dashboard Delta Times (dashboard_deltatimes.py)
This script uses pklmanage.py and graphgen.py scripts to create the dashboards. The deltatimes plots are in histograms and timelines for (presented in different tabs):

 - Last 24 hours
 - Today
 - Yesterday
 - Last Week
 - Last Month
 - Last Year

## Set up
To have working the dashboard some configurations are needed. 
To start, download the repo that contains the dashboard folder [EEWS-EWBS_Interface](https://gitlab.seismo.ethz.ch/SED-EEW/ewbs-converter). Within this folder there is a subfolder called _dashboard_ and there the described script files are in.
### Updater configuration
The very first script configuration is within the updater.py script. Open this file and go to the section title (commented actually) _USER CONFIG_. One example is below:

    	#######USER CONFIG ###########
	#
	countries = ['Costa Rica', 'Nicaragua', 'El Salvador']

	#set the name according to the OS (mainly taking care of using \ for windows and / for linux)
	# folderpkl is where the compressed bz2 data is stored
	# folderlog is where the logs are stored. In this case it is assumed that after
	# folderlog is the countryname for example: log\CostaRica\
	if OS == 'Windows':
		folderpkl = 'pickledata\\'
		folderlog = 'log\\'
	else:
		folderpkl = 'pickledata/'
		folderlog = 'log/'
	####### End User Config ##########

The `countries` variable is a list of countries that will be used as a reference to read log information and to create the output files. It may be just one country name. 
The next variables *folderlog* and *folderpkl* are very important ones. The `folderlog` variable will be the starting point for reading log information from the ascii files that the interface (stompy2ewbs.py) creates. The country name list will be used to start searching log files. For example if in the list there is a list item called _El Salvador_ then this will start the searching in the root of:

    log/ElSalvador

and within this folder It will seach within a structure of subfolders:

    YYYY/MM/DD/

so, for folderlog variable it is needed to provide the whole path to the starting point for the log folder. In El Salvador for example this is (for windows OS):

    folderlog='C:\Users\Canal 10 EWBS 1\ewbs\log\\'
  
In the case of the pickle files' folder this is suggested to be kept in the same folder of the dashboard:

    folderpkl = 'pickledata\\'
It is mandatory to leave the two backslash for windows OS `\\` at the end of each variable string.
### Dashboard Configuration
In order to create a HTML file or have the bokeh server running for the dashboard then it is necessary to configure the *dashboard_deltatimes.py* file. Open the file and go the section *USER CONFIG*. One example is below:

    ########## USER CONFIG ################
    #As soon as it finish creating the html
    #enable or disable to show this in a browser
    showme = False
    # A string to identify the log information of this script
    logIdentifier = 'DASHBOARD'
    
    #A list of countries. It can be just one.
    countries  = ['Costa Rica','Nicaragua','El Salvador']
    
    #The colors that represent to each country in a dictionary
    #Please write the countries' name as it was written in the countries list
    countryColor = {"Costa Rica":"blue", "Nicaragua":"orange", "El Salvador":"green"}
    
    output_file('dashboard_deltatimes.html',title='dashboard DeltaTimes')
    
    
    ########## END USER CONFIG#############

## How to Run
### Parse log information with updater
In order to obtain data for creating the plots the first step is to run the updater. This script will read the log ascii files created by the interface (stompy2ewbs.py) and create compressed pickle files. For this purpose just run:

    python update.py
Previously, the updater.py script must be edited in the part of USER CONFIG (as it is explained above).
### Creating the dashboard - HTML or Bokeh Server
There are two options to present the result of the delta times: 

   1. Creating a static HTML file (with some actions to interact with the plots)
   2. Starting a service with Bokeh Server

For the first option, just run the next command:

    python dashboard_deltatimes.py html

If the *showme* variable is True then it will appear a browser with the plots, otherwise, the user must open the output file defined and created by this execution.

And for the second option:

    bokeh serve --show dashboard_deltatimes.py

This will start a service using bokeh.
