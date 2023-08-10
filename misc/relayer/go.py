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

telegram_notify = telegram.Bot('{}'.format(os.environ['GO_BOT']))
CHAT_ID = '{}'.format(os.environ['CHAT_ID'])
#CHAT_ID = '-772344443'
low_balances = [0] * 30

def multi_run_wrapper(args):
   return query(*args)

def query(name, binaries, address, rpc, denom, limit, id):
	balance = int(re.findall(r'\d+', subprocess.run(['/root/go/bin/{}'.format(binaries), 'q', 'bank', 'balances', '{}'.format(address), '--denom', '{}'.format(denom), '--node', '{}'.format(rpc), '-o', 'json'], stdout=subprocess.PIPE).stdout.decode('utf-8'))[0])
	print(name, balance)

	if (balance < int(limit)):
		print(balance)
		telegram_notify.send_message(chat_id=CHAT_ID, text="Balance of {}: {} {}. Consider refilling!".format(name, balance, denom))
		low_balances[int(id)] = balance
	if (balance > low_balances[int(id)] and low_balances[int(id)] != 0):
		telegram_notify.send_message(chat_id=CHAT_ID, text="Hurray, {} is refilled now!".format(name))

def main():
	chains = json.load(open('/root/alert/chains-data.json'))
	chains["gaia"]["address"] = "cosmos1yeac5tgm4mqwl4fyrqp34s0gq5fy8ugxcj76vc"
	chains["gaia"]["limit"] = "300000"

	chains["osmosis"]["address"] = "osmo1yeac5tgm4mqwl4fyrqp34s0gq5fy8ugxsfd262"

	chains["akash"]["address"] = "akash1yeac5tgm4mqwl4fyrqp34s0gq5fy8ugx4fna4z"
	chains["akash"]["limit"] = "300000"

	chains["sifchain"]["address"] = "sif1yeac5tgm4mqwl4fyrqp34s0gq5fy8ugxa03vrn"

	chains["regen"]["address"] = "regen1yeac5tgm4mqwl4fyrqp34s0gq5fy8ugx8s4x6u"

	chains["sentinel"]["address"] = "sent1yeac5tgm4mqwl4fyrqp34s0gq5fy8ugxrfgrgh"

	chains["juno"]["address"] = "juno1yeac5tgm4mqwl4fyrqp34s0gq5fy8ugxwqapty"
	chains["juno"]["limit"] = "500000"

	chains["cheq"]["address"] = "cheqd1yeac5tgm4mqwl4fyrqp34s0gq5fy8ugxksj68f"

	chains["bitcanna"]["address"] = "bcna1yeac5tgm4mqwl4fyrqp34s0gq5fy8ugxzzwmy2"
	chains["bitcanna"]["limit"] = "1000000"

	chains["kava"]["address"] = "kava1fj23cetx2u50su42hzz7cjyrlxkhwu9vlnmh4q"
	chains["kava"]["limit"] = "100000"


	p = Pool(20)
	while True:
		p.map(multi_run_wrapper, [
			(chains["gaia"]["name"], 		chains["gaia"]["binaries"], 	chains["gaia"]["address"], 		chains["gaia"]["rpc"], 		chains["gaia"]["denom"], 		chains["gaia"]["limit"], 		chains["gaia"]["id"]),
			(chains["osmosis"]["name"], 	chains["osmosis"]["binaries"], 	chains["osmosis"]["address"], 	chains["osmosis"]["rpc"], 	chains["osmosis"]["denom"], 	chains["osmosis"]["limit"], 	chains["osmosis"]["id"]),
			(chains["akash"]["name"], 		chains["akash"]["binaries"], 	chains["akash"]["address"], 	chains["akash"]["rpc"], 	chains["akash"]["denom"], 		chains["akash"]["limit"], 		chains["akash"]["id"]),
			(chains["sifchain"]["name"], 	chains["sifchain"]["binaries"], chains["sifchain"]["address"], 	chains["sifchain"]["rpc"], 	chains["sifchain"]["denom"], 	chains["sifchain"]["limit"], 	chains["sifchain"]["id"]),
			(chains["regen"]["name"], 		chains["regen"]["binaries"], 	chains["regen"]["address"], 	chains["regen"]["rpc"], 	chains["regen"]["denom"], 		chains["regen"]["limit"], 		chains["regen"]["id"]),
			(chains["sentinel"]["name"], 	chains["sentinel"]["binaries"], chains["sentinel"]["address"], 	chains["sentinel"]["rpc"], 	chains["sentinel"]["denom"], 	chains["sentinel"]["limit"], 	chains["sentinel"]["id"]),
			(chains["juno"]["name"], 		chains["juno"]["binaries"], 	chains["juno"]["address"], 		chains["juno"]["rpc"], 		chains["juno"]["denom"], 		chains["juno"]["limit"], 		chains["juno"]["id"]),
			(chains["cheq"]["name"], 		chains["cheq"]["binaries"], 	chains["cheq"]["address"], 		chains["cheq"]["rpc"], 		chains["cheq"]["denom"], 		chains["cheq"]["limit"], 		chains["cheq"]["id"]),
			(chains["bitcanna"]["name"], 	chains["bitcanna"]["binaries"], chains["bitcanna"]["address"], 	chains["bitcanna"]["rpc"], 	chains["bitcanna"]["denom"], 	chains["bitcanna"]["limit"], 	chains["bitcanna"]["id"]),
			(chains["kava"]["name"], 		chains["kava"]["binaries"], 	chains["kava"]["address"], 		chains["kava"]["rpc"], 		chains["kava"]["denom"], 		chains["kava"]["limit"], 		chains["kava"]["id"])
		])
		time.sleep(10800)

main()
