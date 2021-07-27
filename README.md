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
