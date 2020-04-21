import time 
import sys
import os
import re
import json
import logging
import datetime
import platform
if __name__ == '__main__':
    pass

from selenium import webdriver
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By


LOG_FILENAME = 'speedtest_xfinity.log'
logging.basicConfig(filename=LOG_FILENAME,level=logging.DEBUG)

currentworkingdirectory = os.getcwd()
chrome_driver_path=str(currentworkingdirectory)+'\chromedriver.exe'
logging.debug("Path of Chrome driver :" +chrome_driver_path)
chrome_options = Options()
chrome_options.add_argument('headless')

driver = webdriver.Chrome(options=chrome_options,executable_path=chrome_driver_path)

print("Xfinity Speed-test Started") 
 
driver.get("http://speedtest.xfinity.com") 
try:                                          
    start_button_element=WebDriverWait(driver, 15).until(
	EC.presence_of_element_located((By.XPATH, '//*[@id="app"]/div[2]/div/div/div/button')))
    start_button_element.click()   
    print("Xfinity Speed-test is running on your device...")
    logging.debug("Fetching Download Speed...")
    download_speed_element = WebDriverWait(driver, 30).until(
	EC.presence_of_element_located((By.XPATH, '//*[@id="app"]/div[2]/details/summary/div/dl/dd')))
    driver.execute_script("window.scrollTo(0, 200)");
    show_more_button=driver.find_element_by_xpath('//*[@id="app"]/div[2]/details/summary/div');
    show_more_button.click();
    logging.debug("Fetching Upload Speed and Latency...")
    time.sleep(15);
    upload_speed_element=WebDriverWait(driver, 30).until(
	EC.presence_of_element_located((By.XPATH, '//*[@id="app"]/div[2]/details/div/div/dl/div[1]/dd')))
    latency_element=driver.find_element_by_xpath('//*[@id="app"]/div[2]/details/div/div/dl/div[2]/dd'); 		
    print("Download:"+download_speed_element.text)
    print("\nUpload:"+upload_speed_element.text) 
    print("\nLatency:"+latency_element.text)   
   
except NoSuchElementException as exception:
    logging.debug(exception)

except KeyboardInterrupt:
        logging.debug('\nCancelling...')

except Exception as e:
	logging.debug(e)
	
finally:
	driver.close()
	print("Speed Test Completed");	
               

