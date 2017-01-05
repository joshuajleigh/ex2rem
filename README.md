# ex2rem
exchange to remind calendar tools

Want a calendar, but not more gui?
[Remind](https://github.com/hoijui/Remind) is great!

But I'm stuck in an exchange world!
ex2rem.py will query your exchange server, and convert that ugliness into the a much happier remind format.

ical2rem.py will convert an ical file to remind format if for some reason that works better for you.

The config file for ex2rem will need the following format
```
[config]
username=<domain>\<username>
password=<your password>
write=<the output file path>
owa=<your exchange owa address> (often https://owa.domain/EWS/Exchange.asmx)
```

Additionally I've included
* ex2rem.service - a systemd example file to run the service with naked vars
* ex2rem.timer - a timer for said systemd service
* exchange2reminder.service - a systemd example file using the config file
* exchange2reminder.timer - another timer ^
* [calendar](https://github.com/yggi49/obdaRemind/blob/master/obdaRemind.py) - a stolen python script to view remind calender in ncurses
* remind-notify - a bash script to get desktop notifications for said calendar events
* remind.service - a failed attempt to setup desktop notifications via systemd vs a bash startup file (If you can figure out how to make it work please let me know!)
* testsend.bash - something I used to send desktop notifications while writing this, maybe helpful if you want to tinker with this stuff more
