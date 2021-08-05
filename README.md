# PH control

## Raspberry Drivers and library setup

- https://www.waveshare.com/wiki/Libraries_Installation_for_RPi

### Update system
- cd
- sudo apt update
- sudo apt list --upgradeable
- sudo apt ugrade
- sudo apt autoremove


### System libraries
- sudo apt-get install wiringpi
- wget https://project-downloads.drogon.net/wiringpi-latest.deb
- sudo dpkg -i wiringpi-latest.deb
- gpio -v
- sudo apt-get install libopenjp2-7 -y
- sudo apt-get install libatlas-base-dev -y
- sudo apt install libtiff -y
- sudo apt install libtiff5 -y
- sudo apt-get install -y i2c-tools

### Install virtualenv
- sudo apt install python3-pip
- sudo pip3 install virtualenv

### Create, activate virtualenv and install pip libraries
- virtualenv env
- source env/bin/activate
- pip install -r requirements.txt

### Alternatively, Manually install pip libraries
- pip install RPi.GPIO
- pip install smbus
- pip install pillow
- pip install numpy
- pip install pandas

## Hardware

- Raspberrypi 3B+
- DFRobot PH sensor V2 PRO (within the DFROBOT_PH subdirectory)
- DFRobot ADS1115 ADC unit (within the DFROBOT_PH subdirectory)

## Configuration and user control files
### ./status.json
- this file will set status of the processes: PH up, PH Down, and PH Monitoring, this file can be modified directly but serves as a file that allows for user controls
### ./config/ph-control.service
- this file runs the ph-control script as a service file on linux OS
### ./phdata.txt
-  this file saves the Calibration parameters of the DFRobot PH sensor

## Issues
- MQTT communication for UI control
- Calibration protocol
- Service file
- Logging over print statements (log files)
- json files for api

### resolved
- add temperature sensor for temperature compensation
