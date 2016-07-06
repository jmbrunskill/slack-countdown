#!/usr/bin/python
from flask.ext.script import Manager
from flask import Flask
from datetime import datetime,timedelta
import json
import os
import requests

app = Flask(__name__)


manager = Manager(app)

"""Creates web app to be deployed on Heroku."""

SLACK_URL = os.environ.get('SLACK_URL')
if not SLACK_URL:
    print("Missing environment variable SLACK_URL")
    exit(1)

def days_from_christmas():
    """Calculates the number of days between the current date and the next
    Christmas. Returns the string to displayed.
    """
    currentdate = datetime.now()
    christmas = datetime(datetime.today().year, 12, 25)
    if christmas < currentdate:
        christmas = date(datetime.today().year + 1, 12, 25)
    delta = christmas - currentdate
    days = delta.days
    if days == 1:
        return "%d day from the nearest Christmas" % days
    else:
        return "%d days from the nearest Christmas" % days


def days_from_date(strdate):
    """ Returns the number of days between strdate and today. Add one to date
    as date caclulate is relative to time
    """
    currentdate = datetime.today()
    futuredate = datetime.strptime(strdate, '%Y-%m-%d')
    delta = futuredate - currentdate
    return delta.days + 1

def weekdays_from_date(strdate):
    """ Returns the number of week days between strdate and today. Add one to date
    as date caclulate is relative to time
    """

    currentdate = datetime.today()
    futuredate = datetime.strptime(strdate, '%Y-%m-%d')
    delta = timedelta(days=1)
    diff = 0
    weekend = set([5, 6])

    while currentdate <= futuredate:
        if currentdate.weekday() not in weekend:
            diff += 1
        currentdate += delta

    return diff


def events(strdate,event,weekdays):
    """ Returns string to be displayed with the event mentioned. Sends an error
    if date is incorrect
    """

    days = days_from_date(strdate)
    if weekdays:
        days = weekdays_from_date(strdate)

    weekday_str = ""
    if weekdays:
        weekday_str = "week"

    assert (days >= -2), "Date needs to be in the future"
    if days == -1:
        return "%d %sday since %s" % (1,weekday_str,event)
    elif days == -2:
        return "%d %sdays since %s" % (2,weekday_str,event)
    elif days == 1:
        return "%d %sday until %s" % (days,weekday_str,event)
    else:
        return "%d %sdays until %s" % (days,weekday_str,event)


def date_only(strdate,weekdays):
    """ Returns string to be displayed. Sends error message if date is
    in the past
    """
    days = weekdays_from_date(strdate) if weekdays else days_from_date(strdate)
    weekday_str = "week" if weekdays else  ""

    assert (days >= -2), "Date needs to be in the future"
    futuredate = datetime.strptime(strdate, '%Y-%m-%d')
    if days == -1:
        return "%d %sday since %s" % (1, weekday_str, futuredate.strftime("%d %B, %Y"))
    if days == -2:
        return "%d %sdays since %s" % (days,weekday_str, futuredate.strftime("%d %B, %Y"))
    if days == 1:
        return "%d %sday until %s" % (days,weekday_str, futuredate.strftime("%d %B, %Y"))
    else:
        return "%d %sdays until %s" % (days,weekday_str, futuredate.strftime("%d %B, %Y"))



def post(out):
    """ Posts a request to the slack webhook. Payload can be customized
    so the message in slack is customized. The variable out is the text
    to be displayed.
    """

    payload = {
        "attachments": [
            {
                "title": "COUNTDOWN!",
                "text": out,
                "color": "#7CD197"
            }
        ]
    }

    r = requests.post(SLACK_URL, data=json.dumps(payload))


def post_error():
    """Sends error message in Slack to alert the user
    about the incorrect date argument
    """

    payload = {
        "attachments": [
            {
                "title": "Error",
                "text": ("Date entered must be in the future. "
                        "\n Go to the <https://heroku.com|Heroku Scheduler> for you app and edit"
                        " the command"),
                        "color": "#525162"
            }
        ]
    }

    r = requests.post(SLACK_URL, data=json.dumps(payload))


@manager.option("-d", "--deadline", dest="date",
                      help="Specify the deadline in ISO format: yyyy-mm-dd",
                      metavar="DEADLINE")
@manager.option("-e", "--event", dest="event",
                      help="Name of the deadline event",metavar="EVENT")
@manager.option("-w", "--weekdays", dest="weekdays", default=False,
                      help="Only include weekdays")

def deadline(date,event, weekdays):
    """ Method takes two optional arguments. Displays in slack channel
    the number of days till the event. If no arguments are given,
    the number of days till Christmas is displayed.
    """
    try:
        result = ""
        if date:
            if event:
                result = events(date, event, weekdays)
            else:
                result = date_only(date,weekdays)
        else:
            result = days_from_christmas()
    except:
        #print("ERROR")
        post_error()
    else:
        #print(result)
        post(result)



@manager.command
def initiate():
    payload = { "text": "App is now connected to your Slack Channel."}
    r = requests.post(SLACK_URL, data=json.dumps(payload))




if __name__ == "__main__":
    manager.run()
