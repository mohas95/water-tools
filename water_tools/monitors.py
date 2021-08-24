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
	"""Push data in json format to an api file"""
	timestamp = datetime.datetime.now().strftime('%Y/%m/%d %H:%M:%S')
	data["last updated"] = timestamp
	with open(api_file, "w") as f:
		f.write(json.dumps(data, indent=4))

########################################################### Classes
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
		self.one_wire_device_file = None
		self.thread = None

	@property
	def state(self):
		"""Return the state of the TempMonitor"""
		return self._state
	@state.setter
	def state(self,value):
		"""Set the state of the TempMonitor"""
		if not isinstance(value, bool):
			raise TypeError("State must be a bool")
		self._state = value

	@property
	def temperature(self):
		"""Return the temperature of the TempMonitor"""
		return self._temperature
	@temperature.setter
	def temperature(self,value):
		"""Set the temperature of the TempMonitor"""
		self._temperature = value

	@property
	def refresh_rate(self):
		"""Return the refresh_rate of the TempMonitor"""
		return self._refresh_rate
	@refresh_rate.setter
	def refresh_rate(self,value):
		"""Set the refresh_rate of the TempMonitor"""
		if not isinstance(value, int):
			raise TypeError("refresh_rate must be a integer")
		self._refresh_rate = value

	@property
	def api_file(self):
		"""Return the api_file of the TempMonitor"""
		return self._api_file
	@api_file.setter
	def api_file(self,value):
		"""Set the api_file of the TempMonitor"""
		if not isinstance(value, str):
			raise TypeError("api_file must be a string")
		self._api_file= value

	@property
	def logger(self):
		"""Return the logger of the TempMonitor"""
		return self._logger
	@logger.setter
	def logger(self,value):
		"""Set the logger of the TempMonitor"""
		self._logger= value

	@property
	def thread(self):
		"""Return the thread of the TempMonitor"""
		return self._thread
	@thread.setter
	def thread(self,value):
		"""Set the thread of the TempMonitor"""
		self._thread= value

	@property
	def one_wire_device_file(self):
		"""Return the one_wire_device_file of the TempMonitor"""
		return self._one_wire_device_file
	@one_wire_device_file.setter
	def one_wire_device_file(self,value):
		"""Set the one_wire_device_file of the TempMonitor"""
		self._one_wire_device_file = value

	def begin(self):
		try:
			# Settings for the RTD temperature probe
			os.system('modprobe w1-gpio')
			os.system('modprobe w1-therm')
			base_dir = '/sys/bus/w1/devices/'
			device_folder = glob.glob(base_dir + '28*')[0]
			device_file = device_folder + '/w1_slave'
			self.logger.info("[Temperature monitor]: Temperature Sensor Set up Successful")
			self.one_wire_device_file = device_file
			return device_file
		except:
			self.logger.warning("[Temperature monitor]: Error Initializing Temperature Probe")

	def get_temp(self):
		device_file = self.one_wire_device_file
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
			self.temperature = temperature
			return temperature
		except:
			self.logger.warning("[Temperature monitor]: Error Failed to get temperature data")
			self.temperature = None
			return None

	@threaded
	def start(self):

		self.state = True
		self.begin()
		while self.state:
			self.get_temp()
			data = {"temperature":self.temperature,"unit":"Celsius"}
			push_to_api(self.api_file, data)
			self.logger.debug(f'[Temperatur(Celsuis)]: {self.temperature}')
			time.sleep(self.refresh_rate)
		self.temperature = None
		data = {"temperature":self.temperature,"unit":"Celsius"}
		push_to_api(self.api_file, data)
		self.logger.info("[Temperature monitor]: Stopped")

	def stop(self):
		self.state=False

class PHMonitor:
	def __init__(self, api_dir='./api/', log_dir='./log/', temperature_api_file = None, refresh_rate=1, ADC_pin=0, I2C_ADR = DFR_ADS1115.ADS1115_IIC_ADDRESS0, gain =DFR_ADS1115.ADS1115_REG_CONFIG_PGA_6_144V):

		if not os.path.exists(log_dir):
			os.makedirs(log_dir)
		if not os.path.exists(api_dir):
			os.makedirs(api_dir)
		log_file = log_dir + 'PH_process.log'
		self.state = False
		self.ph = None
		self.temp = None
		self.voltage = None
		self.temperature_api_file = temperature_api_file
		self.refresh_rate= refresh_rate
		self.api_file = api_dir + 'PH.json'
		self.logger = setup_logger(name= __name__+ "_ph_logger", logfile=log_file, level=10 if debug_mode else 20, formatter = formatter, maxBytes=2e6, backupCount=3)
		self.ADC_pin = ADC_pin
		self.I2C_ADR = I2C_ADR
		self.gain = gain
		self.ph_reader = None
		self.ADC_reader =None
		self.thread = None

	@property
	def state(self):
		"""Return the state of the PHMonitor"""
		return self._state
	@state.setter
	def state(self,value):
		"""Set the state of the PHMonitor"""
		self._state = value

	@property
	def ph(self):
		"""Return the ph of the PHMonitor"""
		return self._ph
	@ph.setter
	def ph(self,value):
		"""Set the ph of the PHMonitor"""
		self._ph = value

	@property
	def temp(self):
		"""Return the temp of the PHMonitor"""
		return self._temp
	@temp.setter
	def temp(self,value):
		"""Set the temp of the PHMonitor"""
		self._temp = value

	@property
	def voltage(self):
		"""Return the voltage of the PHMonitor"""
		return self._voltage
	@voltage.setter
	def voltage(self,value):
		"""Set the voltage of the PHMonitor"""
		self._voltage = value

	@property
	def temperature_api_file(self):
		"""Return the temperature_api_file of the PHMonitor"""
		return self._temperature_api_file
	@temperature_api_file.setter
	def temperature_api_file(self,value):
		"""Set the temperature_api_file of the PHMonitor"""
		self._temperature_api_file = value

	@property
	def refresh_rate(self):
		"""Return the refresh_rate of the PHMonitor"""
		return self._refresh_rate
	@refresh_rate.setter
	def refresh_rate(self,value):
		"""Set the refresh_rate of the PHMonitor"""
		self._refresh_rate = value

	@property
	def api_file(self):
		"""Return the api_file of the PHMonitor"""
		return self._api_file
	@api_file.setter
	def api_file(self,value):
		"""Set the api_file of the PHMonitor"""
		self._api_file = value

	@property
	def logger(self):
		"""Return the logger of the PHMonitor"""
		return self._logger
	@logger.setter
	def logger(self,value):
		"""Set the logger of the PHMonitor"""
		self._logger = value

	@property
	def ADC_pin(self):
		"""Return the ADC_pin of the PHMonitor"""
		return self._ADC_pin
	@ADC_pin.setter
	def ADC_pin(self,value):
		"""Set the ADC_pin of the PHMonitor"""
		self._ADC_pin = value

	@property
	def I2C_ADR(self):
		"""Return the I2C_ADR of the PHMonitor"""
		return self._I2C_ADR
	@I2C_ADR.setter
	def I2C_ADR(self,value):
		"""Set the I2C_ADR of the PHMonitor"""
		self._I2C_ADR = value

	@property
	def gain(self):
		"""Return the gain of the PHMonitor"""
		return self._gain
	@gain.setter
	def gain(self,value):
		"""Set the gain of the PHMonitor"""
		self._gain = value

	@property
	def ph_reader(self):
		"""Return the ph_reader of the PHMonitor"""
		return self._ph_reader
	@ph_reader.setter
	def ph_reader(self,value):
		"""Set the ph_reader of the PHMonitor"""
		self._ph_reader = value

	@property
	def ADC_reader(self):
		"""Return the ADC_reader of the PHMonitor"""
		return self._ADC_reader
	@ADC_reader.setter
	def ADC_reader(self,value):
		"""Set the ADC_reader of the PHMonitor"""
		self._ADC_reader = value

	@property
	def thread(self):
		"""Return the thread of the PHMonitor"""
		return self._thread
	@thread.setter
	def thread(self,value):
		"""Set the thread of the PHMonitor"""
		self._thread = value

	def begin(self):
		voltage_reader = DFR_ADS1115.ADS1115() #instantiate as1115 ADC I2X Unit
		ph_reader = DFR_PH.DFRobot_PH() # instantiate PH Probe
		voltage_reader.setAddr_ADS1115(self.I2C_ADR) # set the I2C Address to 0x48
		voltage_reader.setGain(self.gain)
			# ph.reset()
		ph_reader.begin()
		self.ph_reader, self.voltage_reader = ph_reader, voltage_reader
		self.logger.info("[PH monitor]: PH Sensor Set up Successful")
		return ph_reader, voltage_reader

	def get_ph(self, temp=25):
		try:
			voltage = self.voltage_reader.readVoltage(self.ADC_pin)

			if self.temperature_api_file:
				try:
					with open(self.temperature_api_file,'r') as f:
						data = json.load(f)
					temperature = data['temperature']
					if not temperature:
						temperature = temp
				except:
					self.logger.warning('[PH monitor]:Error, Could not retrieve temperature from api file, using default')
					temperature = temp
			else:
				temperature = temp


			self.ph = self.ph_reader.readPH(voltage['r'],temperature)
			self.temp = temperature
			self.voltage = voltage['r']

			return self.ph, self.voltage, self.temp
		except:
			self.logger.warning('[PH monitor]:Error, Could not retrieve pH Data')
			self.ph = None
			self.temp = None
			self.voltage = None
			return self.ph, self.voltage, self.temp

	@threaded
	def start(self):
		self.state = True
		self.begin()
		while self.state:
			self.get_ph()
			data = {"ph":self.ph,"unit":"ph"}
			push_to_api(self.api_file, data)
			self.logger.debug('[PH monitor]: PH Voltage: {}, Temperature: {} ----> PH: {}'.format(self.voltage,self.temp,self.ph))
			time.sleep(self.refresh_rate)
		self.ph = None
		data = {"ph":self.ph,"unit":"ph"}
		push_to_api(self.api_file, data)
		self.logger.info("[PH monitor]: Stopped")
	def stop(self):
		self.state=False

if __name__ == '__main__':

    temp_monitor = TempMonitor()
    ph_monitor = PHMonitor(temperature_api_file = './api/TEMPERATURE.json')
    temp_monitor.start()
    ph_monitor.start()
    try:
        while True:
            time.sleep(1)
    except:
        temp_monitor.stop()
        ph_monitor.stop()
