from water_tools import monitors
import time



if __name__ == '__main__':
    temp_monitor = monitors.TempMonitor()
    ph_monitor = monitors.PHMonitor(temperature_api_file = './api/TEMPERATURE.json')


    temp_monitor.start()
    ph_monitor.start()

    try:
        while True:
            time.sleep(1)
    except:
        temp_monitor.stop()
        ph_monitor.stop()
