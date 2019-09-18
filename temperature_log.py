import henmanager.rcontrol as rc
#from henmanager import daemonizer
import argparse
import os
import time
import RPi.GPIO as GPIO
import urllib.request
import json
import configparser


def get_openweather_cond(city_id, api_key):
    """
    Get the current weather data from openweather API
    :return: dictionary with keys : temp, hum
    """
    openweather_url = 'https://api.openweathermap.org/data/2.5/' \
                      'weather?id={}&APPID={}&units=metric'.format(city_id, api_key)
    weather_data = json.loads((urllib.request.urlopen(openweather_url).read().decode("utf-8")))
    ext_data = {"temp": weather_data['main']['temp'], "hum": weather_data['main']['humidity'], "sunrise": weather_data['sys']['sunrise'], "sunset": weather_data['sys']['sunset']}

    return ext_data


def fan_control_tresholds(high_temp, high_hum, low_hum, temp, hum, ext_hum, fan_file, low_temp, temp_priority=True):
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
            elif temp < low_temp:
                fanstate.write("off")


if __name__ == '__main__':
    """
    Capture temperature and humidity. When the day is over, it create a graph.
    Capture mode will write the current temperature and humidity into a file.
    Draw mode will write the last 24h values into a graph.
    
    Call this script in capture mode frequently in the day then call it in draw mode at 00:00 AM.
    """
    #daemonizer.DaemonKiller.handle()
    script_file = os.path.realpath(__file__)
    script_dir = script_file.split('/')
    wd ='/'
    for i in range(1, len(script_dir)-1):
        wd += script_dir[i]+'/'
    os.chdir(wd)

    config = configparser.ConfigParser()
    config.read("conf.cfg")
    ow_city = config.get('openweather', 'City_ID')
    ow_key = config.get('openweather', 'API_key')
    tick = config.getint('openweather', 'frequency')
    fan = config.get('main', 'fan_file')
    values = config.get('main', 'values_t_h')
    #Fan values
    temp_act = config.get('fan', 'temp_act')
    temp_deact = config.get('fan', 'temp_deact')
    hum_act = config.get('fan', 'hum_act')
    hum_deact = config.get('fan', 'hum_deact')


    parser = argparse.ArgumentParser()
    #parser.add_argument('values', type=str, help="File path where the values are stored")
    #parser.add_argument('tick', type=int, help="Time between each value collection.")
    #parser.add_argument('-f', '--fan', type=str, help="Path to the file containing fan state")
    #args = parser.parse_args()

    print("Setting up DHT sensor...")
    GPIO.setmode(GPIO.BOARD)
    thsensor = rc.SensorDHT(22, '22')
    print("Done.")
    print("Starting temperature and humidity logging")

    while(True):
        curtime = time.localtime()
        # Value time starting from the first minute of the hour (eg 0, 15, 30, 45 if tick=15) 
        if int(curtime.tm_min) % tick != 0:
            time.sleep(60)
            continue
        data = thsensor.read_data()
        try:
            ext_d = get_openweather_cond(city_id=ow_city, api_key=ow_key)
        except:
            print("Couldn't reach OpenWeather data !")
            ext_d = {"temp":0, "hum":0}
        if fan is None:
            fan = os.getenv("HOME") + "/fanstate"
        fan_control_tresholds(high_temp=temp_act,
                              high_hum=hum_act,
                              low_hum=hum_deact,
                              temp=data[1],
                              hum=data[0],
                              ext_hum=float(ext_d['hum'])+10.0,
                              fan_file=fan,
                              low_temp=temp_act
                              )
        # # Fan control
        # if data[1] > 30.0 or data[0] > 70.0:
        #     with open(args.fan, 'w') as fanstate:
        #         fanstate.write("on")
        # elif data[0] < 55.0:
        #     with open(args.fan, 'w') as fanstate:
        #         fanstate.write("off")
        # Output data into a csv file
        with open(values + "values-{}-{}.csv".format(curtime.tm_mon, curtime.tm_mday), 'a') as log:
            log.write('{},{},{},{},{},{}\n'.format(
                curtime.tm_hour,
                curtime.tm_min,
                "%.2f" % data[1],
                "%.2f" % data[0],
                ext_d['temp'],
                ext_d['hum']
            ))

        time.sleep(60)

