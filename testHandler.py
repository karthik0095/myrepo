import logging
import os
from pathlib import Path
import sys
import time
import platform
import requests
import json
import threading
import SpeedTestClass
import traceback
import subprocess

print("hello");
logger = logging.basicConfig(filename='testHandlerLog.txt', level=logging.DEBUG,
                             format='%(asctime)s.%(msecs)03d %(levelname)s %(module)s - %(funcName)s: %(message)s',
                             datefmt="%Y-%m-%d %H:%M:%S");
dirPath = os.getcwd();
operatingSystem = platform.system();
args = sys.argv;
server = args[1];
port = args[2];
ooklaServerId='';
if(len(args))==4:
	print("Using the Ookla Server Id Given By User...");
	ooklaServerId=args[3];
	print("Ookla Server Id - "+ooklaServerId );
getConfigurationUrl = "http://"+server+":"+port+"/rest/getTestConfiguration";
setStatusUrl = "http://"+server+":"+port+"/rest/setExecutionStatus";
isConfigActiveUrl = "http://"+server+":"+port+"/rest/isTestConfigurationActive";
touchedFilePath = os.path.join(dirPath,"testHandlerTouch.txt");
touchedFile = Path(os.path.join(dirPath,"testHandlerTouch.txt"));
testId = 0;

def main():

        print("hello1111");
        print("Test Handler Started")
        print("Server IP and Port - " + server + ":" + port);
        print("Configuration URL - " + getConfigurationUrl);
        print("Execution status URL - " + setStatusUrl);
        print("Directory Path - " + dirPath);
        print("Operating System - " + operatingSystem);

	
        try:
            touchFile();

        except Exception as e:

            logging.exception("Exception while File operations");
            logging.info("Aborting Speedtest")
            exit(3)
	
        try:

            logging.debug("Fetching configuration")
            configuration = requests.get(getConfigurationUrl);
            logging.info(str(configuration.content))
            configuration = configuration.json()
            testId = configuration['id']
            logging.info("Test Id - "+str(testId))

        except Exception as e:

            logging.exception("No Configuration Received");
            os.remove(touchedFilePath);
            logging.info("Removed Touched File")
            exit(2);

        try:
            logging.info("Configuration Received - "+str(configuration));
			
            postResponse = requests.post(setStatusUrl, data={'status': 1})
            logging.info("Set status response "+str(postResponse.status_code));
            logging.info("Test Status changed to running");

            type = configuration['type'];
            #type = 1;
            if configuration['noOfExecutions'] == 0:
                configuration['noOfExecutions'] = 1;

            logging.debug("Identifying Test type ");

            """if type == 0:
                logging.info("Test Type - Iperf");
		#iPerfConfig = dict(configuration);
		subCall(configuration);
                #iPerfThread = iPerfHandler.iPerfHandler(configuration,server,port,testId,isConfigActive)
                #iPerfThread.start();
                #iPerfThread.join();
			"""
            if type == 1:
		logging.info("Test Type - SpeedTest");
                speedTestThread = SpeedTestClass.SpeedTest(configuration, server, port,testId,ooklaServerId);
                speedTestThread.start();
                speedTestThread.join();

            else:
                logging.info("Test Type is not SpeedTest");

                """iPerfConfig = dict(configuration);


                iPerfThread = iPerfHandler.iPerfHandler(iPerfConfig, server, port,testId)
                speedTestThread = SpeedTestClass.SpeedTest(configuration, server, port,testId);


                iPerfThread.start();
                speedTestThread.start();

                iPerfThread.join();
                speedTestThread.join();"""


            isConfigActive = requests.get(isConfigActiveUrl);
            isConfigActive = isConfigActive.json();

            if str(isConfigActive) == "True":
                getConfiguration = requests.get(getConfigurationUrl)
                getConfiguration = getConfiguration.json();
                logging.info("Recieved test Id - " + str(getConfiguration['id']))
                logging.info("Test Id from testHandler - " + str(testId))
                if str(getConfiguration['id']) != str(testId):
                    postResponse = requests.post(setStatusUrl, data={'status': 0})
                    logging.info("Completed status response " + str(postResponse.status_code));

            logging.info("Is Configuration Status - "+str(isConfigActive));
        except Exception as e:

            logging.exception("Exception occured from speedtest try block")
            #logging.error(e,exc_info)


        finally:

            os.remove(touchedFilePath);
            logging.info("Removed Touched File")
            logging.debug("Test Completed")

def touchFile():

    logging.debug("Inside Touch File Method");

    if touchedFile.is_file():

        logging.info("Touched File Status - "+"already exists");
        timeStamp = os.path.getctime(touchedFilePath);
        logging.debug("Touched File Created Time - "+str(timeStamp));
        logging.debug("Curent Time - "+str(time.time()));
        logging.debug("Time difference - "+str(time.time()-timeStamp))
        if ((time.time()-timeStamp)>4000):

            logging.info("Creating new timeStamp");
            os.remove(touchedFilePath);
            #open(touchedFile, 'a').close();
            Path(touchedFilePath).touch()
            #return (1);

        else:
            logging.info("Existing Test Handler since touched file inside time limit")
            exit(1)
    else:

        logging.info("Touched File Status - "+"not found");
        #open(touchedFile, 'a').close();
        Path(touchedFilePath).touch()
        logging.debug("Created touch file");
        #return (1);

main();


