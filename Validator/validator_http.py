import os
import sys
import json
import time
import requests
import traceback
from datetime import datetime
from dotenv import load_dotenv
from os.path import dirname as parent_dir_name

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from app import message, checked
from getRandomMessage import getRandomMessage

load_dotenv()

block_missing = 0
latest_height = 0
thread_id=""
warned = False

def query(name, rpc, validator):
    global latest_height, block_missing, alive, thread_id, warned
    alive = False
    try:
        request = requests.get(f"{rpc}/block", headers={
                    'accept': 'application/json',
                    'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/99.0.4844.51 Safari/537.36'
                })
        data = request.json()['result']['block']
        validators = data['last_commit']["signatures"]
        height = int(data['header']['height'])
        if latest_height != height:
            latest_height = int(height)
            for i in validators:
                if i["validator_address"] == validator:
                    alive = True
                    print(f"{name} still alive: {latest_height:,}")
                    if block_missing != 0:
                        if block_missing >= 20:
                            message(os.getenv("NOTI"), f"Hurray, our {name} is up again!", thread_id)
                        block_missing = 0
                    break
            if not alive:
                block_missing = block_missing + 1
                if block_missing >= 20 and block_missing % 20 == 0:
                    if block_missing == 20:
                        res = message(os.getenv("NOTI"), f"Our {name} missing blocks")
                        thread_id = res.get("ts")
                        message(os.getenv("NOTI"), f"{block_missing} blocks missing now. React with ✅ and I will stop alerting in every 500 blocks.", thread_id)
                    else:
                        users_checked = checked(os.getenv("NOTI"), thread_id)
                        if (users_checked == None) or ((os.getenv("MINH") not in users_checked) and (os.getenv("DU") not in users_checked) and (os.getenv("LONG") not in users_checked)):
                            message(os.getenv("NOTI"), getRandomMessage("missing_blocks", user_1=os.getenv("MINH"), user_2=os.getenv("LONG"), user_3=os.getenv("DU"), blocks=block_missing), thread_id)        
                        elif block_missing % 500 == 0:
                            message(os.getenv("NOTI"), f"Our {name} still missing {block_missing} blocks", thread_id)
            
        warned = False
    except Exception as e:
        if not warned:
            URL="https://hooks.slack.com/services/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"
            payload = {
                "attachments": [ 
                    { 
                        "text": f"Validator Bot of {name} failed!!!",
                        "color": "danger",
                        "mrkdwn_in": ["text"],
                        "fields": [
                            { "title": "Date", "value": f"{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}", "short": True },
                            { "title": "Host", "value": "laboratory", "short": True },
                            { "title": "Problem", "value": f"{str(e)}", "short": False }
                        ]
                    }
                ]
            }
            requests.post(URL, data=json.dumps(payload))
            warned = True
        
        traceback.print_exc()

if __name__ == "__main__":
    chain = sys.argv[1]

    # Reads chains-data file relative to the location of this file.
    root_dir = parent_dir_name(parent_dir_name(os.path.realpath(__file__)))
    print(root_dir)
    chains_data = os.path.join(root_dir, 'chains-data.json')
    chains_data = json.load(open(chains_data))
    chainData = chains_data[chain]

    while True:
        query(chainData["name"], chainData["rpc"], chainData["hash"])
        print("Sleeping for 2 seconds") # minimum block time of every chains
        time.sleep(2)        