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

telegram_notify = telegram.Bot('{}'.format(os.environ['JUNO_BOT']))
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
	chains["gaia"]["address"] = "cosmos18xvpj53vaupyfejpws5sktv5lnas5xj274sdwd"
	chains["gaia"]["limit"] = "500000"

	chains["osmosis"]["address"] = "osmo18xvpj53vaupyfejpws5sktv5lnas5xj2kwracl"

	chains["akash"]["address"] = "akash18xvpj53vaupyfejpws5sktv5lnas5xj2nwa2hh"

	chains["sifchain"]["address"] = "sif18xvpj53vaupyfejpws5sktv5lnas5xj2mglmpx"

	chains["regen"]["address"] = "regen18xvpj53vaupyfejpws5sktv5lnas5xj2phm3cf"

	chains["juno"]["address"] = "juno18xvpj53vaupyfejpws5sktv5lnas5xj2g8nkf3"
	chains["juno"]["limit"] = "500000"

	chains["bitcanna"]["address"] = "bcna18xvpj53vaupyfejpws5sktv5lnas5xj2y9qvxl"
	chains["bitcanna"]["limit"] = "3000000"
	
	chains["persistence"]["address"] = "persistence1davex4mc526tphx7r86n0v2l5d3npq0gsxkhl8"
	
	p = Pool(20)
	while True:
		p.map(multi_run_wrapper, [
			(chains["gaia"]["name"], 		chains["gaia"]["binaries"], 	chains["gaia"]["address"], 		chains["gaia"]["rpc"], 		chains["gaia"]["denom"], 		chains["gaia"]["limit"], 		chains["gaia"]["id"]),
			(chains["osmosis"]["name"], 	chains["osmosis"]["binaries"], 	chains["osmosis"]["address"], 	chains["osmosis"]["rpc"], 	chains["osmosis"]["denom"], 	chains["osmosis"]["limit"], 	chains["osmosis"]["id"]),
			(chains["akash"]["name"], 		chains["akash"]["binaries"], 	chains["akash"]["address"], 	chains["akash"]["rpc"], 	chains["akash"]["denom"], 		chains["akash"]["limit"], 		chains["akash"]["id"]),
			(chains["sifchain"]["name"], 	chains["sifchain"]["binaries"], chains["sifchain"]["address"], 	chains["sifchain"]["rpc"], 	chains["sifchain"]["denom"], 	chains["sifchain"]["limit"], 	chains["sifchain"]["id"]),
			(chains["regen"]["name"], 		chains["regen"]["binaries"], 	chains["regen"]["address"], 	chains["regen"]["rpc"], 	chains["regen"]["denom"], 		chains["regen"]["limit"], 		chains["regen"]["id"]),
			(chains["juno"]["name"], 		chains["juno"]["binaries"], 	chains["juno"]["address"], 		chains["juno"]["rpc"], 		chains["juno"]["denom"], 		chains["juno"]["limit"], 		chains["juno"]["id"]),
			(chains["bitcanna"]["name"], 	chains["bitcanna"]["binaries"], chains["bitcanna"]["address"], 	chains["bitcanna"]["rpc"], 	chains["bitcanna"]["denom"], 	chains["bitcanna"]["limit"], 	chains["bitcanna"]["id"]),
			(chains["persistence"]["name"], chains["persistence"]["binaries"],chains["persistence"]["address"], chains["persistence"]["rpc"], chains["persistence"]["denom"], chains["persistence"]["limit"], chains["persistence"]["id"])
		])
		time.sleep(10800)
main()
