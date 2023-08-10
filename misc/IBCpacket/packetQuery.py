import json
import logging
import os
import sys
import time
import multiprocessing as mp
from os.path import dirname as parent_dir_name
from urllib.request import Request, urlopen

import telegram

telegram_notify = telegram.Bot(f"{os.environ['IBC_BOT']}")
CHAT_ID = f"{os.environ['CHAT_ID']}"
#CHAT_ID = '-772344443'

def multi_run_wrapper(args):
   return query(*args)

def query(name, api, channels):
	header = {
		'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/99.0.4844.84 Safari/537.36',
	}
	for channel in channels:
		request = Request(f"{api}/ibc/core/channel/v1/channels/{channel['id']}/ports/transfer/packet_commitments", None, header)
#		https://lcd-cosmos.cosmostation.io/ibc/core/channel/v1/channels/channel-141/ports/transfer/packet_commitments
		data = json.loads(urlopen(request).read())
		packets_lost = int(data["pagination"]["total"])
		if packets_lost > 20:
			try:
				telegram_notify.send_message(chat_id=CHAT_ID, text=f"🛑 {name} -> {channel['chain']}: {packets_lost} packets pending. Please rescue them ASAP!!!")
				print(f"Queried {name} -> {channel['chain']}")
			except:
				print(name, channel["chain"], sys.exc_info())
				logging.exception("Error occurred while printing")
		elif packets_lost > 10:
			try:
				telegram_notify.send_message(chat_id=CHAT_ID, text=f"❗️ {name} -> {channel['chain']}: {packets_lost} packets pending. We are stuckkkkk!")
				print(f"Queried {name} -> {channel['chain']}")
			except:
				print(name, channel["chain"], sys.exc_info())
				logging.exception("Error occurred while printing")
		elif packets_lost > 0:
			try:
				telegram_notify.send_message(chat_id=CHAT_ID, text=f"⚠️ {name} -> {channel['chain']}: {packets_lost} packets pending!")
				print(f"Queried {name} -> {channel['chain']}")
			except:
				print(name, channel["chain"], sys.exc_info())
				logging.exception("Error occurred while printing")
		elif packets_lost == 0:
			telegram_notify.send_message(chat_id=CHAT_ID, text=f"✅ {name} -> {channel['chain']}: clear.")

def main():
	# Reads chains-data file relative to the location of this file.
	root_dir = parent_dir_name(parent_dir_name(os.path.realpath(__file__)))
	chains_data = os.path.join(root_dir, 'chains-data.json')
	chains = json.load(open(chains_data))

	p = mp.Pool()

	while True:
		to_query = []
		for chain in ["gaia", "osmosis", "juno"]:
			to_query.append([chains[chain]["name"], chains[chain]["api"], chains[chain]["channels"]])
		p.map(multi_run_wrapper, to_query)

		time.sleep(300)

if __name__ == '__main__':
	main()
