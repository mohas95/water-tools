import sys
sys.path.append('./DFRobot')

import RPi.GPIO as GPIO
import time
import json
import os.path

from DFRobot_ADS1115 import ADS1115
from DFRobot_PH import DFRobot_PH

import threading

################################################## Define RPI Pins
ph_up = 26 # Relay_Ch1 = 26
ph_down = 20 # Relay_Ch2 = 20
# Relay_Ch3 = 21
ph_probe_ADC = 0 #Analog 0 pin on the as1115 ADC

################################################# Define Global variables
margin = 0.5
high_ph_thresh = 8 + margin
low_ph_thresh = 7 - margin
dose_delay_time = 60
dose_on_time = 5
temperature = 25
PH = None
retry_count = 10
AS1115_I2C_ADR = 0x48
ph_up_status = None
ph_down_status = None
ph_monitor_status = None
status_json = './status.json'

ADS1115_REG_CONFIG_PGA_6_144V        = 0x00 # 6.144V range = Gain 2/3
ADS1115_REG_CONFIG_PGA_4_096V        = 0x02 # 4.096V range = Gain 1
ADS1115_REG_CONFIG_PGA_2_048V        = 0x04 # 2.048V range = Gain 2 (default)
ADS1115_REG_CONFIG_PGA_1_024V        = 0x06 # 1.024V range = Gain 4
ADS1115_REG_CONFIG_PGA_0_512V        = 0x08 # 0.512V range = Gain 8
ADS1115_REG_CONFIG_PGA_0_256V        = 0x0A # 0.256V range = Gain 16

################################################# Process Functions

def PH_up():
	'''
	'''
	global PH
	global ph_up
	global low_ph_thresh
	global dose_delay_time
	global dose_on_time
	global retry_count
	global ph_up_status
	success = None
	count = 0

	while ph_up_status:
		### GPIO Setup
		while success==None:
			try:
				GPIO.setup(ph_up,GPIO.OUT)
				GPIO.output(ph_up, GPIO.HIGH)
				print('\n[PH+]: Initialized PH up doser')
				success = 1
			except:
				print('\n[PH+]: ERROR Initializing PH up doser')
				pass

		### Process
		while True:
			while PH:
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
					count += 1
					tries_left = retry_count-count
					print(f'[PH+]: ERROR in PH Up control, will try {tries_left} more times')

					if count >= retry_count:
						print("[PH+]: Exceeded the number of retries, closing process... attempting to restart process")
						thread.exit()
					else:
						pass

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
	success = None
	count = 0

	while ph_down_status:
		### GPIO Setup
		while success==None:
			try:
				GPIO.setup(ph_down,GPIO.OUT)
				GPIO.output(ph_down, GPIO.HIGH)
				print('\n[PH-]: Initialized PH down doser')
				success = 1
			except:
				print('\n[PH-]: ERROR Initializing PH down doser')
				pass

		### Process
		while True:
			while PH:
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
					count += 1
					tries_left = retry_count-count
					print(f'[PH-]: ERROR in PH down control, will try {tries_left} more times')

					if count >= retry_count:
						print("[PH-]: Exceeded the number of retries, closing process... attempting to restart process")
						thread.exit()
					else:
						pass


def get_PH():
	'''
	'''
	global ph_probe_ADC
	global temperature
	global PH
	global retry_count
	global AS1115_I2C_ADR
	global ph_monitor_status
	success = None
	count = 0

	while ph_monitor_status:
		print(ph_monitor_status)
		### Sensor Setup
		while success == None and ph_monitor_status:
			try:
				ads1115 = ADS1115() #instantiate as1115 ADC I2X Unit
				ph = DFRobot_PH() # instantiate PH Probe

				ads1115.setAddr_ADS1115(AS1115_I2C_ADR) # set the I2C Address to 0x48
				ads1115.setGain(ADS1115_REG_CONFIG_PGA_6_144V)

				ph.reset()
				ph.begin()

				print("\n[PH monitor]: PH Sensor Set up Successful")
				success = 1

			except:
				print("[PH monitor]: Error Initializing PH Probe")
				pass

		### Process
		while ph_monitor_status:
			try:
				#Get the Digital Value of Analog of selected channel
				ph_voltage = ads1115.readVoltage(ph_probe_ADC)
				#Convert voltage to PH with temperature compensation
				print('[PH monitor]: PH Voltage: {}, Temperature: {} ----> '.format(ph_voltage['r'],temperature), end = '')
				PH = ph.readPH(ph_voltage['r'],temperature)
				print("PH:{}".format(PH))
				time.sleep(1.0)
			except:
				PH = None
				count += 1
				tries_left = retry_count-count
				print(f'[PH monitor]: ERROR trying to Get PH data from the sensor, will try {tries_left} more times')

				if count >= retry_count:
					print("[PH monitor]: Exceeded the number of retries, closing process... attempting to restart process")
					thread.exit()
				else:
					pass


if __name__ == '__main__':

###### GPIO Setup
	try:
		GPIO.setwarnings(False)
		GPIO.setmode(GPIO.BCM)

		print("\nGPIO flags set")
	except:
		print('\nCould not initialize gpio pins')
		exit()

###### Import config file & start processes
	try:
		if os.path.isfile(status_json):
			with open(status_json, "r") as f:
				status = json.load(f)
			print(f'status json file loaded: {status_json}')
		else:
			status = {"ph_up":False, "ph_down":False, "ph_monitor":False}
			with open(status_json, "w") as f:
				f.write(json.dumps(status, indent=4) )
			print(f'{status_json} does not exit, new file created and formated')


		ph_up_status = status['ph_up']
		ph_down_status = status['ph_down']
		ph_monitor_status = status['ph_monitor']

		ph_monitor = threading.Thread(target=get_PH,daemon=True)
		ph_up_control = threading.Thread(target = PH_up,daemon=True)
		ph_down_control = threading.Thread(target = PH_down,daemon=True)

		ph_monitor.start()
		ph_up_control.start()
		ph_down_control.start()

	except:
		print('\nCould not open or create json file of the processes')
		exit()

##### Main Code

	while True:

		with open(status_json, "r") as f:
			status = json.load(f)

		ph_up_status = status['ph_up']
		ph_down_status = status['ph_down']
		ph_monitor_status = status['ph_monitor']

		print(status)
		time.sleep(2)

		if not ph_monitor.is_alive():
			ph_monitor = threading.Thread(target=get_PH)
			ph_monitor.start()
		if not ph_up_control.is_alive():
			ph_up_control = threading.Thread(target = PH_up)
			ph_up_control.start()
		if not ph_down_control.is_alive():
			ph_down_control = threading.Thread(target = PH_down)
			ph_down_control.start()
