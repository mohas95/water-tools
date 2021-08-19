from rpi_control_center import GPIO_engine
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

class PHController():
	def __init__(self,up_pin=26, down_pin=20, ph_api_file='./api/PH.json', config_file='./ph_config.json',dose_time=10,delay_time=20, high_thresh = 8, low_thresh=7, margin= 0.5, api_dir = './api/', log_dir = './logs/', refresh_rate = 1):

		if not os.path.exists(log_dir):
			os.makedirs(log_dir)
		log_file = log_dir + 'PH_Controller.log'

		self.state = False
		self.config_file = config_file
		self.refresh_rate = refresh_rate
		self.api_dir = api_dir
		self.log_dir = log_dir
		self.high_thresh = high_thresh + margin
		self.low_thresh = low_thresh - margin
		self.up_pin = up_pin
		self.down_pin = down_pin
		self.dose_time = dose_time
		self.delay_time = delay_time
		self.relay_engine = None
		self.ph_api_file = ph_api_file
		self.ph = None
		self.logger = setup_logger(name=__name__+"_PH_Controller_logger", logfile=log_file, level=10 if debug_mode else 20, formatter = formatter, maxBytes=2e6, backupCount=3)

	def begin(self):
		default_config = {
							"1":{'name':'PH_up', 'pin':self.up_pin, 'state':False},
							"2":{'name':'PH_down', 'pin':self.down_pin, 'state':False}
						}
		self.relay_engine = GPIO_engine.BulkUpdater(
													config_file = self.config_file,
													api_dir = self.api_dir,
													default_config = default_config,
													refresh_rate = self.refresh_rate,
													log_dir = self.log_dir
													)
		self.relay_engine.safe_stop_all_relays()
		self.relay_engine.start()
		self.get_ph()

	def get_ph(self, manual_ph=None):

		if ph_api_file:
			with open(self.ph_api_file, 'r')as f:
				data = json.load(f)
			ph = data['ph']
		else:
			ph = manual_ph
		self.ph = ph
		return ph

	@threaded
	def start(self):
		self.state = True
		self.begin()

		while self.state:
			self.get_ph()
			if not self.ph:
				self.logger.warning('[PH controller]: Please Enable PH readings')
				time.sleep(5)
			while self.state and self.ph:
				self.get_ph()
				if PH < self.low_ph_thresh:
					self.logger.info('[PH controller]: Low threshold enabling PH up')
					self.relay_engine.update_config_file(1,True)
					time.sleep(self.dose_time)
					self.relay_engine.update_config_file(1,False)
					time.sleep(self.delay_time)
				if PH > self.high_ph_thresh:
					self.logger.info('[PH controller]: High threshold enabling PH down')
					self.relay_engine.update_config_file(2,True)
					time.sleep(self.dose_time)
					self.relay_engine.update_config_file(2,False)
					time.sleep(self.delay_time)
				else:
					time.sleep(self.refresh_rate)
			self.relay_engine.stop()
			self.logger.info("\n[PH controller]: Stopped")

	def stop():
		self.state = False


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
