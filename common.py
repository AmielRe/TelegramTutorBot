import requests
import datetime 
import json
from datetime import timedelta
import dateutil.parser


def hourly_it(start, finish):
    while finish > start:
        start = start + timedelta(hours=1)
        yield start
        
def splitTimeFrame(startTime, endTime):
    dt = dateutil.parser.parse(startTime)
    start = dt.strftime('%Y-%m-%d %H:%M:%S')
    startDateTime = datetime.datetime.strptime(start, "%Y-%m-%d %H:%M:%S") - timedelta(hours=1)
    dt = dateutil.parser.parse(endTime)
    end = dt.strftime('%Y-%m-%d %H:%M:%S')
    endDateTime = datetime.datetime.strptime(end, "%Y-%m-%d %H:%M:%S") - timedelta(hours=1)
    
    times = []
    for hour in hourly_it(startDateTime, endDateTime):
        times.append(hour.strftime('%d-%m-%Y %H:%M:%S'))
        
    return times
    