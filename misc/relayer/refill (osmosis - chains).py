import json
import os
import re
import subprocess
from os.path import dirname as parent_dir_name

import telegram.ext

telegram_notify = telegram.Bot(f'5297296062:AAESbdkLSq51b3bvJ0kMqHsLA0_yjHcmuhY')
CHAT_ID = f"{os.environ['CHAT_ID']}"
#CHAT_ID = '-772344443'
passphrase = f"{os.environ['PASSPHRASE']}\n"
refill = 'osmo1amm3lhqeya0t985clyg27szp2wfmnn7rckgxzx'

def multi_run_wrapper(args):
   return query(*args)

def query(name, binaries, address, rpc, limit, low_id, IBCdenom, pool_id, channel):	
	balances = re.findall(r'\d+', subprocess.run([f'/root/go/bin/{binaries}','q','bank','balances',f'{address}','--node',f'{rpc}','-o','json'], stdout=subprocess.PIPE).stdout.decode('utf-8'))
	print(balances)
	if (int(balances[int(low_id)]) < int(limit)):
		if (address == 'osmo16dc379m0qj64g4pr4nkl7ewak52qy2srpp40er'):
			swap(address, limit * 10, rpc)
		else:
			IBCTransfer(address, limit * 10, rpc, IBCdenom, pool_id, channel)
		telegram_notify.send_message(chat_id=CHAT_ID, text=f"Hurray, {name} is refilled now!")
		
def swap(receiver, amount, rpc):
	message = subprocess.run(['osmosisd','tx','bank','send',f'{refill}',f'{receiver}',f'{amount}uosmo','--node','http://0.0.0.0:2001','--gas', '80000', '-y', '--chain-id', 'osmosis-1'], input = passphrase.encode(), stdout=subprocess.PIPE, stderr=subprocess.PIPE)
	print(message.stdout.decode('utf-8'))

def IBCTransfer(receiver, amount, rpc, IBCdenom, pool_id, channel):
	# estimate amount swap in: osmosisd q gamm estimate-swap-exact-amount-in 3 osmo1amm3lhqeya0t985clyg27szp2wfmnn7rckgxzx 1000000uosmo --swap-route-denoms ibc/1480B8FD20AD5FCAE81EA87584D269547DD4D436843C1D20F15E00EB64743EF4 --swap-route-pool-ids 3 --chain-id osmosis-1 --node http://0.0.0.0:2001
	print(subprocess.run(['osmosisd', 'q', 'gamm', 'estimate-swap-exact-amount-in', f'{pool_id}', 'osmo1amm3lhqeya0t985clyg27szp2wfmnn7rckgxzx', f'{amount}uosmo', '--swap-route-denoms', f'{IBCdenom}', '--swap-route-pool-ids', f'{pool_id}', '--node', 'http://0.0.0.0:2001', '--chain-id', 'osmosis-1'], stdout=subprocess.PIPE, stderr=subprocess.PIPE))
	estimate = re.findall(r'\d+', subprocess.run(['osmosisd', 'q', 'gamm', 'estimate-swap-exact-amount-in', f'{pool_id}', 'osmo1amm3lhqeya0t985clyg27szp2wfmnn7rckgxzx', f'{amount}uosmo', '--swap-route-denoms', f'{IBCdenom}', '--swap-route-pool-ids', f'{pool_id}', '--node', 'http://0.0.0.0:2001', '--chain-id', 'osmosis-1'], stdout=subprocess.PIPE, stderr=subprocess.PIPE).stdout.decode('utf-8'))
	tokenOut = int(estimate[0])
	print(tokenOut)
	# swap exact amount in: printf "giantchicken\n" | osmosisd tx gamm swap-exact-amount-in 1000000uosmo 6141388 --swap-route-pool-ids 3 --swap-route-denoms ibc/1480B8FD20AD5FCAE81EA87584D269547DD4D436843C1D20F15E00EB64743EF4 --from refill --chain-id osmosis-1 --node http://0.0.0.0:2001 -y
	message = subprocess.run(['osmosisd', 'tx', 'gamm', 'swap-exact-amount-in', f'{amount}uosmo', f'{tokenOut}', '--swap-route-pool-ids', f'{pool_id}', '--swap-route-denoms', f'{IBCdenom}', '--from', 'refill', '--node', 'http://0.0.0.0:2001', '--chain-id', 'osmosis-1', '-y'], input = passphrase.encode(), stdout=subprocess.PIPE, stderr=subprocess.PIPE)
	print(message)
	# Withdraw to relayer address: printf "giantchicken\n" | osmosisd tx ibc-transfer transfer transfer channel-1 akash1amm3lhqeya0t985clyg27szp2wfmnn7rakk3dw 6141388ibc/1480B8FD20AD5FCAE81EA87584D269547DD4D436843C1D20F15E00EB64743EF4 --chain-id osmosis-1 --node http://0.0.0.0:2001 --from osmo1amm3lhqeya0t985clyg27szp2wfmnn7rckgxzx
	info = subprocess.run(['osmosisd', 'tx', 'ibc-transfer', 'transfer', 'transfer', f'{channel}', f'{receiver}', f'{tokenOut}{IBCdenom}', '--from', 'refill', '--node', 'http://0.0.0.0:2001', '--chain-id', 'osmosis-1', '-y'], input = passphrase.encode(), stdout=subprocess.PIPE, stderr=subprocess.PIPE)
	print(info)

def main():
	root_dir = parent_dir_name(parent_dir_name(os.path.realpath(__file__)))
	chains_data = os.path.join(root_dir, 'chains-data.json')
	chains = json.load(open(chains_data))

	chains["gaia"]["address"] = "cosmos1spjh3cgnr9v3uukpqqx7spsw8smgh63jdep8vc"
	IBCTransfer(chains["gaia"]["address"], 1000, chains["gaia"]["rpc"], chains["gaia"]["IBCdenom"], chains["gaia"]["pool_id"], chains["gaia"]["channel"])

if __name__ == '__main__':
	main()
