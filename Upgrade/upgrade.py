from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

import os
import sys
import json
import time
import datetime
import requests
import traceback
from datetime import datetime as dt
from zoneinfo import ZoneInfo
from dotenv import load_dotenv
from os.path import dirname as parent_dir_name

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from getRandomMessage import getRandomMessage
from app import message

load_dotenv()

upgrade_list = {}
SCOPES = ['https://www.googleapis.com/auth/calendar']

def calendarAddEvent(chainName, timeToUpgrade):
    creds = None
    # The file token.json stores the user's access and refresh tokens, and is created automatically when the authorization flow completes for the first time
    if os.path.exists('token.json'):
        creds = Credentials.from_authorized_user_file('Upgrade/token.json', SCOPES)
    # If there are no (valid) credentials available, let the user log in
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                'Upgrade/credentials.json', SCOPES)
            creds = flow.run_local_server(port=0)
        # Save the credentials for the next run
        with open('Upgrade/token.json', 'w') as token:
            token.write(creds.to_json())

    try:
        service = build('calendar', 'v3', credentials=creds)
        
        # Prepare the datetime for the event
        now = datetime.datetime.now(datetime.timezone.utc)
        t = datetime.timedelta(hours=0, minutes=0, seconds=timeToUpgrade)
        eventTime = now + t
        startTime = (eventTime - datetime.timedelta(hours=12)).isoformat()
        endTime = (eventTime + datetime.timedelta(hours=12)).isoformat()
        # print(startTime)
        # print(endTime)
        # print(now.isoformat())

        # Calendar ID for API
        notionCalendar = 'c_e5274c4d0b395cd35e6af8e094d8c997d1ef8a55b6d356d095739375c2f1d608@group.calendar.google.com'

        # Get all events in timerange to check if there is any upgrade event created before
        page_token = None
        while True:
            events = service.events().list(calendarId=notionCalendar, pageToken=page_token, timeMin=now.isoformat(), timeMax=endTime).execute()
            for event in events['items']:
                # print(event['summary'])
                # print(event['start']['dateTime'])
                if chainName in event['summary']:
                    print('Event already created')
                    return event.get('htmlLink')
            page_token = events.get('nextPageToken')
            if not page_token:
                break

        # Create a new upgrade event
        upgradeEvent = {
            'summary': chainName + ' Upgrade Reminder',
            'location': 'Sao Biển 23, Dương Xá, Gia Lâm, Hà Nội',
            'description': 'Need to upgrade ' + chainName,
            'start': {
                # 'dateTime': '2023-07-05T09:00:00-07:00',
                'dateTime': startTime,
                'timeZone': 'Asia/Ho_Chi_Minh',
            },
            'end': {
                # 'dateTime': '2023-07-05T17:00:00-07:00',
                'dateTime': endTime,
                'timeZone': 'Asia/Ho_Chi_Minh',
            },
            # 'recurrence': [
            #     'RRULE:FREQ=DAILY;COUNT=1'
            # ],
              "organizer": {
                "email": 'vinh@notional.ventures',
                "displayName": 'Nguyễn Quang Vinh',
                "self": False
            },
            'attendees': [
                {'email': 'vinh@notional.ventures'},
            ],
            'reminders': {
                'useDefault': True,
                # 'overrides': [
                #     {'method': 'email', 'minutes': 24 * 60},
                #     {'method': 'popup', 'minutes': 10},
                # ],
            },
        }
        createdEvent = service.events().insert(calendarId=notionCalendar, body=upgradeEvent).execute()
        print('Event created: %s' % (createdEvent.get('htmlLink')))
        return createdEvent.get('htmlLink')

    except HttpError as error:
        print('An error occurred: %s' % error)
        return None

def getUpdate():
    final_msg = ""
    try:
        data = requests.get(
            "https://polkachu.com/api/v2/chain_upgrades",
            headers={
                'accept': 'application/json',
                'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/99.0.4844.51 Safari/537.36'
            }
        )

        data = data.json()
        for chain in data:
            upgrade_list[chain["network"]] = {
                "id": chain["network"],
                "name": chain["chain_name"],
                "upgrade_height":  int(chain["block"]),
                "version": chain["node_version"],
                "repo": chain["repo"],
                "rpc": chain["rpc"],
                "api": chain["api"],
                "upgrade_time": chain["estimated_upgrade_time"],
            }

        # print(upgrade_list)
        # for chain in upgrade_list:
        #     urlString = chain["rpc"] + "/block"
        #     try:
        #         response = requests.get(
        #             urlString,
        #             headers={
        #                 'accept': 'application/json',
        #                 'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/99.0.4844.51 Safari/537.36'
        #             }
        #         ).json()

        #         try:
        #             current_height = response["result"]["block"]["header"]["height"]
        #         except:
        #             current_height = response["block"]["header"]["height"]

        #         upgrade_height = chain["upgrade_height"]

        #         currentHeight = int(response["height"])
        #         blockTime = float(response["blockTime"])
        #         upgradeHeight = upgrade_list[chain]["height"]

        #         timeToUpgrade = (upgradeHeight - currentHeight) * blockTime
        #         print(chain, upgradeHeight, timeToUpgrade )
        #         if timeToUpgrade < 86400:
        #             print(f"{chain} need to upgrade")
        #             str_time = (datetime.datetime.now().astimezone() + datetime.timedelta(seconds=timeToUpgrade) + datetime.timedelta(hours=7)).astimezone()
        #             time = str_time.strftime("%H:%M %d/%m/%Y")
        #             res = message(os.getenv("PI"), f"UPGRADE: *{chain}* at around *{time}*")
        #             thread_id = res.get("ts")
        #             message(os.getenv("PI"), f"Name: *{chain}*\nProposal ID: *{upgrade_list[chain]['id']}*\nBlock: *{upgradeList[chain]['height']}*\nVersion: *{upgradeList[chain]['version']}*\n", thread_id)

        #     except Exception as e:
        #         print(f"Error getting data from {urlString}: {e}")
        #         traceback.print_exc()
        #         continue
        #     # print(urlString)

        for chain in upgrade_list:
            try:
                upgrade_time = upgrade_list[chain]["upgrade_time"]
                # to datetime UTC
                upgrade_time = dt.fromisoformat(upgrade_time.replace('Z', '+00:00'))
                # to Vietnam timezone
                upgrade_time = upgrade_time.astimezone(ZoneInfo("Asia/Ho_Chi_Minh"))
                str_upgrade_date = str(upgrade_time.day) + "/" + str(upgrade_time.month)
                str_upgrade_time = str(upgrade_time.hour) + ":" + str(upgrade_time.minute)

                current_time = dt.fromisoformat(str(dt.now())).replace(tzinfo=None)
                time_diff = upgrade_time.replace(tzinfo=None) - current_time
                if (time_diff.days == 0 and time_diff.seconds < 86400):
                    if (final_msg == ""):
                        final_msg += "Upcoming upgrade in 24 hours:"
                    final_msg += "\n"
                    final_msg += f"- {upgrade_list[chain]['name']} needs to upgrade in about {time_diff.seconds // 3600} hour(s), on {str_upgrade_date} at {str_upgrade_time}"

                # res = message(os.getenv("PI"), f"UPGRADE: *{chain}* at around *{upgrade_time}*")
                # thread_id = res.get("ts")
                # message(os.getenv("PI"), f"Name: *{chain}*\nProposal ID: *{upgrade_list[chain]['id']}*\nBlock: *{upgrade_list[chain]['upgrade_height']}*\nVersion: *{upgrade_list[chain]['version']}*\n", thread_id)
                # calendarAddEvent(chain, upgrade_time)
            except Exception as e:
                print(f"Error getting data")
                traceback.print_exc()
                continue

    except Exception as e:
        final_msg = f"Issue with request to upgrade watcher api: {e}"
        traceback.print_exc()
    
    message(os.getenv("PI"), final_msg)
    # print(final_msg)
    return upgrade_list

if __name__ == "__main__":
    # root_dir = parent_dir_name(parent_dir_name(os.path.realpath(__file__)))
    # chains_data = os.path.join(root_dir, 'chains-data.json')
    # chains_data = json.load(open(chains_data))

    getUpdate()