#!/bin/env bash
#starts a remind desktop notification system

#sets notification command
NOTIFYCOM=notify-send

# set the location of remind file
REMINDFILE=/home/jleigh/.reminders

export DISPLAY=:0
export XAUTHORITY=/home/jleigh.Xauthority

remind -z -k"$NOTIFYCOM %s &" $REMINDFILE
