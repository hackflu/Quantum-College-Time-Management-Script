import datetime
import os
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.errors import HttpError
from random import randint

SCOPES = ["https://www.googleapis.com/auth/calendar"]

class Schedule:

    def __init__(self):
        self.events = []
        self.creds = None

    def generate_color(self,response_length):
        flag = 0
        colors = []
        while flag < len(response_length):
            colorId = randint(1, 12)
            if colorId not in colors:
                colors.append(colorId)
                flag += 1
        return colors

    def create_event(self ,subject , period , classes_time,teacher,colorId):
        try:
            class_time = classes_time.split("-")
            filter_time = class_time[0].strip()
            hours = int(filter_time.split(":")[0])
            minutes = int(filter_time.split(":")[1])
            specified_date = datetime.date.today()
            specified_datetime = datetime.datetime.combine(specified_date, datetime.time(hours, minutes))

            event = {

                'summary': f'{subject} | {classes_time}',
                'start': {
                    'dateTime': specified_datetime.isoformat(),
                    'timeZone': 'Asia/Kolkata',
                },
                'colorId' : f'{colorId}',
                'end': {
                    'dateTime': (specified_datetime + datetime.timedelta(minutes=1)).isoformat(),
                    'timeZone': 'Asia/Kolkata',
                },
                'description': f'Subject: {subject} \n Time: {str(class_time)} \n Period: {period} Period \n See you in {teacher}class!'
            }
            self.events.append(event)

        except HttpError as error:
            print(f"An error occurred: {error}")

    def create_events(self,service):
            for event in self.events:
                service.events().insert(calendarId='primary', body=event).execute()

    def create_cred(self):
        if os.path.exists("token.json"):
            self.creds = Credentials.from_authorized_user_file(r"token.json", SCOPES)

        if not self.creds or not self.creds.valid:
            if self.creds and self.creds.expired and self.creds.refresh_token:
                self.creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
            r"credentials.json", SCOPES,
            )
            self.creds = flow.run_local_server(port=0)

            with open("token.json", "w") as token:
                token.write(self.creds.to_json())

        return self.creds


if __name__ == "__main__":
    Schedule()



