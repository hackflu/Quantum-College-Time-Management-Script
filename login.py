import os
import requests
import base64
from apify_client import ApifyClient
from dotenv import load_dotenv
import time
from googleapiclient.discovery import build
from event import Schedule
import json

load_dotenv()
s1 = Schedule()

headers = {
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/png,image/svg+xml,*/*;q=0.8",
            "Accept-Encoding": "gzip, deflate, br, zstd",
            "Accept-Language": "en-US,en;q=0.5",
            "Connection": "keep-alive",
            "Content-Type": "application/x-www-form-urlencoded",
            "Host": "qums.quantumuniversity.edu.in",
            "Origin": "https://qums.quantumuniversity.edu.in",
            "Referer": "https://qums.quantumuniversity.edu.in/",
            "Upgrade-Insecure-Requests": "1",
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:130.0) Gecko/20100101 Firefox/130.0"
        }

def ocr_space_file(filename, overlay=False, api_key=os.getenv('OCRENGINE')):
  payload = {'isOverlayRequired': overlay,
             'apikey': api_key,
             'language': 'eng',
              'OCREngine' : 2
             }
  with open(filename, 'rb') as f:
      r = requests.post('https://api.ocr.space/parse/image',
                        files={filename: f},
                        data=payload,
                        )
  return r.json()

def csrf_image():
    apify_client = ApifyClient(os.getenv('APIFY'))
    actor_call = apify_client.actor('devil_know_you/bot').call()
    dataset_items = apify_client.dataset(actor_call['defaultDatasetId']).list_items().items

    base64_string = dataset_items[0]['captchaImageSrc']
    print(f"[+] CAPTCHA IMAGE IN BASE64 : {base64_string.split(',')[1]}")
    image_data = base64.b64decode(f"{base64_string.split(',')[1]}")

    with open("decoded_image.jpg", "wb") as image_file:
        image_file.write(image_data)
    print("Image decoded and saved as decoded_image.jpg!")
    img_txt = ocr_space_file(filename='decoded_image.jpg')
    print(f"[+] CAPTCHA TEXT :{img_txt['ParsedResults'][0]['ParsedText']}")

    data = {
        "dataset_item" : dataset_items,
        "imageText" : img_txt
    }
    return data

def get_student_details(cookies , loginResponse ,session):
    redirect_url = "https://qums.quantumuniversity.edu.in/Account/GetStudentDetail"
    print(f"Accessing redirected page: {redirect_url}")

    headers["Referer"] = "https://qums.quantumuniversity.edu.in/Account/Cyborg_StudentMenu"
    headers["Content-Type"] = "application/x-www-form-urlencoded; charset=UTF-8"
    update_headers = {
        "Content-Length": "0",
        "X-Requested-With": "XMLHttpRequest",
    }
    headers.update(update_headers)
    cookies.update(loginResponse.cookies.get_dict())

    redirected_response = session.post(redirect_url, headers=headers, cookies=cookies)
    return redirected_response

def get_today_event(cookies , redirected_response , data_list,session):
    another_redirect = "https://qums.quantumuniversity.edu.in/Web_StudentAcademic/GetTodayAttendance"
    cookies.update(redirected_response.cookies.get_dict())
    data = {
        'RegID': f'{data_list[0]["RegID"]}',
        "date": f"{time.strftime("%d/%m/%Y")}"
    }
    another_redirect_response = session.post(another_redirect, headers=headers, cookies=cookies, data=data)
    return another_redirect_response

def get_total_attendance(cookies , redirected_response , data_list,session):
    attendance_redirect = "https://qums.quantumuniversity.edu.in/Web_StudentAcademic/GetStudentTileData"
    cookies.update(redirected_response.cookies.get_dict())
    data = {
        'RegID': f'{data_list[0]["RegID"]}',
    }
    attendance_redirect_response = session.post(attendance_redirect, headers=headers, cookies=cookies, data=data)
    return attendance_redirect_response

def generate_event(grab_that_info):
    creds = s1.create_cred()
    service = build("calendar", "v3", credentials=creds)
    colors = s1.generate_color(grab_that_info)
    total = 0
    for val in range(0, len(colors)):
        total += 1
        s1.create_event(grab_that_info[val]["subject"], grab_that_info[val]["Period"],
                        grab_that_info[val]["Duration"], grab_that_info[val]["Employeename"],colors[val])

    s1.create_events(service)
    return True if total == len(grab_that_info) else False

def login_to_qums():
    try:
        with requests.Session() as session:
            data = csrf_image()
            login_page = "https://qums.quantumuniversity.edu.in"
            dataset_items = data['dataset_item']
            img_txt = data['imageText']

            login_data = {
                "hdnMsg": "QGC",
                "checkOnline": "0",
                "__RequestVerificationToken": dataset_items[0]['csrfToken'],
                "UserName": os.getenv("USER"),
                "Password": os.getenv("PASS"),
                "clientIP": "~~~~~",
                "captcha": f"{img_txt['ParsedResults'][0]['ParsedText']}",
            }

            cookies= {
                'ASP.NET_SessionId':dataset_items[0]['cookies'][1]['value'],
                '__RequestVerificationToken' : dataset_items[0]['cookies'][0]['value']
            }
            login_response = session.post(login_page, data=login_data, headers=headers, cookies=cookies, allow_redirects=False)

            if login_response.status_code == 302:
                print("Login Successful")
                student_details = get_student_details(cookies,login_response,session)

                if student_details.status_code == 200:
                    received_json = student_details.json()
                    data_list = json.loads(received_json['state'])
                    print("page accessed successfully!")
                    return {
                        'cookies': cookies,
                        'student_details': student_details,
                        'data_list': data_list,
                        'session': session
                    }
                else:
                    raise Exception(f"Failed to access the Cyborg_StudentMenu page. Status code: {student_details.status_code}")
            else:
                raise Exception(f"Login failed {login_response.status_code}")
    except Exception as e:
        print(f"Error occurred: {e}")
        time.sleep(5)
        return login_to_qums()