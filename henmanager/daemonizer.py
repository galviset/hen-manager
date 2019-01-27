import signal
import sys
import RPi.GPIO as GPIO


class DaemonKiller:
    @staticmethod
    def handle():
        signal.signal(signal.SIGINT, DaemonKiller.kill_daemon)
        signal.signal(signal.SIGTERM, DaemonKiller.kill_daemon)

    def kill_daemon(signum, frame):
        GPIO.cleanup()
        print("Exiting...")
        sys.exit(0)
