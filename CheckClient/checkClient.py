import os
import sys
import json
import time
import requests
import traceback
import re
import subprocess
from datetime import datetime
from dotenv import load_dotenv
from os.path import dirname as parent_dir_name

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from app import message

load_dotenv()
miss_counter = 0 
thread_id=""
warned = False

def queryClient(chain, client):
	message = subprocess.run(['hermes1.5','query','client','state', '--chain',f'{chain}', '--client', f'{client}'], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
	# print(message.stdout.decode('utf-8'))
	message = message.stdout.decode('utf-8')
	# print(message)
        
	dest_chain_id = ""
	for substr in message.split('\n'):
		if " id: " in substr:
			dest_chain_id = substr.split('id: ')[1]
	dest_chain_id = dest_chain_id.replace(',', '')
	dest_chain_id = dest_chain_id.replace('"', '')
	print(dest_chain_id)
                        
	dest_chain_height = ""
	for substr in message.split('\n'):
		if " height: " in substr:
			dest_chain_height = substr.split('height: ')[1]
	dest_chain_height = dest_chain_height.replace(',', '')
	print(dest_chain_height)

def query(api, validator):
    global miss_counter, thread_id, warned
    header = {
        'accept': 'application/json',
        'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/99.0.4844.51 Safari/537.36'
    }
    try:
        request = requests.get(f"{api}/umee/oracle/v1/slash_window", headers=header)
        slash_window = int(request.json()["window_progress"])
        
        request = requests.get(f"{api}/umee/oracle/v1/validators/{validator}/miss", headers=header)
        miss_counter = int(request.json()["miss_counter"])
        percentage = float(miss_counter) / float(slash_window) * 100
        print(f"Miss counter: {miss_counter}\nSlash Window: {slash_window}\nPercentage: {percentage}")
        if percentage > 80:
            if thread_id == "":
                message(os.getenv("NOTI"), f"Our UMEE miss_counter: {miss_counter}, is {percentage}%!")
            else: 
                message(os.getenv("NOTI"), f"Our UMEE miss_counter: {miss_counter}, is {percentage}%!", thread_id)
        
        warned = False
    except Exception as e:
        if not warned:
            URL="https://hooks.slack.com/services/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"
            payload = {
                "attachments": [ 
                    { 
                        "text": f"Umee miss_counter bot failed!!!",
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
    # Reads chains-data file relative to the location of this file.
    root_dir = parent_dir_name(parent_dir_name(os.path.realpath(__file__)))
    chains_data = os.path.join(root_dir, 'chains-data.json')
    chains_data = json.load(open(chains_data))
    # umee = chains_data["umee"]       
    # umee["val"] = "umeevaloper1dmahqt84r9je3sqvljzjrttjj78cmrf39k5zhs"

    # while True:
    #     query(umee["api"], umee["val"])
    #     print("Sleeping for 10 seconds\n") # block time of umee
    #     time.sleep(10)
    queryClient('axelar-dojo-1', '07-tendermint-37')