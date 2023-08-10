import subprocess
import telegram.ext
from urllib.request import urlopen
from multiprocessing import Pool, Process
from telegram import ParseMode
import json
from telegram.ext import Defaults, Updater
import requests
import os
import time
import re

telegram_notify = telegram.Bot('{}'.format(os.environ['HERMES_BOT']))
CHAT_ID = '{}'.format(os.environ['CHAT_ID'])
#CHAT_ID = '-772344443'
low_balances = [0] * 30

def multi_run_wrapper(args):
   return query(*args)

def query(name, binaries, address, rpc, denom, limit, id):
	balance = int(re.findall(r'\d+', subprocess.run(['/root/go/bin/{}'.format(binaries), 'q', 'bank', 'balances', '{}'.format(address), '--denom', '{}'.format(denom), '--node', '{}'.format(rpc), '-o', 'json'], stdout=subprocess.PIPE).stdout.decode('utf-8'))[0])
	print(name, balance)

	if (balance < int(limit)):
		telegram_notify.send_message(chat_id=CHAT_ID, text="Balance of {}: {} {}. Consider refilling!".format(name, balance, denom))
		low_balances[int(id)] = balance
	if (balance > low_balances[int(id)] and low_balances[int(id)] != 0):
		telegram_notify.send_message(chat_id=CHAT_ID, text="Hurray, {} is refilled now!".format(name))

def main():
	chains = json.load(open('/root/alert/chains-data.json'))
	chains["gaia"]["address"] = "cosmos16dc379m0qj64g4pr4nkl7ewak52qy2srf6xl03"
	chains["gaia"]["limit"] = "300000"

	chains["osmosis"]["address"] = "osmo16dc379m0qj64g4pr4nkl7ewak52qy2srpp40er"

	chains["sentinel"]["address"] = "sent16dc379m0qj64g4pr4nkl7ewak52qy2srjpsxt7"

	p = Pool(20)
	while True:
		p.map(multi_run_wrapper, [
			(chains["gaia"]["name"], 		chains["gaia"]["binaries"], 	chains["gaia"]["address"], 		chains["gaia"]["rpc"], 		chains["gaia"]["denom"], 		chains["gaia"]["limit"], 		chains["gaia"]["id"]),
			(chains["osmosis"]["name"], 	chains["osmosis"]["binaries"], 	chains["osmosis"]["address"], 	chains["osmosis"]["rpc"], 	chains["osmosis"]["denom"], 	chains["osmosis"]["limit"], 	chains["osmosis"]["id"]),
			(chains["sentinel"]["name"], 	chains["sentinel"]["binaries"], chains["sentinel"]["address"], 	chains["sentinel"]["rpc"], 	chains["sentinel"]["denom"], 	chains["sentinel"]["limit"], 	chains["sentinel"]["id"])
		])
		time.sleep(10800)
main()
