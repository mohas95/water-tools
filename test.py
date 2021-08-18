from water_tools import ph_control
import time



if __name__ == '__main__':


    temp_control = ph_control.TempMonitor()

    temp_control.start()

    try:
        while True:
            time.sleep(1)
    except:
        temp_control.stop()
