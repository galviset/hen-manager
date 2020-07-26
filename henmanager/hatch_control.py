import time
import RPi.GPIO as GPIO
import temperature_log as tl
import argparse
import rcontrol as rc
import daemonizer
import configparser
import os
import schedule
import math

class HatchControler():
    def __init__(self, pin_up, pin_down):
        self.pin_up = 40
        self.pin_down = 38
        #Time
        self.sunrise = None
        self.sunset = None
        #Offset
        self.offset_morning = None
        self.offset_evening = None
        self.open_time = None
        self.close_time = None

    def schedule_times(self):
        print("Opening at : "+self.open_time)
        print("Closing at :"+self.close_time)
        schedule.every().day.at(self.open_time).do(self.move_hatch, "open")
        schedule.every().day.at(self.close_time).do(self.move_hatch, "close")
        return schedule.CancelJob

    def move_hatch(self, action):
        GPIO.setmode(GPIO.BOARD)
        # Motor control (0:up 1:down)
        motor = rc.Device("motor", self.pin_up, self.pin_down)
        if action == "open":
           motor.enable(1)
           time.sleep(5)
           motor.disable(1)
           time.sleep(5)
           print("Hatch opened")
        elif action == "close":
           motor.enable(0)
           time.sleep(5)
           motor.disable(0)
           time.sleep(5)
           print("Hatch closed")
        GPIO.cleanup()
        return schedule.CancelJob

    def getOpenWeatherSun(self, owcity_id, owapi_key):
        # Get sunrise and sunset time
        print("Getting OpenWeather data")
        for i in range(0,5):
            while True:
                try:
                    weather_data = tl.get_openweather_cond(owcity_id, owapi_key)
                except:
                    continue
                break
        hatch.sunrise = time.localtime(weather_data['sunrise'])
        hatch.sunset = time.localtime(weather_data['sunset'])      
        risetime = str(self.sunrise.tm_hour)+","+str(self.sunrise.tm_min)
        dusktime = str(self.sunset.tm_hour)+","+str(self.sunset.tm_min)
        print("Sunrise : "+risetime)
        print("Sunset : "+dusktime)
        return

    def calculateControlerOffsets(self):
        results = self.calculateOffset(hatch.sunrise, hatch.offset_morning)
        hatch.open_time = "{0}:{1}".format(results[0], results[1])
        results = self.calculateOffset(hatch.sunset, hatch.offset_evening)
        hatch.close_time = "{0}:{1}".format(results[0], results[1])


    def calculateOffset(self, initial_time, offset):
        total_min = initial_time.tm_hour*60+initial_time.tm_min
        total_result = total_min + offset
        result_hour = str(math.floor(total_result/60))
        result_min = str(total_result%60)
        if len(result_hour) == 1:
            result_hour = "0"+result_hour
        if len(result_min) == 1:
            result_min = "0"+result_min
        return result_hour, result_min


if __name__ == "__main__":
    """
    This script control the hatch by opening it and closing it by using sunrise and sunset time.
    """
    daemonizer.DaemonKiller.handle()
    script_file = os.path.realpath(__file__)
    script_dir = script_file.split('/')
    wd = '/'
    for i in range(1, len(script_dir)-2):
        wd += script_dir[i]+'/'
    os.chdir(wd)

    #parser = argparse.ArgumentParser()
    #parser.add_argument('offset', type=int, help="Offset time from the sunrise and sunset. Setting 30 will delay hatch opening and closing by 30 minutes.")
    #args = parser.parse_args()

    hatch = HatchControler('40', '38')

    #Read configuration
    config = configparser.ConfigParser()
    config.read("conf.cfg")
    ow_city = config.get('openweather', 'City_ID')
    ow_key = config.get('openweather', 'API_key')
    sun_o_c = config.get('hatch', 'sun_o_c')
    openhour = config.get('hatch', 'openhour')
    closehour = config.get('hatch', 'closehour')
    hatch.offset_morning = config.getint('hatch', 'offset_morning')
    hatch.offset_evening = config.getint('hatch', 'offset_evening')

    #Initialize script
    curday = time.localtime().tm_mday
    hatch.getOpenWeatherSun(ow_city, ow_key)
    hatch.calculateControlerOffsets()
    starting_script = True

    print("Hatch control enabled")
    if sun_o_c == "y" or sun_o_c == "o":
        hatch.calculateControlerOffsets()
        schedule.every().day.at("00:01").do(hatch.getOpenWeatherSun, ow_city, ow_key)
        schedule.every().day.at("00:10").do(hatch.calculateControlerOffsets)
    while True:
        curtime = time.localtime()
        schedule.run_pending()
        if curtime.tm_mday != curday or starting_script:
            starting_script = False
            curday = curtime.tm_mday
            if sun_o_c == "n":
                print("Manual mode")
                hatch.open_time = openhour
                hatch.close_time = closehour
                hatch.schedule_times()
            elif sun_o_c == "y" or sun_o_c == "o":
                print("Sun mode")
                hatch.schedule_times()
        time.sleep(30)
