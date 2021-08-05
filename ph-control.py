import sys
sys.path.append('./DFRobot')

import RPi.GPIO as GPIO
import time
import json
import os.path
import glob

from DFRobot_ADS1115 import ADS1115
from DFRobot_PH import DFRobot_PH

import threading

############################################################ Define RPI Pins
ph_up = 26 # Relay_Ch1 = 26
ph_down = 20 # Relay_Ch2 = 20
# Relay_Ch3 = 21
ph_probe_ADC = 0 #Analog 0 pin on the as1115 ADC
AS1115_I2C_ADR = 0x48 # address of the I2C AS1115 ADC

############################################################ Define Global variables
margin = 0.5 # margin of sensitivity for the PH Threshold
high_ph_thresh = 8 + margin # upper threshold of pH until ph down activates
low_ph_thresh = 7 - margin # lower threshold of pH until ph down activates
dose_delay_time = 60 # Delay time between dosages
dose_on_time = 5 # Length of dose time
retry_count = 10 # number of times process will try to restart until it exits
refresh_rate = 1 #how often program will check for changes of status from status json file in seconds
sample_frequency = 1.0 #sample frequency of the ph probe in seconds
status_json = './status.json' #location of the status json file
status_log = './logs/status.log'
process_log = './logs/process.log'


### DO NOT CHANGE THESE VARIABLES (used to pass information between processes)
PH = None # variable storing PH readings, set to None, when ph monitor is not activated
temperature = None # Fixed temperature, should be replaced with sensor readings for temp compensation
ph_up_status = None # variable used to pass on the status of each process determined by the status.json file
ph_down_status = None # variable used to pass on the status of each process determined by the status.json file
ph_monitor_status = None # variable used to pass on the status of each process determined by the status.json file
temp_monitor_status = None # variable used to pass on the status of each process determined by the status.json file

ADS1115_REG_CONFIG_PGA_6_144V        = 0x00 # 6.144V range = Gain 2/3
ADS1115_REG_CONFIG_PGA_4_096V        = 0x02 # 4.096V range = Gain 1
ADS1115_REG_CONFIG_PGA_2_048V        = 0x04 # 2.048V range = Gain 2 (default)
ADS1115_REG_CONFIG_PGA_1_024V        = 0x06 # 1.024V range = Gain 4
ADS1115_REG_CONFIG_PGA_0_512V        = 0x08 # 0.512V range = Gain 8
ADS1115_REG_CONFIG_PGA_0_256V        = 0x0A # 0.256V range = Gain 16

############################################################ Process Functions

def PH_up():
	'''
	'''
	global temperature
	global PH
	global ph_up
	global low_ph_thresh
	global dose_delay_time
	global dose_on_time
	global retry_count
	global ph_up_status
	global refresh_rate
	success = None
	count = 0

	### GPIO Setup
	while success==None and ph_up_status:
		try:
			GPIO.setup(ph_up,GPIO.OUT)
			GPIO.output(ph_up, GPIO.HIGH)
			print('\n[PH+]: Initialized PH up doser')
			success = 1
		except:
			print('\n[PH+]: ERROR Initializing PH up doser')
			update_status(process_status = 'ph_up', status_file = status_json, status_value = False)
			time.sleep(refresh_rate*2)
			ph_up_status = False

	### Process
	while ph_up_status:
		if not PH:
			print('[PH+]: Please Enable PH readings')
			time.sleep(5)
		while PH and ph_up_status:
			try:
				if PH < low_ph_thresh:
					print(f'[PH+]: {PH} lower than threashold, activating pump')
					GPIO.output(ph_up, GPIO.LOW)
					time.sleep(dose_on_time)
					GPIO.output(ph_up, GPIO.HIGH)
					print(f'[PH+]: pump deactivated, waiting {dose_delay_time} seconds')
					time.sleep(dose_delay_time)

					count = 0
				else:
					pass
			except:
				GPIO.output(ph_up, GPIO.HIGH) #just incase turn off pump
				count += 1
				tries_left = retry_count-count
				print(f'[PH+]: ERROR in PH Up control, will try {tries_left} more times')
				time.sleep(1)

				if count+1 >= retry_count:
					print("[PH+]: Exceeded the number of retries, closing process... attempting to restart process")
					update_status(process_status = 'ph_up', status_file = status_json, status_value = False)
					time.sleep(refresh_rate*2)
					ph_up_status = False

				else:
					pass
		GPIO.output(ph_up, GPIO.HIGH) #just incase turn off pump

def PH_down():
	'''
	'''
	global PH
	global ph_down
	global high_ph_thresh
	global dose_delay_time
	global dose_on_time
	global retry_count
	global ph_down_status
	global status_json
	global refresh_rate
	success = None
	count = 0

	### GPIO Setup
	while success==None and ph_down_status:
		try:
			GPIO.setup(ph_down,GPIO.OUT)
			GPIO.output(ph_down, GPIO.HIGH)
			print('\n[PH-]: Initialized PH down doser')
			success = 1
		except:
			print('\n[PH-]: ERROR Initializing PH down doser')
			update_status(process_status = 'ph_down', status_file = status_json, status_value = False)
			time.sleep(refresh_rate*2)
			ph_down_status = False

	### Process
	while ph_down_status:
		if not PH:
			print('[PH-]: Please Enable PH readings')
			time.sleep(5)
		while PH and ph_down_status:
			try:
				if PH > high_ph_thresh:
					print(f'[PH-]: {PH} higher than the upper threashold, activating pump')
					GPIO.output(ph_down, GPIO.LOW)
					time.sleep(dose_on_time)
					GPIO.output(ph_down, GPIO.HIGH)
					print(f'[PH-]: pump deactivated, waiting {dose_delay_time} seconds')
					time.sleep(dose_delay_time)

					count = 0
				else:
					pass
			except:
				GPIO.output(ph_down, GPIO.HIGH)
				count += 1
				tries_left = retry_count-count
				print(f'[PH-]: ERROR in PH down control, will try {tries_left} more times')
				time.sleep(1)

				if count+1 >= retry_count:
					print("[PH-]: Exceeded the number of retries, closing process... attempting to restart process")
					update_status(process_status = 'ph_down', status_file = status_json, status_value = False)
					time.sleep(refresh_rate*2)
					ph_down_status = False

				else:
					pass

		GPIO.output(ph_down, GPIO.HIGH)


def get_temp():
	'''
	'''
	global status_json
	global temperature
	global retry_count
	global temp_monitor_status
	global sample_frequency
	global refresh_rate
	success = None
	count = 0

	while temp_monitor_status:
		### Sensor Setup
		while success == None and temp_monitor_status:
			try:
				# Settings for the RTD temperature probe
				os.system('modprobe w1-gpio')
				os.system('modprobe w1-therm')
				base_dir = '/sys/bus/w1/devices/'
				device_folder = glob.glob(base_dir + '28*')[0]
				device_file = device_folder + '/w1_slave'

				print("\n[Temperature monitor]: Temperature Sensor Set up Successful")
				success = 1

			except:
				print("[Temperature monitor]: Error Initializing Temperature Probe")
				update_status(process_status = 'temp_monitor', status_file = status_json, status_value = False)
				time.sleep(refresh_rate*2)
				temp_monitor_status=False

		### Process
		while temp_monitor_status:
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

				print("[Temperature monitor]: Temperature:{}".format(temperature))
				time.sleep(sample_frequency)

				count = 0

			except:
				temperature = None
				count += 1
				tries_left = retry_count-count
				print(f'[Temperature monitor]: ERROR trying to Get Temperature data from the sensor, will try {tries_left} more times')
				time.sleep(1)

				if count+1 >= retry_count:
					print("[TEMPERATURE monitor]: Exceeded the number of retries, closing process... Please restart process")

					update_status(process_status = 'temp_monitor', status_file = status_json, status_value = False)
					time.sleep(refresh_rate*2)
					temp_monitor_status = False

				else:
					pass

		temperature = None

def get_PH():
	'''
	'''
	global ph_probe_ADC
	global temperature
	global PH
	global retry_count
	global AS1115_I2C_ADR
	global ph_monitor_status
	global sample_frequency
	global status_json
	global refresh_rate
	success = None
	count = 0

	while ph_monitor_status:
		### Sensor Setup
		while success == None and ph_monitor_status:
			try:
				ads1115 = ADS1115() #instantiate as1115 ADC I2X Unit
				ph = DFRobot_PH() # instantiate PH Probe

				ads1115.setAddr_ADS1115(AS1115_I2C_ADR) # set the I2C Address to 0x48
				ads1115.setGain(ADS1115_REG_CONFIG_PGA_6_144V)

				# ph.reset()
				ph.begin()

				print("\n[PH monitor]: PH Sensor Set up Successful")
				success = 1

			except:
				print("[PH monitor]: Error Initializing PH Probe, reseting please recalibrate")
				ph.reset()
				update_status(process_status = 'ph_monitor', status_file = status_json, status_value = False)
				time.sleep(refresh_rate*2)
				ph_monitor_status = False

		### Process
		while ph_monitor_status:
			try:
				#Get the Digital Value of Analog of selected channel
				ph_voltage = ads1115.readVoltage(ph_probe_ADC)
				#Convert voltage to PH with temperature compensation

				if temperature:
					temp = temperature
				else:
					temp = 25

				print('[PH monitor]: PH Voltage: {}, Temperature: {} ----> '.format(ph_voltage['r'],temp), end = '')
				PH = ph.readPH(ph_voltage['r'],temp)
				print("PH:{}".format(PH))
				time.sleep(sample_frequency)

				count = 0

			except:
				PH = None
				count += 1
				tries_left = retry_count-count
				print(f'[PH monitor]: ERROR trying to Get PH data from the sensor, will try {tries_left} more times')
				time.sleep(1)

				if count+1 >= retry_count:
					print("[PH monitor]: Exceeded the number of retries, closing process... Please restart process")
					update_status(process_status = 'ph_monitor', status_file = status_json, status_value = False)
					time.sleep(refresh_rate*2)
					ph_monitor_status = False

				else:
					pass
		PH = None

############################################################ Helper functions

def load_status(file, last_status=None):

	if os.path.isfile(file):
		try:
			with open(status_json, "r") as f:
				status = json.load(f)
			# print(f'status json file loaded: {status_json}')
		except:
			if last_status:
				status = last_status
				with open(status_json, "w") as f:
					f.write(json.dumps(status, indent=4) )
				print(f'Error in config file detected new file created and formated with last known status: {file}')
			else:
				print('File currupt:Could not get the last known status')
				exit()

	else:
		status = {"ph_up":False, "ph_down":False, "ph_monitor":False, "temp_monitor" : False}
		with open(file, "w") as f:
			f.write(json.dumps(status, indent=4) )
		print(f'{status_json} does not exit, new file created and formated')

	return status

def update_status(process_status, status_file ='./status.json', status_value = False):
	status = load_status(status_file)
	status[process_status] = status_value
	# print(status)

	with open(status_file, "w") as f:
		f.write(json.dumps(status, indent=4))

############################################################ Main Process
if __name__ == '__main__':

###### GPIO Setup
	try:
		GPIO.setwarnings(False)
		GPIO.setmode(GPIO.BCM)

		print("\nGPIO flags set")
	except:
		print('\nCould not initialize gpio pins')
		exit()

###### Import config file & start processes, Initial setup
	try:
		status = load_status(status_json)

		temp_monitor_status = status['temp_monitor']
		ph_up_status = status['ph_up']
		ph_down_status = status['ph_down']
		ph_monitor_status = status['ph_monitor']

		temp_monitor = threading.Thread(target=get_temp,daemon=True)
		ph_monitor = threading.Thread(target=get_PH,daemon=True)
		ph_up_control = threading.Thread(target = PH_up,daemon=True)
		ph_down_control = threading.Thread(target = PH_down,daemon=True)

		temp_monitor.start()
		ph_monitor.start()
		ph_up_control.start()
		ph_down_control.start()

	except:
		print('\nCould not open or create json file of the processes')
		exit()

##### Main Code
	try:
		while True:
			status = load_status(status_json, status)

			temp_monitor_status = status['temp_monitor']
			ph_up_status = status['ph_up']
			ph_down_status = status['ph_down']
			ph_monitor_status = status['ph_monitor']

			print(status)

			time.sleep(refresh_rate)

			if not temp_monitor.is_alive():
				temp_monitor = threading.Thread(target=get_temp,daemon=True)
				temp_monitor.start()
			if not ph_monitor.is_alive():
				ph_monitor = threading.Thread(target=get_PH,daemon=True)
				ph_monitor.start()
			if not ph_up_control.is_alive():
				ph_up_control = threading.Thread(target = PH_up,daemon=True)
				ph_up_control.start()
			if not ph_down_control.is_alive():
				ph_down_control = threading.Thread(target = PH_down,daemon=True)
				ph_down_control.start()
	except:
		print('\nDone!')
		GPIO.cleanup()
