from henmanager import rcontrol as rc
from henmanager import daemonizer
from picamera import PiCamera
import RPi.GPIO as GPIO
import argparse
import os
import time


def get_time():
    fulltime = time.localtime()
    return '{}-{}-{}-{}-{}'.format(fulltime.tm_mon, fulltime.tm_mday, fulltime.tm_hour,
                                   fulltime.tm_min, fulltime.tm_sec)


def start_monitor(logfile, detect, led):
    led.disable()
    while True:
        time.sleep(0.01)
        movement = detect.get_data()
        if movement == 1:
            logfile.write(get_time() + 'Movement detected\n')
            led.enable()
            for sec in range(1, 10):
                camera.capture(args.pic+'img'+get_time()+'.jpg')
                time.sleep(1)
            led.disable()


if __name__ == '__main__':
    daemonizer.DaemonKiller.handle()

    # Main script for monitoring chicken movements and image capture
    parser = argparse.ArgumentParser()
    parser.add_argument('log', type=str, help="log file path", default=os.getenv("HOME")+"/hatch.log")
    parser.add_argument('pic', type=str, help="where the pictures will be stored", default=os.getenv("HOME"))
    args = parser.parse_args()

    # GPIO setup
    # GPIO.setwarnings(False)
    GPIO.setmode(GPIO.BOARD)

    # Devices
    light = rc.Device("light", 36)

    # Sensors
    pir = rc.Sensor(11)

    # Set up the camera
    camera = PiCamera()

    log = open(args.log, 'w')

    start_monitor(log, pir, light)
