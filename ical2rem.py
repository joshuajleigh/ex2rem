#!/usr/bin/env python

import argparse
from icalendar import Calendar, Event, vDDDTypes
import calendar
from datetime import datetime
from pytz import UTC # timezone

time_ahead = "15"
reminder_interval = "3"

def args():
    """Get arguments from command line."""
    p = argparse.ArgumentParser(description="Script to convert ics to remind format")
    p.add_argument("--file", "-f", help="file to convert")
    return p.parse_args()

input = args()
file_to_convert = str(input.file)
g = open(file_to_convert)
gcal = Calendar.from_ical(g.read())
remcal=""

for entry in gcal.walk('VEVENT'):
    if entry.get('summary'):
        try:
            event_name = entry.get('summary')
            event_start_raw = str(vDDDTypes.from_ical(entry.get('dtstart')))
#            print( event_start_raw )
            event_start = datetime.strptime(event_start_raw[:-6], '%Y-%m-%d %H:%M:%S' )
#            print( event_start )
            month = str(calendar.month_abbr[event_start.month])
            day = str(event_start.day)
            year = str(event_start.year)
            hour = str(event_start.hour)
            minute = str(event_start.minute)
            if minute == "0":
                minute = "00"
            remcal+="REM " + month + " " + day + " " + year + " +0  AT " + hour + ":" + minute + " +" + time_ahead + " *" + reminder_interval + " SCHED _sfun MSG %a %3 %" + '"' + str(event_name) + '"' + "% \n"
            with open('remtest','w+') as f:
                f.write(remcal)
        except ValueError:
          continue

