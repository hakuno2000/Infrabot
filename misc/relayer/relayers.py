import json
import os
import time
import multiprocessing as mp

from os.path import dirname as parent_dir_name

import requests
from telegram import Bot

class Relayer:
    def __init__(self, relayer_name: str, bot, addresses: dict, gas_limits: dict):
        self.relayer_name = relayer_name
        self.bot = bot
        self.addresses = addresses
        self.gas_limits = gas_limits    


CHAT_ID = os.environ['CHAT_ID']
RELAYER_BOT = os.environ['RELAYER_BOT']
# CHAT_ID = '-772344443'

bots = {
    "dig": Relayer(
        relayer_name = "dig", 
        bot = Bot(RELAYER_BOT),
        addresses = {
            "gaia": "cosmos1zgmfjq86snl92u6zuxg4qlwt7f0ds3atwct9yz",
            "osmosis": "osmo1zgmfjq86snl92u6zuxg4qlwt7f0ds3atxrc4js",
            "juno": "juno1zgmfjq86snl92u6zuxg4qlwt7f0ds3atc2g7r7",
            "dig": "dig1zgmfjq86snl92u6zuxg4qlwt7f0ds3atkvzwxe",
	    },
        gas_limits={}
    ),

    "go": Relayer(
        relayer_name = "go-relayer", 
        bot = Bot(RELAYER_BOT),        
        addresses = {
            "gaia": "cosmos1yeac5tgm4mqwl4fyrqp34s0gq5fy8ugxcj76vc",
            "osmosis": "osmo1yeac5tgm4mqwl4fyrqp34s0gq5fy8ugxsfd262",
            "akash": "akash1yeac5tgm4mqwl4fyrqp34s0gq5fy8ugx4fna4z",
            "sifchain": "sif1yeac5tgm4mqwl4fyrqp34s0gq5fy8ugxa03vrn",
            "regen": "regen1yeac5tgm4mqwl4fyrqp34s0gq5fy8ugx8s4x6u",
            "sentinel": "sent1yeac5tgm4mqwl4fyrqp34s0gq5fy8ugxrfgrgh",
            "juno": "juno1yeac5tgm4mqwl4fyrqp34s0gq5fy8ugxwqapty",
            "cheq": "cheqd1yeac5tgm4mqwl4fyrqp34s0gq5fy8ugxksj68f",
            "bitcanna": "bcna1yeac5tgm4mqwl4fyrqp34s0gq5fy8ugxzzwmy2",
            "kava": "kava1fj23cetx2u50su42hzz7cjyrlxkhwu9vlnmh4q",
	    },
        gas_limits = {
            "gaia": "300000",
            "akash": "300000",
            "juno": "500000",
            "bitcanna": "1000000",
            "kava": "100000",
        },
    ),

    "hermes": Relayer(
        relayer_name = "hermes-relayer", 
        bot = Bot(RELAYER_BOT),        
        addresses = {
            "gaia": "cosmos16dc379m0qj64g4pr4nkl7ewak52qy2srf6xl03",
            "osmosis": "osmo16dc379m0qj64g4pr4nkl7ewak52qy2srpp40er",
            "sentinel": "sent16dc379m0qj64g4pr4nkl7ewak52qy2srjpsxt7",
	    },
        gas_limits = {
            "gaia": "300000",
        },
    ),

    "juno": Relayer(
        relayer_name = "juno-relayer", 
        bot = Bot(RELAYER_BOT),        
        addresses = {
            "gaia": "cosmos18xvpj53vaupyfejpws5sktv5lnas5xj274sdwd",
            "osmosis": "osmo18xvpj53vaupyfejpws5sktv5lnas5xj2kwracl",
            "akash": "akash18xvpj53vaupyfejpws5sktv5lnas5xj2nwa2hh",
            "sifchain": "sif18xvpj53vaupyfejpws5sktv5lnas5xj2mglmpx",
            "regen": "regen18xvpj53vaupyfejpws5sktv5lnas5xj2phm3cf",            
            "bitcanna": "bcna18xvpj53vaupyfejpws5sktv5lnas5xj2y9qvxl",            
            "persistence": "persistence1davex4mc526tphx7r86n0v2l5d3npq0gsxkhl8",
	    },
        gas_limits = {
            "gaia": "500000",
            "juno": "500000",
            "bitcanna": "3000000",
        },
    ),

    "omniflixhub": Relayer(
        relayer_name = "omniflixhub-relayer", 
        bot = Bot(RELAYER_BOT),        
        addresses = {
            "gaia": "cosmos1p4zdymjq0jna478v96kjwn8glcuvkmtq234tz5",
            "osmosis": "osmo1p4zdymjq0jna478v96kjwn8glcuvkmtqz2xm5x",
            "akash": "akash1p4zdymjq0jna478v96kjwn8glcuvkmtq82cvmw",
            "sifchain": "sif1p4zdymjq0jna478v96kjwn8glcuvkmtq0v6adl",
            "sentinel": "sent1p4zdymjq0jna478v96kjwn8glcuvkmtq32rjxm",
            "chihuahua": "chihuahua1p4zdymjq0jna478v96kjwn8glcuvkmtqfyc9rk",
            "stargaze": "stars1p4zdymjq0jna478v96kjwn8glcuvkmtq7dzkf9",            
            "juno": "juno1p4zdymjq0jna478v96kjwn8glcuvkmtqurks9g",
            "kichain": "ki1p4zdymjq0jna478v96kjwn8glcuvkmtqmuyyxq",
            "gravity": "gravity1p4zdymjq0jna478v96kjwn8glcuvkmtqwp8n8u",
            "terra": "terra10c7nrsfa29dw2qq38mdue4n8czqdehkf7ts532",
            "crypto": "cro1fvasy2vulcghpcrptckp6p4pwnl6mhpkt4stmj",
	    },
        gas_limits = {
            "gaia": "500000",
            "chihuahua": "3000000",
            "juno": "500000",
            "kichain": "300000",            
        },
    ),
}

low_balances = {}
def multi_run_wrapper(args):
    return query(*args)

def query(relayer_name, chat_id, name, address, rest, denom, limit, id):    
    if relayer_name not in low_balances:
        low_balances[relayer_name] = {}

    if address not in low_balances[relayer_name]:
        low_balances[relayer_name][address] = 0

    url = f'{rest}/cosmos/bank/v1beta1/balances/{address}' #; print(url)
    try:
        req = requests.get(url).json()
    except Exception as e:
        print(f'Query Error: {e}')
        return    

    balance = 0
    if 'balances' not in req:
        print('Error: ', req)        
        return

    for i in req['balances']:
        if i['denom'] == denom:
            balance = int(i['amount'])
            break

    print(f"{name} = {balance}{denom}")

    bot = bots[relayer_name].bot    

    if (balance < int(limit)):
        # print(balance, int(limit))
        bot.send_message(chat_id=chat_id, text=f"Balance of {name}: {balance}{denom}. Consider refilling!\nRelayer: {relayer_name}\nAddr: {address}")                  
        low_balances[relayer_name][address] = balance
        
    if(address in low_balances[relayer_name] and low_balances[relayer_name][address] != 0 and balance > int(limit)):
        bot.send_message(chat_id=chat_id, text=f"Hurray, {relayer_name} {address} is refilled now!")

def main():
    # Reads chains-data file relative to the location of this file.
    root_dir = parent_dir_name(parent_dir_name(os.path.realpath(__file__)))
    chains_data = os.path.join(root_dir, 'chains-data.json')
    chains_data = json.load(open(chains_data))

    p = mp.Pool(mp.cpu_count())    
    
    while True:
        for relayer_name, relayer in bots.items(): 
            print(f"\n{relayer_name}")

            # if gas_limits is not empty, then set the gas limits for the chain
            if relayer.gas_limits != {}:
                for chain, gas_limit in relayer.gas_limits.items():
                    chains_data[chain]["limit"] = gas_limit                       
            
            # resets queries for every new relayer
            queries_to_run = []
            for chain, addr in bots[relayer_name].addresses.items():             
                chain_info = chains_data[chain]                                
                # query(relayer_name, CHAT_ID, chain_info["name"], addr, chain_info["api"], chain_info["denom"], chain_info["limit"], chain_info["id"])
                queries_to_run.append((relayer_name, CHAT_ID, chain_info["name"], addr, chain_info["api"], chain_info["denom"], chain_info["limit"], chain_info["id"]))

            p.map(multi_run_wrapper, queries_to_run)            

        seconds = 10800
        print(f"Pausing for {seconds/60} minutes")
        time.sleep(seconds)


if __name__ == '__main__':
    main()
