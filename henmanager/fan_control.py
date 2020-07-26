import rcontrol as rc
import daemonizer
import os
import time
import argparse
import RPi.GPIO as GPIO

if __name__ == '__main__':
    """
    Control the fan by reading the Pi environment variable HEN_FAN set by temperature_log.pi
    """
    daemonizer.DaemonKiller.handle()

    parser = argparse.ArgumentParser()
    parser.add_argument('-f', '--fan', type=str, help="Path to the file containing fan state")
    args = parser.parse_args()
    current_state = "off"
    GPIO.setmode(GPIO.BOARD)
    if args.fan is None:
        args.fan = os.getenv("HOME") + "/fanstate"

    while True:
        with open(args.fan, 'r') as fanfile:
            try:
                state = fanfile.readlines()[0]
            except:
                print("Error while reading fan state.")
                state = "off"

        if state == "on" and current_state == "off":
            #GPIO.setmode(GPIO.BOARD)
            fan = rc.Device('fan', 32)
            fan.enable()
            current_state = "on"
            print("Fan enabled.")
            #GPIO.cleanup()
        if state == "off" and current_state == "on":
            #GPIO.setmode(GPIO.BOARD)
            fan = rc.Device('fan', 32)
            fan.disable()
            current_state = "off"
            print("Fan disabled.")
            #GPIO.cleanup()
        time.sleep(120)
