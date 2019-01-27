import signal
import sys
import RPi.GPIO as GPIO


class DaemonKiller:
    def __init__(self):
        signal.signal(signal.SIGINT, self.kill_daemon)
        signal.signal(signal.SIGTERM, self.kill_daemon)

    def kill_daemon(self, signum, frame):
        GPIO.cleanup()
        sys.exit(0)
