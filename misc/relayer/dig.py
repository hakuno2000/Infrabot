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

telegram_notify = telegram.Bot('{}'.format(os.environ['DIG_BOT']))
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
	chains["gaia"]["address"] = "cosmos1zgmfjq86snl92u6zuxg4qlwt7f0ds3atwct9yz"

	chains["osmosis"]["address"] = "osmo1zgmfjq86snl92u6zuxg4qlwt7f0ds3atxrc4js"

	chains["juno"]["address"] = "juno1zgmfjq86snl92u6zuxg4qlwt7f0ds3atc2g7r7"
	
	chains["dig"]["address"] = "dig1zgmfjq86snl92u6zuxg4qlwt7f0ds3atkvzwxe"

	p = Pool(20)
	while True:
		p.map(multi_run_wrapper, [
			(chains["gaia"]["name"], 		chains["gaia"]["binaries"], 	chains["gaia"]["address"], 		chains["gaia"]["rpc"], 		chains["gaia"]["denom"], 		chains["gaia"]["limit"], 		chains["gaia"]["id"]),
			(chains["osmosis"]["name"], 	chains["osmosis"]["binaries"], 	chains["osmosis"]["address"], 	chains["osmosis"]["rpc"], 	chains["osmosis"]["denom"], 	chains["osmosis"]["limit"], 	chains["osmosis"]["id"]),
			(chains["juno"]["name"], 		chains["juno"]["binaries"], 	chains["juno"]["address"], 		chains["juno"]["rpc"], 		chains["juno"]["denom"], 		chains["juno"]["limit"], 		chains["juno"]["id"]),
			(chains["dig"]["name"], 		chains["dig"]["binaries"], 		chains["dig"]["address"], 		chains["dig"]["rpc"], 		chains["dig"]["denom"], 		chains["dig"]["limit"], 		chains["dig"]["id"])
		])
		time.sleep(10800)

main()
