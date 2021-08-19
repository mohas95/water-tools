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

	@property
	def state(self):
		"""Return the state of the PHController"""
		return self._state
	@state.setter
	def state(self,value):
		"""Set the state of the PHController"""
		self._state = value

	@property
	def config_file(self):
		"""Return the config_file of the PHController"""
		return self._config_file
	@config_file.setter
	def config_file(self,value):
		"""Set the config_file of the PHController"""
		self._config_file = value

	@property
	def refresh_rate(self):
		"""Return the refresh_rate of the PHController"""
		return self._refresh_rate
	@refresh_rate.setter
	def refresh_rate(self,value):
		"""Set the refresh_rate of the PHController"""
		self._refresh_rate = value

	@property
	def api_dir(self):
		"""Return the api_dir of the PHController"""
		return self._api_dir
	@api_dir.setter
	def api_dir(self,value):
		"""Set the api_dir of the PHController"""
		self._api_dir = value

	@property
	def log_dir(self):
		"""Return the log_dir of the PHController"""
		return self._log_dir
	@log_dir.setter
	def log_dir(self,value):
		"""Set the log_dir of the PHController"""
		self._log_dir = value

	@property
	def high_thresh(self):
		"""Return the high_thresh of the PHController"""
		return self._high_thresh
	@high_thresh.setter
	def high_thresh(self,value):
		"""Set the high_thresh of the PHController"""
		self._high_thresh = value

	@property
	def low_thresh(self):
		"""Return the low_thresh of the PHController"""
		return self._low_thresh
	@low_thresh.setter
	def low_thresh(self,value):
		"""Set the low_thresh of the PHController"""
		self._low_thresh = value

	@property
	def up_pin(self):
		"""Return the up_pin of the PHController"""
		return self._up_pin
	@up_pin.setter
	def up_pin(self,value):
		"""Set the up_pin of the PHController"""
		self._up_pin = value

	@property
	def down_pin(self):
		"""Return the down_pin of the PHController"""
		return self._down_pin
	@down_pin.setter
	def down_pin(self,value):
		"""Set the down_pin of the PHController"""
		self._down_pin = value

	@property
	def dose_time(self):
		"""Return the dose_time of the PHController"""
		return self._dose_time
	@dose_time.setter
	def dose_time(self,value):
		"""Set the dose_time of the PHController"""
		self._dose_time = value

	@property
	def delay_time(self):
		"""Return the delay_time of the PHController"""
		return self._delay_time
	@delay_time.setter
	def delay_time(self,value):
		"""Set the delay_time of the PHController"""
		self._delay_time = value

	@property
	def relay_engine(self):
		"""Return the relay_engine of the PHController"""
		return self._relay_engine
	@relay_engine.setter
	def relay_engine(self,value):
		"""Set the relay_engine of the PHController"""
		self._relay_engine = value

	@property
	def ph_api_file(self):
		"""Return the ph_api_file of the PHController"""
		return self._ph_api_file
	@ph_api_file.setter
	def ph_api_file(self,value):
		"""Set the ph_api_file of the PHController"""
		self._ph_api_file = value

	@property
	def ph(self):
		"""Return the ph of the PHController"""
		return self._ph
	@ph.setter
	def ph(self,value):
		"""Set the ph of the PHController"""
		self._ph = value

	@property
	def logger(self):
		"""Return the logger of the PHController"""
		return self._logger
	@logger.setter
	def logger(self,value):
		"""Set the logger of the PHController"""
		self._logger = value

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
		self.logger.info("[PH Controller]: PH Controller Set up Successful")


	def get_ph(self, manual_ph=None):
		if self.ph_api_file:
			try:
				with open(self.ph_api_file, 'r')as f:
					data = json.load(f)
				ph = data['ph']
			except:
				self.logger.warning('[PH Controller]:Error, Could not retrieve pH data from API file')
				ph = manual_ph
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
				ph = self.ph

				try:
					if ph < self.low_thresh:
						self.logger.info(f'[PH controller]:[Ph={ph}] Low threshold hit enabling PH up')
						self.relay_engine.update_config_file("1",True)
						time.sleep(self.dose_time)
						self.relay_engine.update_config_file("1",False)
						time.sleep(self.delay_time)
					if ph > self.high_thresh:
						self.logger.info(f'[PH controller]:[Ph={ph}] High threshold hit enabling PH down')
						self.relay_engine.update_config_file("2",True)
						time.sleep(self.dose_time)
						self.relay_engine.update_config_file("2",False)
						time.sleep(self.delay_time)
					else:
						time.sleep(self.refresh_rate)
				except:
					self.logger.warning('[PH controller]: Could not get proper PH value, will try again')
					time.sleep(self.refresh_rate)

		self.relay_engine.stop()
		self.logger.info("[PH controller]: Stopped")

	def stop(self):
		self.state = False


if __name__ == '__main__':
	pass
