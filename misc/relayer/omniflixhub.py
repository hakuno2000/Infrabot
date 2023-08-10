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

telegram_notify = telegram.Bot('{}'.format(os.environ['OMNIFLIX_BOT']))
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
	chains["gaia"]["address"] = "cosmos1p4zdymjq0jna478v96kjwn8glcuvkmtq234tz5"
	chains["gaia"]["limit"] = "500000"

	chains["osmosis"]["address"] = "osmo1p4zdymjq0jna478v96kjwn8glcuvkmtqz2xm5x"

	chains["akash"]["address"] = "akash1p4zdymjq0jna478v96kjwn8glcuvkmtq82cvmw"

	chains["sifchain"]["address"] = "sif1p4zdymjq0jna478v96kjwn8glcuvkmtq0v6adl"

	chains["sentinel"]["address"] = "sent1p4zdymjq0jna478v96kjwn8glcuvkmtq32rjxm"

	chains["chihuahua"]["address"] = "chihuahua1p4zdymjq0jna478v96kjwn8glcuvkmtqfyc9rk"
	chains["chihuahua"]["limit"] = "3000000"

	chains["stargaze"]["address"] = "stars1p4zdymjq0jna478v96kjwn8glcuvkmtq7dzkf9"

	chains["juno"]["address"] = "juno1p4zdymjq0jna478v96kjwn8glcuvkmtqurks9g"
	chains["juno"]["limit"] = "500000"

	chains["kichain"]["address"] = "ki1p4zdymjq0jna478v96kjwn8glcuvkmtqmuyyxq"
	chains["kichain"]["limit"] = "300000"
	
	chains["gravity"]["address"] = "gravity1p4zdymjq0jna478v96kjwn8glcuvkmtqwp8n8u"
	
	chains["terra"]["address"] = "terra10c7nrsfa29dw2qq38mdue4n8czqdehkf7ts532"
	
	chains["crypto"]["address"] = "cro1fvasy2vulcghpcrptckp6p4pwnl6mhpkt4stmj"

	p = Pool(20)
	while True:
		p.map(multi_run_wrapper, [
			(chains["gaia"]["name"], 		chains["gaia"]["binaries"], 	chains["gaia"]["address"], 		chains["gaia"]["rpc"], 		chains["gaia"]["denom"], 		chains["gaia"]["limit"], 		chains["gaia"]["id"]),
			(chains["osmosis"]["name"], 	chains["osmosis"]["binaries"], 	chains["osmosis"]["address"], 	chains["osmosis"]["rpc"], 	chains["osmosis"]["denom"], 	chains["osmosis"]["limit"], 	chains["osmosis"]["id"]),
			(chains["akash"]["name"], 		chains["akash"]["binaries"], 	chains["akash"]["address"], 	chains["akash"]["rpc"], 	chains["akash"]["denom"], 		chains["akash"]["limit"], 		chains["akash"]["id"]),
			(chains["sifchain"]["name"], 	chains["sifchain"]["binaries"], chains["sifchain"]["address"], 	chains["sifchain"]["rpc"], 	chains["sifchain"]["denom"], 	chains["sifchain"]["limit"], 	chains["sifchain"]["id"]),
			(chains["sentinel"]["name"], 	chains["sentinel"]["binaries"], chains["sentinel"]["address"], 	chains["sentinel"]["rpc"], 	chains["sentinel"]["denom"], 	chains["sentinel"]["limit"], 	chains["sentinel"]["id"]),
			(chains["juno"]["name"], 		chains["juno"]["binaries"], 	chains["juno"]["address"], 		chains["juno"]["rpc"], 		chains["juno"]["denom"], 		chains["juno"]["limit"], 		chains["juno"]["id"]),
			(chains["chihuahua"]["name"], 	chains["chihuahua"]["binaries"],chains["chihuahua"]["address"], chains["chihuahua"]["rpc"],	chains["chihuahua"]["denom"], 	chains["chihuahua"]["limit"], 	chains["chihuahua"]["id"]),
			(chains["kichain"]["name"], 	chains["kichain"]["binaries"], 	chains["kichain"]["address"], 	chains["kichain"]["rpc"], 	chains["kichain"]["denom"], 	chains["kichain"]["limit"], 	chains["kichain"]["id"]),
			(chains["stargaze"]["name"], 	chains["stargaze"]["binaries"], chains["stargaze"]["address"], 	chains["stargaze"]["rpc"], 	chains["stargaze"]["denom"], 	chains["stargaze"]["limit"], 	chains["stargaze"]["id"]),
			(chains["gravity"]["name"], 	chains["gravity"]["binaries"], 	chains["gravity"]["address"], 	chains["gravity"]["rpc"], 	chains["gravity"]["denom"], 	chains["gravity"]["limit"], 	chains["gravity"]["id"]),
			(chains["terra"]["name"], 		chains["terra"]["binaries"], 	chains["terra"]["address"], 	chains["terra"]["rpc"], 	chains["terra"]["denom"], 		chains["terra"]["limit"], 		chains["terra"]["id"]),
			(chains["crypto"]["name"], 		chains["crypto"]["binaries"], 	chains["crypto"]["address"], 	chains["crypto"]["rpc"], 	chains["crypto"]["denom"], 		chains["crypto"]["limit"], 		chains["crypto"]["id"])
		])
		time.sleep(10800)

main()
