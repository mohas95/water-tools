import sys
sys.path.append('./DFRobot')

import RPi.GPIO as GPIO
import time

from DFRobot_ADS1115 import ADS1115
from DFRobot_PH import DFRobot_PH

import threading

## Define RPI Pins
ph_up = 26 # Relay_Ch1 = 26
ph_down = 20 # Relay_Ch2 = 20
# Relay_Ch3 = 21
ph_probe_ADC = 0


## Define Global variables
high_ph_thresh = 8
low_ph_thresh = 7
temperature = 25
PH = None

ADS1115_REG_CONFIG_PGA_6_144V        = 0x00 # 6.144V range = Gain 2/3
ADS1115_REG_CONFIG_PGA_4_096V        = 0x02 # 4.096V range = Gain 1
ADS1115_REG_CONFIG_PGA_2_048V        = 0x04 # 2.048V range = Gain 2 (default)
ADS1115_REG_CONFIG_PGA_1_024V        = 0x06 # 1.024V range = Gain 4
ADS1115_REG_CONFIG_PGA_0_512V        = 0x08 # 0.512V range = Gain 8
ADS1115_REG_CONFIG_PGA_0_256V        = 0x0A # 0.256V range = Gain 16

def stop_all():
	'''
	'''
	GPIO.output(ph_up, GPIO.HIGH)
	GPIO.output(ph_down, GPIO.HIGH)


def PH_up(on_time = 5):
	'''
	'''
	GPIO.output(ph_up, GPIO.LOW)
	time.sleep(on_time)
	GPIO.output(ph_up, GPIO.HIGH)

def PH_down(on_time = 5):
	'''
	'''
	GPIO.output(ph_down, GPIO.LOW)
	time.sleep(on_time)
	GPIO.output(ph_down, GPIO.HIGH)

def get_PH():
	'''
	'''
	global ph_probe_ADC
	global temperature
	global PH

	success = None

	while success == None:
		try:
			ads1115 = ADS1115()
			ph = DFRobot_PH()

			ads1115.setAddr_ADS1115(0x48)
			ads1115.setGain(ADS1115_REG_CONFIG_PGA_6_144V)

			ph.reset()
			ph.begin()

			print("\nPH Sensor Set up Successful")
			success = 1

		except:
			print("Error Initializing PH Probe")
			pass

	while True:
		try:
			#Get the Digital Value of Analog of selected channel
			ph_voltage = ads1115.readVoltage(ph_probe_ADC)
			#Convert voltage to PH with temperature compensation
			print('PH Voltage: {}, Temperature: {} ----> '.format(ph_voltage['r'],temperature), end = '')
			PH = ph.readPH(ph_voltage['r'],temperature)
			print("PH:{}".format(PH))
			time.sleep(1.0)
		except:
			PH = None
			print('ERROR trying to Get PH data from the sensor')
			exit()



if __name__ == '__main__':

###### GPIO Setup
	try:
		GPIO.setwarnings(False)
		GPIO.setmode(GPIO.BCM)

		GPIO.setup(ph_up,GPIO.OUT)
		GPIO.setup(ph_down ,GPIO.OUT)
		GPIO.output(ph_up, GPIO.HIGH) #set relay off	GPIO.output(Relay_Ch1, GPIO.HIGH) #set relay off
		GPIO.output(ph_down, GPIO.HIGH) #set relay off

		print("\nSetup of Relay Module is [success]")
	except:
		print('\nCould not initialize gpio pins')
		exit()

##### Main Code
	ph_monitor = threading.Thread(target=get_PH)
	ph_monitor.start()

	time.sleep(10)
	temperature = -5
	time.sleep(10)
	temperature = 55





	# ## Test
	#
	# GPIO.output(ph_up, GPIO.LOW) #set relay off	GPIO.output(Relay_Ch1, GPIO.HIGH) #set relay off
	# time.sleep(15)
	# GPIO.output(ph_down, GPIO.LOW) #set relay off
	# time.sleep(15)
	#
	# GPIO.output(ph_up, GPIO.HIGH) #set relay off	GPIO.output(Relay_Ch1, GPIO.HIGH) #set relay off
	# GPIO.output(ph_down, GPIO.HIGH) #set relay off
