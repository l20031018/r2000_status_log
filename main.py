import schedule
import time

import configparser
import json
from datetime import datetime
import sys
if sys.version_info.major == 3:
    py_version = 3
    import urllib.request
else:
    py_version = 2
    import urlib2


def job(arg):
    print("I'm working..." + arg)


def create_url(ip, l):
    head = "http://" + ip + "/cmd/set_parameter?"
    paras = ''
    for i in l:
        paras += i[0] + '=' + i[1] + '&'
    return head + paras[:-1]


def set_para():
    global ip, l, py_version
    print(create_url(ip, l))
    print('sending command')
    if py_version == 3:
        response = urllib.request.urlopen(create_url(ip, l))
    else:
        response = urllib2.urlopen(create_url(ip, l))
    j = response.read()
    result = json.loads(j)
    if result["error_code"] == 0 and result["error_text"] == 'success':
        print('set parameter success')
    else:
        print('set parameter fail')


def log_fun(texts):
    with open('logfile.txt', 'a') as f:
        f.write(datetime.now().strftime('%Y-%m-%d %H:%M:%S') + ':   ' + texts + '\n')


def log_status():
    global ip, l, py_version
    request_status = 'http://' + ip + '/cmd/get_parameter?list=status_flags'
    if py_version == 3:
        response = urllib.request.urlopen(request_status)
    else:
        response = urllib2.urlopen(request_status)
    j = response.read()
    result = json.loads(j)
    b1 = result["status_flags"]
    #print(b1)
    if b1 & 0x01 == 1:
        log_fun('System is initializing, valid scan data not available yet')
    if b1 & 0x02 == 1:
        log_fun('Scan data output is muted by current system configuration')
    if b1 & 0x04 == 1:
        log_fun('Current scan frequency does not match set value')
    if b1 & 0x80 == 1:
        log_fun('device_warning')
    if b1 & 0x200 == 1:
        log_fun('Current internal temperature below 0 degree')
    if b1 & 0x400 == 1:
        log_fun('Current internal temperature above 80 degree')
    if b1 & 0x800 == 1:
        log_fun('sensor CPU overload is imminent')
    if b1 & 8000 == 1:
        log_fun('device_error ')
    if b1 & 0x20000 == 1:
        log_fun('Current internal temperature below -10 degree')
    if b1 & 0x40000 == 1:
        log_fun('Current internal temperature above 85 degree')
    if b1 & 0x80000 == 1:
        log_fun('CPU is in overload')
    log_fun('status:  ' + str(b1) + '\n')


def log_temperature():
    global ip, l, py_version
    request_temperature = 'http://' + ip + '/cmd/get_parameter?list=temperature_current'
    if py_version == 3:
        response = urllib.request.urlopen(request_temperature)
    else:
        response = urllib2.urlopen(request_temperature)
    j = response.read()
    result = json.loads(j)
    b1 = result["temperature_current"]
    log_fun(('temperature = ' + str(b1)))


conf = configparser.ConfigParser()
conf.read('config.ini')
f_type = conf.get('option', 'filter_type')
ip = conf.get('ip_address', 'ip')
l = conf.items(f_type)
schedule.every(0.1).minutes.do(log_temperature)
schedule.every(0.05).minutes.do(log_status)


while True:
    schedule.run_pending()
    time.sleep(1)
