from login import *
import json
from twilio.rest import Client
from dotenv import load_dotenv
import os

load_dotenv()

account_sid = os.getenv('TWILIOSSID')
auth_token = os.getenv('TWILIOAUTHTOKEN')
client = Client(account_sid, auth_token)

def get_event_details():
    login_status = login_to_qums()
    today_event = get_today_event(login_status['cookies'],login_status['student_details'],login_status['data_list'], login_status['session'])
    if today_event.status_code == 200:
        event_info = today_event.json()
        grab_that_info = event_info["state"]
        data_list = json.loads(grab_that_info)
        event_generated = generate_event(data_list)
        print("EVENT GENERATED SUCCESSFULLY" if event_generated else "EVENT NOT GENERATED")


def get_today_attendance():
    login_status = login_to_qums()
    today_event = get_today_event(login_status['cookies'], login_status['student_details'], login_status['data_list'],
                                  login_status['session'])
    if today_event.status_code == 200:
        event_info = today_event.json()
        grab_that_info = event_info["state"]
        data_list = json.loads(grab_that_info)
        totalClass = len(data_list)
        present = 0
        notMentioned = 0
        for i in range(totalClass):
            if data_list[i]["Attend"] == 'A':
                present =+ 1
            elif data_list[i]["Attend"] == 'N.M.':
                notMentioned =+1
        today_event = get_total_attendance(login_status['cookies'], login_status['student_details'],
                                           login_status['data_list'],
                                           login_status['session'])
        if today_event.status_code == 200:
            attendance_info = today_event.json()
            grab_that_info = attendance_info["state"]
            data_list = json.loads(grab_that_info)
            client.messages.create(
                from_='whatsapp:+14155238886',
                body=f"Total class : {totalClass}\nPresent in  class : {present}\nNot Mentioned : {notMentioned}\nTotal Attendance : {data_list[0]['AttendPer']}",
                to='whatsapp:+919608144523'
            )


if __name__ == "__main__":
    get_today_attendance()