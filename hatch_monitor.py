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

def start_monitor(logfile):
    while True:
        movement = pir.get_data()
        if movement == 1:
            logfile.write(get_time() + 'Movement detected')
            for sec in range(1, 5):
                camera.capture(args['pic']+'img'+get_time()+'.jpg')
                time.sleep(1)

if __name__ == '___main__':
    daemon = daemonizer.DaemonKiller
    #Main script for monitoring chicken movements and image capture
    parser = argparse.ArgumentParser()
    parser.add_argument('log', type=str, help="log file path", default=os.getenv("HOME")+"/hatch.log")
    parser.add_argument('pic', type=str, help="where the pictures will be stored", default=os.getenv("HOME"))
    args = parser.parse_args()

    #Devices
    light = rc.Device("light", 36)

    #Sensors
    pir = rc.Sensor(11)

    #Set up the camera
    camera = PiCamera()
    camera.rotation = 180

    #GPIO setup
    GPIO.setwarnings(False)
    GPIO.setmode(GPIO.BOARD)

    log = open(args['log'], 'w')

    start_monitor(log)
