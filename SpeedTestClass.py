import subprocess
import os
import time
import re
import requests
import logging
import threading
from pathlib import Path
import json
import testHandler

class SpeedTest(threading.Thread):
    testInterval = 2
    postUrl = "";
    activeUrl = "";
    testConfigurationUrl = "";
    noOfExecutions = 0;
    id = "";
    count = 0;
    speedTestResultFile = "";
    speedTestPyFile = "";
    latency = '0';
    tcpUpLink = '0';
    tcpDownLink = '0';
    udpUplink = '0';
    udpDownLink = '0';
    receivedTestId = 0;
    speedTestServerId = 0;

    def __init__(self,configuration,server,port,testId,ooklaServerId):

        threading.Thread.__init__(self)
        self.ooklaServerId=ooklaServerId;
        self.receivedTestId = testId;
        self.noOfExecutions = configuration['noOfExecutions'];
        self.id = configuration['id'];
        #self.band = configuration['band'];
	speedTestServer = configuration['speedTestServer']	
	print("speedTestServer- "+str(speedTestServer))	
	self.speedTestServerId = speedTestServer['id'];
	print("speedTestServerId- "+str(self.speedTestServerId))
        self.testInterval = configuration['testInterval'];
        self.postUrl = "http://"+server+":"+port+"/rest/speedtest";
        self.activeUrl  = "http://"+server+":"+port+"/rest/isTestConfigurationActive";
        self.testConfigurationUrl = "http://" + server + ":" + port + "/rest/getTestConfiguration";

        logger = logging.basicConfig(filename='speedTestLog.txt', level=logging.DEBUG,
                                     format='%(asctime)s.%(msecs)03d %(levelname)s %(module)s - %(funcName)s: %(message)s',
                                     datefmt="%Y-%m-%d %H:%M:%S");
        self.testInterval = self.testInterval - 1;
        self.testInterval = self.testInterval * 60;
        if self.speedTestServerId==3:
            self.speedTestResultFile = os.path.join(os.getcwd(), "speedTestResult.txt");
        else:
            self.speedTestResultFile = os.path.join(os.getcwd(), "xfinitySpeedTestResult.txt");
        logging.info("Test Time interval in Seconds - " + str(self.testInterval))
        logging.info("SpeedTest Result file - " + self.speedTestResultFile)
        logging.info("Current Working Directory - " + str(os.getcwd()))

    def run(self):
        self.speedTestIterator();


    def speedTestIterator(self):

        while(self.count<self.noOfExecutions):

            getConfiguration =  requests.get(self.testConfigurationUrl)
            getConfiguration = getConfiguration.json();
            logging.info("Recieved test Id - "+str(getConfiguration['id']))
            logging.info("Test Id from testHandler - " + str(self.receivedTestId))
            if str(getConfiguration['id']) != str(self.receivedTestId):
                logging.info("Test Configuration mismatch - Exiting from SpeedTest")
                break;
            isConfigActive = requests.get(self.activeUrl).json();
            #isConfigActive ="true";
            print ("Configuration Status - "+str(isConfigActive));
            if str(isConfigActive) == "True":
                Path(os.path.join(os.getcwd(),"testHandlerTouch.txt")).touch()
                self.count+=1;
                logging.info("Before making tcpDownLink, tcpUpLink, latency as 0")
		self.tcpDownLink = '0';
		self.tcpUpLink = '0';
		self.latency = '0';
		logging.info ("tcpUpLink after setting to 0 - "+str(self.tcpUpLink))
                logging.info ("Test is running for "+str(self.count)+" th time")
                self.runSpeedtestPy();
                #time.sleep(self.testInterval);
            else:
                logging.info("Configuration is not true - Stopping SpeedTest ")
                break;


    def runSpeedtestPy(self):

        try:

            self.speedTestObject = open(self.speedTestResultFile, 'w');
            logging.info("Created Result File ");

        except Exception as e:

            logging.exception("Cannot create result file in location - "+self.speedTestResultFile)

        try:
            logging.info("Started SpeedTest Script")
            if self.speedTestServerId==3:
                self.speedTestPyFile = os.path.join(os.getcwd(),"speedtest.py");
                if(self.ooklaServerId!=''):
                    subprocess.call(['python',self.speedTestPyFile,'--server',self.ooklaServerId], stdout=self.speedTestObject);
                else:
                    subprocess.call(['python',self.speedTestPyFile], stdout=self.speedTestObject);
            else:
                self.speedTestPyFile = os.path.join(os.getcwd(),"xfinitySpeedTest.py");
                subprocess.call(['python',self.speedTestPyFile],stdout=self.speedTestObject);

            self.speedTestObject.close();

            self.speedTestObject = open(self.speedTestResultFile, 'r');
            fileContents = self.speedTestObject.readlines()
            logging.info("SpeedTest Result - "+str(fileContents));
            for eachLine in fileContents:

                if eachLine.__contains__("ms"):
                    eachLineList = eachLine.split(":")
                    s = eachLineList[1]
                    self.latency =  ((re.findall("\d+\.*\d+",s))[0])
                    logging.info ("Latency - "+self.latency)

                if eachLine.__contains__("Download:"):
                    eachLineList = eachLine.split(":")
                    s = eachLineList[1]
                    self.tcpDownLink = ((re.findall("\d+\.\d+", s))[0])
                    logging.info("TCP Download - "+self.tcpDownLink)

                if eachLine.__contains__("Upload:"):
                    eachLineList = eachLine.split(":")
                    s = eachLineList[1]
                    self.tcpUpLink = ((re.findall("\d+\.\d+", s))[0])
                    logging.info("TCP Upload - "+self.tcpUpLink)


            self.speedTestObject.close();

            payload = {"udpUplink": str(self.udpUplink),"udpDownlink":str(self.udpDownLink),"tcpDownlink":str(self.tcpDownLink),"tcpUplink":str(self.tcpUpLink),"latency":str(self.latency), "speedTestServerId":self.speedTestServerId};

            head = {'Content-Type': 'application/json'}

            logging.info("Payload for POST operation - "+str(payload));

        except Exception as e:

            logging.exception("During String parsing")

        try:

            postResponse = requests.post(self.postUrl, data=json.dumps(payload), headers=head);
            logging.info("POST Response - " + str(postResponse));


        except Exception as e:
            logging.exception("POST operation failed")

        try:
            logging.info("SpeedTest waiting for - "+str(self.testInterval))
            logging.info(str(type(self.testInterval)))
            time.sleep(self.testInterval)
            logging.info("SpeedTest waited for " + str(self.testInterval) + " ms")

        except Exception as e:
            logging.exception("Exception from sleep thread ")









