import henmanager.rcontrol as rc
from henmanager import daemonizer
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
    parser.add_argument('mode', type=str, help="Mode : capture (c) or draw (d)")
    parser.add_argument('values', type=str, help="File path where the values are stored")
    parser.add_argument('-p', '--plot', type=str, help="Path where the plot will be saved")
    args = parser.parse_args()
    curtime=time.localtime()
    
    # Capture mode
    if args.mode == "c":
        i2c = busio.I2C(board.SCL, board.SDA)
        ina219 = adafruit_ina219.INA219(i2c)
        voltage_logging(ina219, args.values)
    
    #Draw mode
    if args.mode == "d":
        import matplotlib.pyplot as plt
        from matplotlib.lines import Line2D
        import numpy as np
        
        values = {'time': [], 'volt': [], 'amp': []}
        with open(args.values + "battery-{}-{}.csv".format(curtime.tm_mon, curtime.tm_mday), 'r') as log:
            lines = log.readlines()
            for line in lines:
                line = line.split(",")
                digitime = float(line[0]) + (float(line[1]) / 60)
                values['time'].append(digitime)
                values['volt'].append(float(line[2]))
                values['amp'].append(float(line[3]))

        mint = min(values['time'])
        maxt = max(values['time'])
        minvolt = min(values['volt'])
        maxvolt = max(values['volt'])

        # Plot processing
        fig = plt.figure()
        ax1 = fig.add_subplot(111)
        
        #Voltage
        axvolt = ax1.plot(values['time'], values['volt'], 'r-', label="Voltage batterie")
        ax1.set_xlabel("Heure de la journée")
        ax1.set_ylabel("Volt", color='r')
        #ax1.set_ylim(bottom=minvolt, top=maxvolt)
        ax1.set_title("Batterie du poulailler le {}/{}/{}".format(curtime.tm_mday, curtime.tm_mon, curtime.tm_year))
        
        if maxt >= 12:
            ax1.xaxis.set_ticks(np.arange(0, maxt, step=round(maxt/12)))
        else:
            import math
            ax1.xaxis.set_ticks(np.arange(0, maxt, step=math.ceil(maxt/12)))

        #Courant
        ax2 = ax1.twinx()
        axamp = ax2.plot(values['time'], values['amp'], 'b-', label='Consommation')
        ax2.set_ylabel('Intensite (mA)', color='b')
        ax2.tick_params('y', colors='b')
        ax2.set_ylim(bottom=0, top=1000)
       
        plotname = "vplot-{}-{}.png".format(curtime.tm_mon, curtime.tm_mday)
        plt.savefig(args.plot + plotname, dpi=400, facecolor='xkcd:light grey')
        
        exit(0) 
