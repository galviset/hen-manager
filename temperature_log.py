import henmanager.rcontrol as rc
from henmanager import daemonizer
import argparse
import os
import time
import RPi.GPIO as GPIO
import urllib.request
import json


def get_openweather_cond(city_id, api_key):
    """
    Get the current weather data from openweather API
    :return: dictionary with keys : temp, hum
    """
    openweather_url = 'https://api.openweathermap.org/data/2.5/' \
                      'weather?id={}&APPID={}&units=metric'.format(city_id, api_key)
    weather_data = json.loads((urllib.request.urlopen(openweather_url).read().decode("utf-8")))
    ext_data = {"temp": weather_data['main']['temp'], "hum": weather_data['main']['humidity']}

    return ext_data


def fan_control_tresholds(high_temp, high_hum, low_hum, temp, hum, ext_hum, fan_file, temp_priority=True):
    with open(fan_file, 'w') as fanstate:
        if temp_priority:
            if temp > high_temp:
                fanstate.write("on")
            elif hum > high_hum > ext_hum:
                fanstate.write("on")
            elif ext_hum > high_hum:
                fanstate.write("off")
            elif hum < low_hum:
                fanstate.write("off")


if __name__ == '__main__':
    """
    Capture temperature and humidity. When the day is over, it create a graph.
    Capture mode will write the current temperature and humidity into a file.
    Draw mode will write the last 24h values into a graph.
    
    Call this script in capture mode frequently in the day then call it in draw mode at 00:00 AM.
    """
    daemonizer.DaemonKiller.handle()
    curtime = time.localtime()

    parser = argparse.ArgumentParser()
    parser.add_argument('mode', type=str, help="Mode : capture (c) or draw (d)")
    parser.add_argument('values', type=str, help="File path where the values are stored")
    parser.add_argument('-p', '--plot', type=str, help="Path where the plot will be saved")
    parser.add_argument('-f', '--fan', type=str, help="Path to the file containing fan state")
    args = parser.parse_args()

    # Capture mode
    if args.mode == "c":
        GPIO.setmode(GPIO.BOARD)
        thsensor = rc.SensorDHT(22, '22')
        data = thsensor.read_data()
        ext_d = get_openweather_cond(city_id=3019875, api_key="353f254df68419e836dd7f22cd6fd6f0")
        if args.fan is None:
            args.fan = os.getenv("HOME") + "/fanstate"

        fan_control_tresholds(high_temp=28.0,
                              high_hum=70.0,
                              low_hum=60.0,
                              temp=data[1],
                              hum=data[0],
                              ext_hum=float(ext_d['hum'])+10.0,
                              fan_file=args.fan
                              )
        # # Fan control
        # if data[1] > 30.0 or data[0] > 70.0:
        #     with open(args.fan, 'w') as fanstate:
        #         fanstate.write("on")
        # elif data[0] < 55.0:
        #     with open(args.fan, 'w') as fanstate:
        #         fanstate.write("off")
        # Output data into a csv file
        with open(args.values + "values-{}-{}.csv".format(curtime.tm_mon, curtime.tm_mday), 'a') as log:
            log.write('{},{},{},{},{},{}\n'.format(
                curtime.tm_hour,
                curtime.tm_min,
                "%.2f" % data[1],
                "%.2f" % data[0],
                ext_d['temp'],
                ext_d['hum']
            ))

    # Draw mode
    elif args.mode == "d":
        import matplotlib.pyplot as plt
        from matplotlib.lines import Line2D
        import numpy as np

        values = {'time': [], 'temp': [], 'hum': [], 'extemp': [], 'exhum': []}
        with open(args.values + "values-{}-{}.csv".format(curtime.tm_mon, curtime.tm_mday), 'r') as log:
            lines = log.readlines()
            for line in lines:
                line = line.split(",")
                digitime = float(line[0]) + (float(line[1]) / 60)
                values['time'].append(digitime)
                values['temp'].append(float(line[2]))
                values['hum'].append(float(line[3]))
                values['extemp'].append(float(line[4]))
                values['exhum'].append(float(line[5]))

        mint = min(values['time'])
        maxt = max(values['time'])
        mintemp = min(values['temp'])
        maxtemp = max(values['temp'])
        minextemp = min(values['extemp'])
        maxextemp = max(values['extemp'])

        # Temperature statistics
        tempstat = ""
        tempstat += "max T° = " + str(maxtemp) + "°C\n"
        tempstat += "min T°  = " + str(mintemp) + "°C\n"
        tempstat += "deltaT° = " + str("%.2f" % (maxtemp - mintemp)) + "°C"

        fig = plt.figure()
        ax1 = fig.add_subplot(111)
        # Temperatures
        axtemp = ax1.plot(values['time'], values['temp'], 'r-', label="Temperature interne")
        axextemp = ax1.plot(values['time'], values['extemp'], 'xkcd:orange', label="Temperature locale")
        ax1.set_xlabel('Heure de la journee')
        ax1.set_ylabel('Temperature (°C)', color='r')
        ax1.tick_params('y', colors='r')
        if mintemp < minextemp: bot = mintemp
        else: bot = minextemp
        if maxtemp > maxextemp: tp = maxtemp
        else: tp = maxextemp
        ax1.set_ylim(bottom=bot, top=tp)
        ax1.set_title("Conditions du poulailler le {}/{}/{}".format(curtime.tm_mday, curtime.tm_mon, curtime.tm_year))
        hightemp = Line2D([mint, maxt], [35, 35], linewidth=0.5, linestyle='--', color='xkcd:brick red')
        ax1.add_line(hightemp)
        if maxtemp > 35:
            ax1.text(0, 35.5, "T° max reco.", fontsize=7, color='xkcd:dark red')
        if maxt>=12:
            ax1.xaxis.set_ticks(np.arange(0, maxt, step=round(maxt/12)))
        else:
            import math
            ax1.xaxis.set_ticks(np.arange(0, maxt, step=math.ceil(maxt/12)))

        # Humidities
        ax2 = ax1.twinx()
        axhum = ax2.plot(values['time'], values['hum'], 'b-', label="Humidite interne")
        axexhum = ax2.plot(values['time'], values['exhum'], 'xkcd:sky blue', label="Humidite locale")
        ax2.set_ylabel('Humidite (%)', color='b')
        ax2.tick_params('y', colors='b')
        ax2.set_ylim(bottom=0, top=100)
        highhum = Line2D([mint, maxt], [75, 75], linewidth=0.5, linestyle='--', color=(0, 0.2, 0.8, 0.2))
        lowhum = Line2D([mint, maxt], [50, 50], linewidth=0.5, linestyle='--', color=(0, 0.2, 0.8, 0.2))

        ax2.text(0, 75.5, "%H max reco.", fontsize=6, color='xkcd:grey blue')
        ax2.text(0, 50.5, "%H min reco.", fontsize=6, color='xkcd:grey blue')
        ax2.add_line(highhum)
        ax2.add_line(lowhum)

        # fig.tight_layout()
        axes = axtemp + axextemp + axhum + axexhum
        axeslabels = [l.get_label() for l in axes]
        box = ax1.get_position()
        ax1.set_position([box.x0-0.02, box.y0 + 0.15, box.width, box.height * 0.85])
        ax2.set_position([box.x0-0.02, box.y0 + 0.15, box.width, box.height * 0.85])
        plt.legend(axes, axeslabels, fontsize=7, bbox_to_anchor=(0.285, -0.13))
        statbox = plt.text(0.385 * maxt, -28, tempstat, fontsize=7,
                           bbox=dict(facecolor='w', edgecolor=(0,0,0,0.12), pad=2))

        plotname = "plot-{}-{}.png".format(curtime.tm_mon, curtime.tm_mday)
        # plt.show()
        if args.plot is None:
            args.plot = os.getenv("HOME") + "/"
        plt.savefig(args.plot + plotname, dpi=400, facecolor='xkcd:light grey')

    else:
        print("Usage : sudo python3 temperature_log.py c|d /home/user/temp.csv -p /home/user/plots/")
        exit(0)
