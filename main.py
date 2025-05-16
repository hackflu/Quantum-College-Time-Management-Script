from apscheduler.schedulers.blocking import BlockingScheduler

from attendance import *

def main():
    # scheduler = BlockingScheduler(timezone='Asia/Kolkata')
    # scheduler.add_job(get_event_details, 'cron', hour='6', minute='1')
    # scheduler.add_job(get_today_attendance , 'cron' , hour='18', minute='1')
    # scheduler.start()


    get_event_details()

if __name__ == '__main__':
    main()

