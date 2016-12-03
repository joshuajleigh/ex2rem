#!/usr/bin/python3.5

import datetime
import argparse
import requests
import configparser
from pytz import timezone, utc
from pyexchange import Exchange2010Service, ExchangeNTLMAuthConnection

REPORT=""
VALUES={
    "username": False,
    "password": False,
    "owa": False,
    "interval": False,
    "before": False,
    "future":False,
    "ahead": False,
    "write": False}

def args():
    """Get arguments from command line."""
    p = argparse.ArgumentParser(description="Exchange to Remind script")
    p.add_argument("--config", "-c", help="path to config file")
    p.add_argument("--future", "-f", help="how many days in the future to pull", type=int, default=30)
    p.add_argument("--before", "-b", help="how many days in the past to pull", type=int, default=15)
    p.add_argument("--interval", "-i", help="time in minutes between notifications", default=3)
    p.add_argument("--ahead", "-a", help="time in minutes, how far ahead to start warning", default=15)
    p.add_argument("--owa", "-o", type=str, help="exchange owa address")
    p.add_argument("--username", "-u", type=str, help="exchange usename in form of <domain>\\\<username>")
    p.add_argument("--password", "-p", type=str, help="exchange password")
    p.add_argument("--write", "-w", help="file to write output to")
    return p.parse_args()

def read_config_file(conf):
    """Load config from config file."""
    try:
        c = configparser.RawConfigParser()
        c.read(conf)
        return c
    except:
        return "filler"

def validate_args(arg, REPORT):
    """verify input(s) from config file and command line flags"""
    conf=read_config_file(arg.config)
    for i in VALUES:
        try:
            VALUES[i]=conf.get('config', i)
        except:
            continue

    for key, value in VALUES.items():
        if not value:
           try:
               VALUES[key]=eval('arg.{}'.format(key))
           except:
               print("something went wrong with input!")
               exit()

    if not VALUES['username']:
        REPORT+="please provide username in flag, -u whatever\n"
        REPORT+="or config file, username=whatever\n"
    if not VALUES['password']:
        REPORT+="please provide password in flag, -p password\n"
        REPORT+="or config file, password=whatever\n"
    if not VALUES['owa']:
        REPORT+="please provide owa url in flag, -o whatever\n"
        REPORT+="or config file, owa=whatever\n"
    if not VALUES['write']:
        REPORT+="please provide a path to file to write\n"
        REPORT+="flag -w /path/to/file\n"
        REPORT+="or config file write=/path/to/file\n"
    if not VALUES['username'] or not VALUES['password'] or not VALUES['owa'] or not VALUES['write']:
        print(REPORT)
        exit()
    return VALUES

def validateURL(URL):
    """verify the URL provided is (close) to a valid owa url"""
    try:
        request = requests.get(URL)
        if request.status_code == 200:
            print('url is a valid site, but not exchange link')
            quit()
        if request.reason == 'Unauthorized':
            global REPORT
            REPORT+="url valid - "
            return REPORT
    except(requests.exceptions.ConnectionError):
        print('Website {} not resolving'.format(URL))
        quit()
    except(requests.exceptions.MissingSchema):
        print('Invalid URL \'{}\': No schema supplied. Perhaps you meant https://{}?'.format(URL,URL))
        quit()

def getEvents(VALUES):
    """get months events from exchange and write them to file"""
    url = u'{s}'.format(s=VALUES['owa'])
    username = u'{s}'.format(s=VALUES['username'])
    password = u"{s}".format(s=VALUES['password'])
    BEFORE = VALUES['before']
    FUTURE = VALUES['future']

    try:
        connection = ExchangeNTLMAuthConnection(url=url, username=username, password=password)
        service = Exchange2010Service(connection)

        local_tz = timezone("America/Chicago")

        start = datetime.datetime.now() + datetime.timedelta(-BEFORE)
        start = local_tz.localize(start)
        start = start.astimezone(utc)

        end = datetime.datetime.now() + datetime.timedelta(FUTURE)
        end = local_tz.localize(end)
        end = end.astimezone(utc)

        eventsList = service.calendar().list_events(start=start, end=end, details=True)
        return eventsList
    except:
        print("username or password incorrect")
        print("remember username should be in form of ")
        print("-u <domain>\\\<username> or")
        print("in config file user=<domain>\\<username>")
        quit()

def convertList(eventsList, notify_start, notify_interval):
    """converts times from universal to local time"""
    local_tz = timezone("America/Chicago")
    full_calendar = ''
    for event in eventsList.events:
        start_local=event.start.astimezone(local_tz)
        stop_local=event.end.astimezone(local_tz)
        MSG=str(event.subject)
        RAW_TIME=str(start_local).split(' ')
        DATE=RAW_TIME[0]
        START_TIME=RAW_TIME[1][:-9]
        full_calendar += "REM {date} AT {start_time} +{notify_start} *{notify_interval} SCHED _sfun MSG %a %2 % {message} %\n".format(
        date=DATE, start_time=START_TIME, notify_start=notify_start, notify_interval=notify_interval, message=MSG)
    return full_calendar

def main():
    """ get args, confirm them, pull calendar data, write to a file"""
    ARGS=args()
    VALUES=validate_args(ARGS, REPORT)
    validateURL(VALUES['owa'])
    list_of_events=getEvents(VALUES)
    new_calendar=convertList(list_of_events, VALUES['ahead'], VALUES['interval'])
    print(REPORT + "replication complete " + str(datetime.datetime.now()))

    with open(VALUES['write'],'w+') as f:
        f.write(new_calendar)


main()
