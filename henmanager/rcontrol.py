import RPi.GPIO as GPIO
import Adafruit_DHT

class Device():

    def __init__(self, label, *args):
        """
        Add a device controlled by relay(s).
        :param label: name of the device (string)
        :param *args: GPIO pin number(s) (int)
        """
        self.name = label
        self.relays = []
        for pin in args:
            self.relays.append(Relay(pin))
        for relay in self.relays:
            relay.deactivate()

    def enable(self, rl=0):
        self.relays[rl].activate()

    def disable(self, rl=0):
        self.relays[rl].deactivate()

class Relay():

    def __init__(self, p):
        """
        :param p: GPIO pin number
        :var on: status of the relay
        """
        self.pin = p
        self.on = False
        GPIO.setup(self.pin, GPIO.OUT)

    def activate(self):
        GPIO.output(self.pin, 0)
        self.on = True

    def deactivate(self):
        GPIO.output(self.pin, 1)
        self.on = False

class Sensor():

    def __init__(self, p):
        self.pin = p
        GPIO.setup(self.pin, GPIO.IN)

    def get_data(self):
        return GPIO.input(self.pin)

class SensorDHT():

    types = { '11' : Adafruit_DHT.DHT11,
              '22' : Adafruit_DHT.DHT22,
              '2302' : Adafruit_DHT.AM2302 }

    def __init__(self, p, stype):
        """
        :param p: WARNING : use GPIO number over pin number
        :param stype: '11', '22' or '2302'
        """
        self.pin = p
        self.st = SensorDHT.types[stype]

    def read_data(self):
        """
        :return: humidity (int), temperature (int)
        """
        #Both humidity and temperature are None if read failed
        data = Adafruit_DHT.read_retry(self.st, self.pin)
        if data[0] == None:
            print("DHT read failed !")
            data = [0, 0]
        return data
