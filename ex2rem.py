#!/usr/bin/python3

import argparse
import configparser
import requests
import datetime
import exchangelib

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
    p.add_argument("--username", "-u", type=str, help="exchange usename")
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
        print("did not read a config file, is {} a file?".format(conf))
        return "filler"

def validate_args(arg, REPORT):
    """verify input(s) from config file and command line flags"""
    conf=read_config_file(arg.config)
    for i in VALUES:
        try:
            VALUES[i]=conf.get('ex2rem', i)
#            print("found value {}".format(i))
        except:
#            print("did not find value for {}".format(i))
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
    endpoint = "http://" + URL
    try:
        request = requests.get(endpoint)
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
    url = VALUES['owa']
#    print(url)
    username = VALUES['username']
    password = VALUES['password']
    BEFORE = VALUES['before']
    FUTURE = VALUES['future']

    try:
        credentials = exchangelib.Credentials(username=username, password=password)
        config = exchangelib.Configuration(server=url, credentials=credentials)
        account = exchangelib.Account(primary_smtp_address=username, credentials=credentials, config=config)

        tz = exchangelib.EWSTimeZone.localzone()
        right_now = tz.localize(exchangelib.EWSDateTime.now())

        start = right_now - datetime.timedelta(days=7)
#        print(start)
        end = right_now + datetime.timedelta(days=7)
#        print(end)

        allEvents = account.calendar.view(start=start, end=end)
#        for item in allEvents:
#            local_start = item.start.astimezone(tz=tz)
#            local_end = item.end.astimezone(tz=tz)
#            print("{} start={} end={}".format(item.subject, local_start, local_end))

        return allEvents
    except:
        print("username or password incorrect")
        print("remember username should be in form of ")
        print("-u <domain>\\\<username> or")
        print("in config file user=<domain>\\<username>")
        quit()

def convertList(allEvents, notify_start, notify_interval):
    """converts times from universal to local time"""
    full_calendar = ''
    tz = exchangelib.EWSTimeZone.localzone()
    for item in allEvents:
#        print(item.subject)
        local_start = item.start.astimezone(tz=tz)
        MSG=str(item.subject)
        RAW_TIME=str(local_start).split(' ')
        DATE=RAW_TIME[0]
        START_TIME=RAW_TIME[1][:-9]
        full_calendar += "REM {date} AT {start_time} +{notify_start} *{notify_interval} SCHED _sfun MSG {message} %1\n".format(date=DATE, start_time=START_TIME, notify_start=notify_start, notify_interval=notify_interval, message=MSG)
    print(full_calendar)
    return full_calendar

def main():
    """ get args, confirm them, pull calendar data, write to a file"""
    ARGS=args()
#    print(ARGS)
    VALUES=validate_args(ARGS, REPORT)
    validateURL(VALUES['owa'])
    getEvents(VALUES)
    list_of_events=getEvents(VALUES)
    new_calendar=convertList(list_of_events, VALUES['ahead'], VALUES['interval'])
    print(REPORT + "replication complete " + str(datetime.datetime.now()))

    with open(VALUES['write'],'w+') as f:
        f.write(new_calendar)


main()
