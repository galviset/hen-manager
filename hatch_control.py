import time
import RPi.GPIO as GPIO
import temperature_log as tl
import argparse
from henmanager import rcontrol as rc
from henmanager import daemonizer
import configparser
import os

def move_hatch(movetime, timeoffset, action):
    curtime = time.localtime()
    movehour = int(movetime.split(",")[0])
    movemin = int(movetime.split(",")[1])
    if curtime.tm_hour == movehour:
        if curtime.tm_min == movemin:
            time.sleep(timeoffset*60)
            if action == "open":
                motor.enable(1)
                time.sleep(4)
                motor.disable(1)
                print("Hatch opened")
            elif action == "close":
                motor.enable(0)
                time.sleep(5)
                motor.disable(0)
                print("Hatch closed")

if __name__ == "__main__":
    """
    This script control the hatch by opening it and closing it by using sunrise and sunset time.
    """
    daemonizer.DaemonKiller.handle()
    script_file = os.path.realpath(__file__)
    script_dir = script_file.split('/')
    wd = '/'
    for i in range(1, len(script_dir)-1):
        wd += script_dir[i]+'/'
    os.chdir(wd)

    #parser = argparse.ArgumentParser()
    #parser.add_argument('offset', type=int, help="Offset time from the sunrise and sunset. Setting 30 will delay hatch opening and closing by 30 minutes.")
    #args = parser.parse_args()

    config = configparser.ConfigParser()
    config.read("conf.cfg")
    ow_city = config.get('openweather', 'City_ID')
    ow_key = config.get('openweather', 'API_key')
    sun_o_c = config.get('hatch', 'sun_o_c')
    openhour = config.get('hatch', 'openhour')
    closehour = config.get('hatch', 'closehour')
    offset = config.getint('hatch', 'offset')

    weather_data = tl.get_openweather_cond(city_id=ow_city, api_key=ow_key)
    curday = time.localtime().tm_mday
    sunrise = time.localtime(weather_data['sunrise'])
    sunset = time.localtime(weather_data['sunset'])
    risetime = str(sunrise.tm_hour)+","+str(sunrise.tm_min)
    dusktime = str(sunset.tm_hour)+","+str(sunset.tm_min)

    GPIO.setmode(GPIO.BOARD)
    # Motor control (0:up 1:down)
    motor = rc.Device("motor", 40, 38)
    print("Hatch control enabled")
    if sun_o_c == "n":
        print("Manual mode")
    elif sun_o_c == "y" or sun_o_c == "o":
        print("Sunrise/Sunset mode")
        print("Sunrise : "+risetime)
        print("Sunset : "+dusktime)

    while True:
        curtime = time.localtime()
        # Reset at midnight
        if curday != curtime.tm_mday :
            curday = curtime.tm_mday
            weather_data = tl.get_openweather_cond(city_id=ow_city, api_key=ow_key)
            print("Refreshing OpenWeather data")

            # Get sunrise and sunset time
            sunrise = time.localtime(weather_data['sunrise'])
            sunset = time.localtime(weather_data['sunset'])      
            risetime = str(sunrise.tm_hour)+","+str(sunrise.tm_min)
            dusktime = str(sunset.tm_hour)+","+str(sunset.tm_min)
            print("Sunrise : "+risetime)
            print("Sunset : "+dusktime)

        # Manual mode
        '''
        if curtime.tm_hour == sunrise.tm_hour :
            if curtime.tm_min == sunrise.tm_min :
                time.sleep(offset*60)
                motor.enable(1)
                time.sleep(4)
                motor.disable(1)
                print("Hatch opened")

        if curtime.tm_hour == sunset.tm_hour:
            if curtime.tm_min == sunset.tm_min:
                time.sleep(offset*60)
                motor.enable(0)
                time.sleep(5)
                motor.disable(0)
                print("Hatch closed")
        '''
        if sun_o_c == "n":         
            move_hatch(openhour, offset, "open")
            move_hatch(closehour, offset, "close")
        elif sun_o_c == "y" or sun_o_c == "o":
            move_hatch(risetime, offset, "open")
            move_hatch(dusktime, offset, "close")

        time.sleep(60)

