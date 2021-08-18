from water_tools import monitors
import time



if __name__ == '__main__':


    temp_monitor = monitors.TempMonitor()

    temp_monitor.start()

    try:
        while True:
            time.sleep(1)
    except:
        temp_monitor.stop()
