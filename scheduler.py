from __future__ import print_function
import datetime
import pickle
import dateutil.parser
from datetime import timedelta
import os.path
from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from common import splitTimeFrame

# If modifying these scopes, delete the file token.pickle.
# SCOPES = ['https://www.googleapis.com/auth/calendar.readonly']
SCOPES = ['https://www.googleapis.com/auth/calendar']

def placeFreeTimeSlot(timeSlot):
    """Shows basic usage of the Google Calendar API.
    Prints the start and name of the next 10 events on the user's calendar.
    """
    creds = None
    # The file token.pickle stores the user's access and refresh tokens, and is
    # created automatically when the authorization flow completes for the first
    # time.
    if os.path.exists('token.pickle'):
        with open('token.pickle', 'rb') as token:
            creds = pickle.load(token)
    # If there are no (valid) credentials available, let the user log in.
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                'credentials.json', SCOPES)
            creds = flow.run_local_server(port=0)
        # Save the credentials for the next run
        with open('token.pickle', 'wb') as token:
            pickle.dump(creds, token)

    service = build('calendar', 'v3', credentials=creds)
    
    #--------------------- Manipulating Booking Time ----------------------------
    dt = dateutil.parser.parse(timeSlot)
    start_time=dt.strftime('%Y-%m-%d')+'T'+dt.strftime('%H:%M:%S')+'+03:00'
    oneMoreHour = datetime.datetime.strptime(timeSlot, "%d-%m-%Y %H:%M:%S") + timedelta(hours=1)
    end_time=oneMoreHour.strftime('%Y-%m-%d')+'T'+oneMoreHour.strftime('%H:%M:%S')+'+03:00'
    #----------------------------------------------------------------------------
    
    # Call the Calendar API
    now = datetime.datetime.utcnow().isoformat() + 'Z' # 'Z' indicates UTC time
    print('קובע שיעור...')
    events_result = service.events().list(calendarId='primary', timeMin=now,
                                        maxResults=100, singleEvents=True,
                                        orderBy='startTime').execute()
    events = events_result.get('items', [])
    if not events:
        event = {
        'summary': 'פנוי',
        'description': "",
        'start': {
        'dateTime': start_time,
        'timeZone': 'Asia/Jerusalem',
        },
        'end': {
        'dateTime': end_time,
        'timeZone': 'Asia/Jerusalem',
        },
        'recurrence': [
        'RRULE:FREQ=DAILY;COUNT=1'
        ],
        }
        event = service.events().insert(calendarId='primary', body=event).execute()
        print ('חלון זמן נוצר: %s' % (event.get('htmlLink')))
        return True

    else:
        # --------------------- Check if there are any similar start time --------------------- 
        for event in events:
            start = event['start'].get('dateTime', event['start'].get('date'))
            if start==start_time:
                print('כבר נקבע שיעור....')
                return False
        # -------------------- Break out of for loop if there are no apppointment that has the same time ----------
        event = {
        'summary': 'פנוי',
        'description': "",
        'start': {
        'dateTime': start_time,
        'timeZone': 'Asia/Jerusalem',
        },
        'end': {
        'dateTime': end_time,
        'timeZone': 'Asia/Jerusalem',
        },
        'recurrence': [
        'RRULE:FREQ=DAILY;COUNT=1'
        ],
        }
        event = service.events().insert(calendarId='primary', body=event).execute()
        print ('חלון זמן נוצר: %s' % (event.get('htmlLink')))
        return True
    
    
def book_timeslot(booking_time,input_email,input_name):
    """Shows basic usage of the Google Calendar API.
    Prints the start and name of the next 10 events on the user's calendar.
    """
    creds = None
    # The file token.pickle stores the user's access and refresh tokens, and is
    # created automatically when the authorization flow completes for the first
    # time.
    if os.path.exists('token.pickle'):
        with open('token.pickle', 'rb') as token:
            creds = pickle.load(token)
    # If there are no (valid) credentials available, let the user log in.
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                'credentials.json', SCOPES)
            creds = flow.run_local_server(port=0)
        # Save the credentials for the next run
        with open('token.pickle', 'wb') as token:
            pickle.dump(creds, token)

    service = build('calendar', 'v3', credentials=creds)
    
    #--------------------- Manipulating Booking Time ----------------------------
    dt = dateutil.parser.parse(booking_time)
    start_time=dt.strftime('%Y-%m-%d')+'T'+dt.strftime('%H:%M:%S')+'+03:00'
    oneMoreHour = datetime.datetime.strptime(booking_time, "%d-%m-%Y %H:%M:%S") + timedelta(hours=1)
    end_time=oneMoreHour.strftime('%Y-%m-%d')+'T'+oneMoreHour.strftime('%H:%M:%S')+'+03:00'
    #----------------------------------------------------------------------------

    # Call the Calendar API
    now = datetime.datetime.utcnow().isoformat() + 'Z' # 'Z' indicates UTC time
    print('קובע שיעור...')
    events_result = service.events().list(calendarId='primary', timeMin=now,
                                        maxResults=100, singleEvents=True,
                                        orderBy='startTime').execute()
    events = events_result.get('items', [])
    if not events:
        event = {
        'summary': 'שיעור פרטי',
        'description': str("שיעור פרטי") + " עם " + str(input_name),
        'start': {
        'dateTime': start_time,
        'timeZone': 'Asia/Jerusalem',
        },
        'end': {
        'dateTime': end_time,
        'timeZone': 'Asia/Jerusalem',
        },
        'recurrence': [
        'RRULE:FREQ=DAILY;COUNT=1'
        ],
        'attendees': [
        {'email': str(input_email)},
        ],
        'reminders': {
        'useDefault': False,
        'overrides': [
            {'method': 'email', 'minutes': 24 * 60},
            {'method': 'popup', 'minutes': 10},
        ],
        },
        }
        event = service.events().insert(calendarId='primary', body=event).execute()
        print ('שיעור נוצר: %s' % (event.get('htmlLink')))
        return True

    else:
        # --------------------- Check if there are any similar start time --------------------- 
        for event in events:
            start = event['start'].get('dateTime', event['start'].get('date'))
            if start==start_time:
                print('כבר נקבע שיעור....')
                return False
        # -------------------- Break out of for loop if there are no apppointment that has the same time ----------
        event = {
        'summary': 'שיעור פרטי',
        'description': str("שיעור פרטי") + " עם " + str(input_name),
        'start': {
        'dateTime': start_time,
        'timeZone': 'Asia/Jerusalem',
        },
        'end': {
        'dateTime': end_time,
        'timeZone': 'Asia/Jerusalem',
        },
        'recurrence': [
        'RRULE:FREQ=DAILY;COUNT=1'
        ],
        'attendees': [
        {'email': str(input_email)},
        ],
        'reminders': {
        'useDefault': False,
        'overrides': [
            {'method': 'email', 'minutes': 24 * 60},
            {'method': 'popup', 'minutes': 10},
        ],
        },
        }
        event = service.events().insert(calendarId='primary', body=event).execute()
        print ('אירוע נוצר: %s' % (event.get('htmlLink')))
        return True
    
def delete_availableSlot(availableSlotTime):
    """Shows basic usage of the Google Calendar API.
    Prints the start and name of the next 10 events on the user's calendar.
    """
    creds = None
    # The file token.pickle stores the user's access and refresh tokens, and is
    # created automatically when the authorization flow completes for the first
    # time.
    if os.path.exists('token.pickle'):
        with open('token.pickle', 'rb') as token:
            creds = pickle.load(token)
    # If there are no (valid) credentials available, let the user log in.
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                'credentials.json', SCOPES)
            creds = flow.run_local_server(port=0)
        # Save the credentials for the next run
        with open('token.pickle', 'wb') as token:
            pickle.dump(creds, token)

    service = build('calendar', 'v3', credentials=creds)
    
    events_tuple = get_SplitedFreeSlotsWithEvent()
    eventToDelete = [currEvent for currEvent in events_tuple if currEvent[0] == availableSlotTime]
    
    service.events().delete(calendarId='primary', eventId=eventToDelete[0][1]['id']).execute()
    
def get_availableSlots():
    """Shows basic usage of the Google Calendar API.
    Prints the start and name of the next 10 events on the user's calendar.
    """
    creds = None
    # The file token.pickle stores the user's access and refresh tokens, and is
    # created automatically when the authorization flow completes for the first
    # time.
    if os.path.exists('token.pickle'):
        with open('token.pickle', 'rb') as token:
            creds = pickle.load(token)
    # If there are no (valid) credentials available, let the user log in.
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                'credentials.json', SCOPES)
            creds = flow.run_local_server(port=0)
        # Save the credentials for the next run
        with open('token.pickle', 'wb') as token:
            pickle.dump(creds, token)

    service = build('calendar', 'v3', credentials=creds)
    
    # Call the Calendar API
    now = datetime.datetime.utcnow().isoformat() + 'Z' # 'Z' indicates UTC time
    events_result = service.events().list(calendarId='primary', timeMin=now,
                                        maxResults=100, singleEvents=True,
                                        orderBy='startTime').execute()
    events = events_result.get('items', [])
    eventsFinal = []
    for event in events:
        if event['summary']=="פנוי":
            eventsFinal.append(event)
            
    return eventsFinal

def get_SplitedFreeSlots():
    freeSlots = get_availableSlots()
    splitFreeSlots = []
    
    for slot in freeSlots:
        for currSlot in splitTimeFrame(slot['start'].get('dateTime', slot['start'].get('date')),slot['end'].get('dateTime', slot['end'].get('date'))):
            splitFreeSlots.append(currSlot)
        
    dates = []
    tempDate = []
    for currSlot in splitFreeSlots:
        tempDate.append("{0}".format(currSlot))
        dates.append(tempDate)
        tempDate = []
        
    return dates
    
def get_SplitedFreeSlotsWithEvent():
    freeSlots = get_availableSlots()
    splitFreeSlots = []
    
    for slot in freeSlots:
        for currSlot in splitTimeFrame(slot['start'].get('dateTime', slot['start'].get('date')),slot['end'].get('dateTime', slot['end'].get('date'))):
            splitFreeSlots.append((currSlot, slot))
        
    return splitFreeSlots

if __name__ == '__main__': 
    input_email='test@gmail.com'
    booking_time='14:00' 
    result=book_timeslot(booking_time,input_email)