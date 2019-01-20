import RPi.GPIO as GPIO

class Device():

    def __init__(self, label, pin=0):
        """
        Add a controllable device plugged on a relay.
        :param label: name of the device (string)
        :param pin: GPIO pin number (int)
        """
        self.name = label
        self.relay = Relay(pin)

    def enable(self, rl=None):
        self.relay.activate()

    def disable(self, rl=None):
        self.relay.deactivate()

class MultipleRelaysDevice(Device):

    def __init__(self, label, pins):
        """
        Add a device controllable through several relays.
        :param label: name of the device (string)
        :param pins: GPIO pins numbers (tuple of int)
        """
        super().__init__(label)
        self.relays = []
        for pin in pins:
            self.relays.append(Relay(pin))

    def enable(self, rl=None):
        self.relays[rl].activate()

    def disable(self, rl=None):
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
        GPIO.output(self.pin, 1)
        self.on = True

    def deactivate(self):
        GPIO.output(self.pin, 0)
        self.on = False

class Sensor():

    def __init__(self, p):
        self.pin = p
        GPIO.setup(self.pin, GPIO.IN)

    def get_data(self):
        return GPIO.input(self.pin)