import rcontrol as rc
import daemonizer
import time
import board
import busio
import adafruit_ina219
import argparse

def voltage_logging(ina, logfile):
    curtime = time.localtime()
    volt = float(0)
    amp = float(0)
    for i in range(0, 10):
        volt += ina.bus_voltage
        amp += ina.current
    volt = volt/10
    amp = amp/10
    with open(logfile + "battery-{}-{}.csv".format(curtime.tm_mon, curtime.tm_mday), 'a') as lf:
        lf.write('{},{},{},{}\n'.format(
            curtime.tm_hour,
            curtime.tm_min,
            "%.2f" % volt,
            "%.2f" % amp))

if __name__ == "__main__":
    daemonizer.DaemonKiller.handle()
    parser = argparse.ArgumentParser()
    parser.add_argument('values', type=str, help="File path where the values are stored")
    parser.add_argument('tick', type=int, help="Time between each measurement")
    args = parser.parse_args()
    
    while(True):
        curtime = time.localtime()
        if curtime.tm_min % args.tick != 0:
            time.sleep(60)
            continue
        i2c = busio.I2C(board.SCL, board.SDA)
        ina219 = adafruit_ina219.INA219(i2c)
        voltage_logging(ina219, args.values)
        time.sleep(60)

