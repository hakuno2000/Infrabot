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

def queryHermesGetClient(chain, client):
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
	# print(dest_chain_id)
                        
	dest_chain_height = ""
	for substr in message.split('\n'):
		if " height: " in substr:
			dest_chain_height = substr.split('height: ')[1]
	dest_chain_height = dest_chain_height.replace(',', '')
	# print(dest_chain_height)

	# print(dest_chain_id, dest_chain_height)
	if dest_chain_id == '': print(message)
	return dest_chain_id, dest_chain_height

def queryRpcGetHeigt(rpc):
	global miss_counter, thread_id, warned
	header = {
		'accept': 'application/json',
		'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/99.0.4844.51 Safari/537.36'
	}
	try:
		request = requests.get(f"{rpc}/block", headers=header)
		response = request.json()
		height = response["result"]["block"]["header"]["height"]
		# print(height)
		return height

        # if percentage > 80:
        #     if thread_id == "":
        #         message(os.getenv("NOTI"), f"Our UMEE miss_counter: {miss_counter}, is {percentage}%!")
        #     else: 
        #         message(os.getenv("NOTI"), f"Our UMEE miss_counter: {miss_counter}, is {percentage}%!", thread_id)
        
		warned = False
	except Exception as e:
        # if not warned:
        #     URL="https://hooks.slack.com/services/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"
        #     payload = {
        #         "attachments": [ 
        #             { 
        #                 "text": f"Umee miss_counter bot failed!!!",
        #                 "color": "danger",
        #                 "mrkdwn_in": ["text"],
        #                 "fields": [
        #                     { "title": "Date", "value": f"{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}", "short": True },
        #                     { "title": "Host", "value": "laboratory", "short": True },
        #                     { "title": "Problem", "value": f"{str(e)}", "short": False }
        #                 ]
        #             }
        #         ]
        #     }
        #     requests.post(URL, data=json.dumps(payload))
        #     warned = True
		traceback.print_exc()
            
def checkClientState(chain, client):
	dest_chain_id, dest_chain_height = queryHermesGetClient(chain, client)
	# dest_chain_rpc = clients_data[dest_chain_id]["api"]
	dest_chain = clients_data[dest_chain_id]
	# print(dest_chain)
	if dest_chain_id == '': return
	dest_chain_current_height = queryRpcGetHeigt(dest_chain["rpc"])

	block_time = dest_chain["block_time"]
	last_update = (int(dest_chain_current_height) - int(dest_chain_height)) * block_time
	limit = 86400
	
	print(f"Chain {chain}'s client to {dest_chain['name']} last updated height is {dest_chain_height} and current height is {dest_chain_current_height}")
	# if last_update > limit:
	# 	if thread_id == "":
	# 		message(os.getenv("PI"), f"Our {dest_chain_id} client is not updated")
	# 	else: 
	# 		message(os.getenv("PI"), f"Our {dest_chain_id} client is not updated", thread_id)

if __name__ == "__main__":
	# Reads chains-data file relative to the location of this file.
	root_dir = parent_dir_name(parent_dir_name(os.path.realpath(__file__)))
	clients_data = os.path.join(root_dir, 'clients-data.json')
	clients_data = json.load(open(clients_data))
	# umee = chains_data["umee"]       
	# umee["val"] = "umeevaloper1dmahqt84r9je3sqvljzjrttjj78cmrf39k5zhs"

	# while True:
	#     query(umee["api"], umee["val"])
	#     print("Sleeping for 10 seconds\n") # block time of umee
	#     time.sleep(10)

	# checkClientState('centauri-1', '07-tendermint-1')
	for chain in clients_data:
		for client in clients_data[chain]["clients"]:
			# if client == '': continue
			checkClientState(chain, client)