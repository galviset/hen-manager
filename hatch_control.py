import time
import RPi.GPIO as GPIO
import temperature_log as tl
import argparse
from henmanager import rcontrol as rc
from henmanager import daemonizer


if __name__ == "__main__":
    """
    This script control the hatch by opening it and closing it by using sunrise and sunset time.
    """
    daemonizer.DaemonKiller.handle()

    parser = argparse.ArgumentParser()
    parser.add_argument('offset', type=int, help="Offset time from the sunrise and sunset. Setting 30 will delay hatch opening and closing by 30 minutes.")
    args = parser.parse_args()

    weather_data = tl.get_openweather_cond(city_id=***REMOVED***, api_key="***REMOVED***")
    curday = time.localtime().tm_mday
    sunrise = time.localtime(weather_data['sunrise'])
    sunset = time.localtime(weather_data['sunset'])

    GPIO.setmode(GPIO.BOARD)
    # Motor control (0:up 1:down)
    motor = rc.Device("motor", 40, 38)

    while True:
        curtime = time.localtime()
        # Reset at midnight
        if curday != curtime.tm_mday :
            curday = curtime.tm_mday
            weather_data = tl.get_openweather_cond(city_id=***REMOVED***, api_key="***REMOVED***")
            print("Refreshing OpenWeather data")

            # Get sunrise and sunset time
            sunrise = time.localtime(weather_data['sunrise'])
            sunset = time.localtime(weather_data['sunset'])      
        
        # Check time
        if curtime.tm_hour == sunrise.tm_hour :
            if curtime.tm_min == sunrise.tm_min :
                time.sleep(args.offset*60)
                motor.enable(1)
                time.sleep(4)
                motor.disable(1)
                print("Hatch opened")

        if curtime.tm_hour == sunset.tm_hour:
            if curtime.tm_min == sunset.tm_min:
                time.sleep(args.offset*60)
                motor.enable(0)
                time.sleep(5)
                motor.disable(0)
                print("Hatch closed")

        time.sleep(60)

