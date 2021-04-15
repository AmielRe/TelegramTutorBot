import requests
import datetime 
import json
from datetime import timedelta
import dateutil.parser
from scheduler import book_timeslot
from scheduler import get_availableSlots
from scheduler import delete_availableSlot
from scheduler import placeFreeTimeSlot
from common import hourly_it
from common import splitTimeFrame
from scheduler import get_SplitedFreeSlots
from scheduler import get_SplitedFreeSlotsWithEvent
import re
import api_key
api_key=api_key.api['api_key']
    
def check_email(email):
    regex = '^\w+([\.-]?\w+)*@\w+([\.-]?\w+)*(\.\w{2,3})+$'
    if(re.search(regex,email)):  
        print("Valid Email") 
        return True
    else:  
        print("Invalid Email")  
        return False
        
def validateDate(date_text):
    try:
        datetime.datetime.strptime(date_text, '%d-%m-%Y %H:%M:%S')
        freeSlots = get_SplitedFreeSlots()
        tempDate = []
        tempDate.append("{0}".format(date_text))
        if(tempDate in freeSlots):
            return True
        else:
            return False
    except ValueError:
        return False

def getLastMessage():
    url = "https://api.telegram.org/bot{}/getUpdates".format(api_key)
    response = requests.get(url)
    data=response.json()
    last_msg=data['result'][len(data['result'])-1]['message']['text']
    chat_id=data['result'][len(data['result'])-1]['message']['chat']['id']
    update_id=data['result'][len(data['result'])-1]['update_id']
    user_name=data['result'][len(data['result'])-1]['message']['from']['first_name']
    if len(data['result']) < 100:
        return last_msg,chat_id,update_id,user_name
    else:
        print('offseting updates limit...')
        url = "https://api.telegram.org/bot{}/getUpdates?offset={}".format(api_key,update_id)
        response = requests.get(url)
        data=response.json()
        last_msg=data['result'][len(data['result'])-1]['message']['text']
        chat_id=data['result'][len(data['result'])-1]['message']['chat']['id']
        update_id=data['result'][len(data['result'])-1]['update_id']
        user_name=data['result'][len(data['result'])-1]['message']['from']['first_name']
        return last_msg,chat_id,update_id,user_name


def sendMessage(chat_id,text_message):
    url='https://api.telegram.org/bot'+str(api_key)+'/sendMessage?text='+str(text_message)+'&chat_id='+str(chat_id)
    response = requests.get(url)
    return response

def sendInlineMessageForService(chat_id):
    text_message="שלום! אני הבוט שלך עבור קביעת שיעורים פרטיים עם עדן!\n\nאתה יכול לשלוט בי באמצעות הפקודות:\n\n\"שלום\" - להתחיל לדבר עם הבוט\n\"די\" - להפסיק לדבר עם הבוט.\n"
    keyboard={'keyboard':[
                        [{'text':'שנה שיעור'},{'text':'בטל שיעור'}],
                        [{'text':'שיעור חדש'}]]}
    key=json.JSONEncoder().encode(keyboard)
    url='https://api.telegram.org/bot'+str(api_key)+'/sendmessage?chat_id='+str(chat_id)+'&text='+str(text_message)+'&reply_markup='+key
    response = requests.get(url)
    return response
    

def sendInlineMessageForBookingTime(chat_id):
    text_message='בחר זמן עבור השיעור...'
    dates = get_SplitedFreeSlots()
        
    if(len(dates) <= 0):
        sendMessage(chat_id, "לצערנו אין חלון זמן פנוי כרגע" + "\n" + "אנא נסה שנית במועד מאוחר יותר" + "\n" + "תודה!")
    else:
        keyboard={'keyboard': dates}
        key=json.JSONEncoder().encode(keyboard)
        url='https://api.telegram.org/bot'+str(api_key)+'/sendmessage?chat_id='+str(chat_id)+'&text='+str(text_message)+'&reply_markup='+key
        response = requests.get(url)
        return response

def run():
    logf = open("BotLog.txt", "w")
    logf.close()
    update_id_for_booking_of_time_slot=''
    prev_last_msg,chat_id,prev_update_id,user_name=getLastMessage()
    while True:
        try:
            current_last_msg,chat_id,current_update_id,user_name=getLastMessage()
            if prev_last_msg==current_last_msg and current_update_id==prev_update_id:
                events = get_availableSlots()
                continue
            else:
                if current_last_msg=='/start' or current_last_msg=='start' or current_last_msg=='היי' or current_last_msg=='שלום':
                    sendInlineMessageForService(chat_id)
                if current_last_msg in ['בטל שיעור','שנה שיעור','שיעור חדש']:
                    sendInlineMessageForBookingTime(chat_id)
                if validateDate(current_last_msg):
                    booking_time=current_last_msg
                    update_id_for_booking_of_time_slot=current_update_id
                    sendMessage(chat_id,"הכנס כתובת מייל:")
                if current_last_msg=='די':
                    update_id_for_booking_of_time_slot=''
                    # return
                    continue
                if update_id_for_booking_of_time_slot!=current_update_id and update_id_for_booking_of_time_slot!= '':
                    if check_email(current_last_msg)==True:
                        update_id_for_booking_of_time_slot=''
                        sendMessage(chat_id,"קובע, אנא המתן.....")
                        input_email=current_last_msg
                        dates = get_SplitedFreeSlotsWithEvent()
                        dates = [currDate for currDate in dates if currDate[0] != booking_time]
                        delete_availableSlot(booking_time)
                        for currDate in dates:
                            placeFreeTimeSlot(currDate[0])
                        response=book_timeslot(booking_time,input_email,user_name)
                        if response == True:
                            sendMessage(chat_id,"שיעור נקבע! נתראה ב - " + str(booking_time))
                            #sendMessage("860442422", "שיעור חדש נקבע עם " + str(user_name) + " ב - " + str(booking_time))
                            continue
                        else:
                            update_id_for_booking_of_time_slot=''
                            sendMessage(chat_id,"בבקשה נסה חלון זמן אחר ונסה שוב מחר")
                            continue
                    else:
                        sendMessage(chat_id,"יש להכניס מייל תקין.\nהקש \"די\" על מנת להפסיק לדבר עם הבוט\nתודה!")
    
                            
            prev_last_msg=current_last_msg
            prev_update_id=current_update_id
        except Exception as e:
            logf = open("BotLog.txt", "a+")
            logf.write(datetime.datetime.now().strftime("%H:%M:%S") + ": Fail: {0}\n".format(str(e)))
            logf.close()
            continue
            
if __name__ == "__main__":
    run()