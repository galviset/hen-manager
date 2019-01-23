from henmanager import rcontrol as hm
from picamera import PiCamera
import argparse

if __name__ == '___main__':
    #Devices
    motor = hm.Device("visseuse", 40, 38)
    light = hm.Device("light", 36)

    #Sensors
    pir = hm.Sensor(11)
    dht = hm.SensorDHT(7, '22')

    #Set up the camera
    camera = PiCamera()
    camera.rotation = 180
