import subprocess
import re
from multiprocessing import Pool, Process
import json

def multi_run_wrapper(args):
   return export(*args)

def getTX(port, height): # note: use requests.get here? then .json()['result']['block']['data']['txs']
	info = subprocess.run(["curl",f"http://0.0.0.0:{port}/block?height={height}"], stdout=subprocess.PIPE, check = True, stderr=subprocess.PIPE)
	result = subprocess.run(["jq", ".result.block.data.txs"], input = info.stdout, stdout=subprocess.PIPE, stderr=subprocess.PIPE).stdout.decode("utf-8")
	return [height, result]

def export(chainid, port, height):
	for i in range(1, height):
		result = getTX(port, i)
		print(f"{result[0]}:\n{result[1]}")
		value = {
			"height": result[0],
			"txs": json.loads(result[1])
		}
		with open(f"{chainid}.json", "r+") as file:
			data = json.load(file)
			data[f"{chainid}"].append(value)
			file.seek(0)
			json.dump(data, file, indent = 4)

def init(chainid):
	f = open(f"{chainid}.json", "w")
	f.write(f"{{\"{chainid}\": []}}")
	f.close()

def main():
	init("cosmoshub_1")
	init("cosmoshub_2")
	init("cosmoshub_3")

	p = Pool()
	result = p.map(multi_run_wrapper, [
		("cosmoshub_1", 20001, 500042),
		("cosmoshub_2", 30001, 2902002),
		("cosmoshub_3", 40001, 5200791)
	])

main()