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
