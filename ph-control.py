import RPi.GPIO as GPIO
import time
import threading

## Define Global variables
ph_up = 26 # Relay_Ch1 = 26
ph_down = 20 # Relay_Ch2 = 20
# Relay_Ch3 = 21

if __name__ == '__main__':

###### GPIO Setup
	GPIO.setwarnings(False)
	GPIO.setmode(GPIO.BCM)

	GPIO.setup(ph_up,GPIO.OUT)
	GPIO.setup(ph_down ,GPIO.OUT)
	GPIO.output(ph_up, GPIO.HIGH) #set relay off	GPIO.output(Relay_Ch1, GPIO.HIGH) #set relay off
	GPIO.output(ph_down, GPIO.HIGH) #set relay off

	print("\nSetup of Relay Module is [success]")

	GPIO.output(ph_up, GPIO.LOW) #set relay off	GPIO.output(Relay_Ch1, GPIO.HIGH) #set relay off
    time.sleep(15)
    GPIO.output(ph_down, GPIO.LOW) #set relay off
    time.sleep(15)

	GPIO.output(ph_up, GPIO.HIGH) #set relay off	GPIO.output(Relay_Ch1, GPIO.HIGH) #set relay off
	GPIO.output(ph_down, GPIO.HIGH) #set relay off
