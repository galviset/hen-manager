import argparse
import os
import time
import numpy as np

def replace_if_nan(value, replacement):
    if value == replacement:
        return np.NAN
    else:
        return value

if __name__ == '__main__':
    """
    Capture temperature and humidity. When the day is over, it create a graph.
    Capture mode will write the current temperature and humidity into a file.
    Draw mode will write the last 24h values into a graph.
    
    Call this script in capture mode frequently in the day then call it in draw mode at 00:00 AM.
    """
    curtime = time.localtime()

    parser = argparse.ArgumentParser()
    parser.add_argument('values', type=str, help="File path where the values are stored")
    parser.add_argument('-p', '--plot', type=str, help="Path where the plot will be saved")
    parser.add_argument('-f', '--fan', type=str, help="Path to the file containing fan state")
    parser.add_argument('-d', '--date', type=str, help="Choose the date (format: month-day)")
    args = parser.parse_args()

    import matplotlib.pyplot as plt
    from matplotlib.lines import Line2D

    values = {'time': [], 'temp': [], 'hum': [], 'extemp': [], 'exhum': []}
    if args.date is not None:
        valuesfile = "values-"+args.date+".csv"
    else:
        valuesfile = "values-{}-{}.csv".format(curtime.tm_mon, curtime.tm_mday)
    with open(args.values + valuesfile, 'r') as log:
        lines = log.readlines()
        for line in lines:
            line = line.split(",")
            digitime = float(line[0]) + (float(line[1]) / 60)
            values['time'].append(digitime)
            values['temp'].append(replace_if_nan(float(line[2]), 0))
            values['hum'].append(replace_if_nan(float(line[3]), 0))
            values['extemp'].append(replace_if_nan(float(line[4]), 0))
            values['exhum'].append(replace_if_nan(float(line[5]), 0))

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
    if args.date is not None:
        title = "Conditions du poulailler le "+args.date+"-"+str(curtime.tm_year)
    else:
        title = "Conditions du poulailler le {}/{}/{}".format(curtime.tm_mday, curtime.tm_mon, curtime.tm_year)
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

    if args.date is not None:
        plotname = "plot-"+args.date+".png"
    else:
        plotname = "plot-{}-{}.png".format(curtime.tm_mon, curtime.tm_mday)
    # plt.show()
    if args.plot is None:
        args.plot = os.getenv("HOME") + "/"
    plt.savefig(args.plot + plotname, dpi=400, facecolor='xkcd:light grey')

