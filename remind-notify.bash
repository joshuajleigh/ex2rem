#!/bin/env bash
#starts a remind desktop notification system

#sets notification command
NOTIFYCOM=notify-send

# set the location of remind file
REMINDFILE=/home/<user>/.reminders

export DISPLAY=:0
export XAUTHORITY=/home/<user>/.Xauthority

remind -z -k"$NOTIFYCOM %s &" $REMINDFILE
