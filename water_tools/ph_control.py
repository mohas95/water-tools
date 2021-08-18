from rpi_control_center import GPIO_engine
from DFRobot import DFR_PH, DFR_ADS1115
import json
import threading
import datetime
import time
import os
import os.path
import glob
import logging
import logzero
from logzero import setup_logger

######## Default Configuration
default_config = {
		"1":{'name':'PH_up', 'pin':26, 'state':False},
		"2":{'name':'PH_down', 'pin':20, 'state':False}
}
########################################################### Global Variables
format = '%(color)s[%(levelname)1.1s %(asctime)s %(name)s :%(funcName)s %(thread)d]%(end_color)s %(message)s' # format for the logzero logger
formatter = logzero.LogFormatter(fmt=format) # format object for logzero logger
debug_mode = False #debug mode for developers

########################################################### Wrapper/decorator definition function
def threaded(func):
	"""start and return a thread of the passed in function. Threadify a function with the @threaded decorator"""
	def wrapper(*args, **kwargs):
		thread = threading.Thread(target=func, args=args, kwargs=kwargs, daemon=False)
		thread.start()
		return thread
	return wrapper

def push_to_api(api_file, data):

	timestamp = datetime.datetime.now().strftime('%Y/%m/%d %H:%M:%S')

	data["last updated"] = timestamp

	with open(api_file, "w") as f:
		f.write(json.dumps(data, indent=4))

# class PHController():
#     def __init__(self):
#         self.temperature = None
#         self.high_thresh
#         self.low_thresh
#         self.up_state
#         self.down_state
#         self.ph_monitor_state
#         self.ph
#         self.up_pin = 26
#         self.down_pin = 20

class TempMonitor():
	def __init__(self, api_dir= './api/', log_dir='./log/', refresh_rate=1):

		if not os.path.exists(log_dir):
			os.makedirs(log_dir)
		if not os.path.exists(api_dir):
			os.makedirs(api_dir)

		log_file = log_dir + 'temperature_process.log'

		self.state = False
		self.temperature = None
		self.refresh_rate= refresh_rate
		self.api_file = api_dir + 'TEMPERATURE.json'
		self.logger = setup_logger(name= __name__+ "_temp_logger", logfile=log_file, level=10 if debug_mode else 20, formatter = formatter, maxBytes=2e6, backupCount=3)
		self.one_wire_device_folder = self.begin()
		self.thread = None

	def begin(self):
		try:
			# Settings for the RTD temperature probe
			os.system('modprobe w1-gpio')
			os.system('modprobe w1-therm')
			base_dir = '/sys/bus/w1/devices/'
			device_folder = glob.glob(base_dir + '28*')[0]
			device_file = device_folder + '/w1_slave'

			self.logger.info("\n[Temperature monitor]: Temperature Sensor Set up Successful")

			return device_file

		except:
			self.logger.warning("[Temperature monitor]: Error Initializing Temperature Probe")

	def get_temp(self, device_file):
		try:
			with open(device_file, "r") as f:
				lines = f.readlines()

			while lines[0].strip()[-3:] != 'YES':
				time.sleep(0.2)

				with open(device_file, "r") as f:
					lines = f.readlines()

			equals_pos = lines[1].find('t=')
			if equals_pos != -1:
				temp_string = lines[1][equals_pos+2:]
				temperature = float(temp_string) / 1000.0

			return temperature
		except:
			self.logger.warning("[Temperature monitor]: Error Failed to get temperature data")

	@threaded
	def start(self):
		success=None
		self.state = True

		while self.state and not success:
			self.one_wire_device_folder = self.begin()
			success =True

		while self.state:
			self.temperature = self.get_temp(self.one_wire_device_folder)
			data = {"temperature":self.temperature,"unit":"Celsius"}
			push_to_api(self.api_file, data)
			self.logger.info(f'[Temperatur(Celsuis)]: {self.temperature}')
			time.sleep(self.refresh_rate)

		self.temperature = None
		data = {"temperature(Celsius)":self.temperature}
		push_to_api(self.api_file, data)
		self.logger.info("\n[Temperature monitor]: Stopped")

	def stop(self):
		self.state=False

#
# class PHMonitor():
#     def __init__(self):
#         self.state


if __name__ == '__main__':
	pass

# gpio_engine = GPIO_engine.BulkUpdater(
#                                         config_file = './ph_config.json',
#                                         api_dir = './api',
#                                         default_config = default_config,
#                                         refresh_rate = 1
#                                         )
# gpio_engine.start()
#
#
#
#
#
# gpio_engine.stop()
