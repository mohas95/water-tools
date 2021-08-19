This package provides various water monitoring tools for sensor and pump integration. At the current stage of development the package includes temperature monitor,
ph monitor, ph controller.This package uses the RPI-Control-center gpio engine as its driver to make RPI API-ification easy.
At this current stage this python package is only for the Raspberry pi and uses DFRobot sensor library as well as the ADC integration

- Documentation: *Coming soon*
- [Github](https://github.com/moha7108/water-tools)

## Installation

- pip
```shell
pip install RPi-water-tools
```
- source
```shell
git clone https://github.com/moha7108/water-tools
cd water_tools
pip install -r requirements.txt
```

## Example Usage

```python
from water_tools import monitors, ph_control
import time

if __name__ == '__main__':
    temp_monitor = monitors.TempMonitor()
    ph_monitor = monitors.PHMonitor(temperature_api_file = './api/TEMPERATURE.json')
    ph_controller = ph_control.PHController(ph_api_file='./api/PH.json', config_file='./ph_config.json', api_dir = './api/', log_dir = './logs/')

    temp_monitor.start()
    ph_monitor.start()
    ph_controller.start()

    try:
        while True:
            time.sleep(1)
    except:
        temp_monitor.stop()
        ph_monitor.stop()
        ph_controller.stop()
```

### Configuration/ API Files
- *will be updated*

## Hardware and drivers

### Hardware

- [Raspberrypi 3B+](https://www.raspberrypi.org/products/raspberry-pi-3-model-b/)
  - OS: Rasbian Buster +

### System Libraries

- [waveshare guide](https://www.waveshare.com/wiki/Libraries_Installation_for_RPi)

``` shell
cd
sudo apt update
sudo apt list --upgradeable
sudo apt ugrade
sudo apt autoremove

sudo apt-get install wiringpi
wget https://project-downloads.drogon.net/wiringpi-latest.deb
sudo dpkg -i wiringpi-latest.deb
gpio -v
sudo apt-get install libopenjp2-7 -y
sudo apt-get install libatlas-base-dev -y
sudo apt install libtiff -y
sudo apt install libtiff5 -y
sudo apt-get install -y i2c-tools
```

## Feedback

All kinds of feedback and contributions are welcome.

- [Create an issue](https://github.com/moha7108/water-tools/issues)
- Create a pull request
- Reach out to @moha7108

## Contributors

- Mohamed Debbagh
  - [GitLab](https://gitlab.com/moha7108/), [Github](https://github.com/moha7108/), [Twitter](https://twitter.com/moha7108)

## Change Log

###0.1.4
- Ph controller success flag when begin() is complete

###0.1.3
- fix error handling of ph controller

###0.1.2
- Add error handling when api is busy and parameter getters access file when they are being written to

### 0.1.0
- first working code debut
