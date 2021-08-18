from rpi_control_center import GPIO_engine
from DFRobot import DFR_PH DFR_ADS1115

######## Default Configuration
default_config = {
        "1":{'name':'PH_up', 'pin':26, 'state':False},
        "2":{'name':'PH_down', 'pin':20, 'state':False}
}


########################################################### Wrapper/decorator definition function
def threaded(func):
    """start and return a thread of the passed in function. Threadify a function with the @threaded decorator"""
    def wrapper(*args, **kwargs):
        thread = threading.Thread(target=func, args=args, kwargs=kwargs, daemon=False)
        thread.start()
        return thread
    return wrapper




class PHController():
    def __init__(self):
        self.temperature = None
        self.high_thresh
        self.low_thresh
        self.up_state
        self.down_state
        self.ph_monitor_state
        self.ph
        self.up_pin = 26
        self.down_pin = 20


class TempMonitor():
    def __init__(self):
        self.state



class PHMonitor():
    def __init__(self):
        self.state









if __name__ == '__main__':

gpio_engine = GPIO_engine.BulkUpdater(
                                        config_file = './ph_config.json',
                                        api_dir = './api',
                                        default_config = default_config,
                                        refresh_rate = 1
                                        )
gpio_engine.start()





gpio_engine.stop()
