import os
import sys
import json
import time
import websocket
from dotenv import load_dotenv
from os.path import dirname as parent_dir_name

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from app import message, checked
from getRandomMessage import getRandomMessage

load_dotenv()

block_missing = 0
thread_id = ""
warned = False

def on_message(ws, message, name, hash):
    data = json.loads(message)
    data = data["result"]["data"]["value"]
    checkUptime(data, name, hash)

def on_error(ws, error):
    print("Error:", error)

def on_close(ws, close_status_code, close_msg):
    print(
        "Connection closed with status code:", close_status_code, "message:", close_msg
    )
    print("Wait for 10s before reconnecting...")
    time.sleep(10)
    
def on_open(ws):
    data = {
        "jsonrpc": "2.0",
        "method": "subscribe",
        "id": 0,
        "params": {"query": "tm.event='NewBlock'"}
    }
    ws.send(json.dumps(data))

def checkUptime(data, name, validator):
    global block_missing, alive, thread_id, warned
    alive = False
    signatures = data["block"]["last_commit"]["signatures"]
    for i in signatures:
        if i["validator_address"] == validator:
            alive = True
            print(f"{name} still alive: {int(data['block']['last_commit']['height']):,}")
            if block_missing != 0:
                if name == "Sei":
                    if block_missing >= 50:
                        message(
                            os.getenv("NOTI"), 
                            f"Hurray, our {name} is up again!", 
                            thread_id
                        )
                        
                if block_missing >= 20:
                    message(
                        os.getenv("NOTI"), 
                        f"Hurray, our {name} is up again!", 
                        thread_id
                    )
                block_missing = 0
            break
    if not alive:
        block_missing = block_missing + 1
        print(f"{name} miss {block_missing} blocks: {int(data['block']['last_commit']['height']):,}")
        
        if name == "Sei":
            if block_missing >= 50 and block_missing % 50 == 0:
                if block_missing == 50:
                    res = message(os.getenv("NOTI"), f"Our {name} missing blocks")
                    thread_id = res.get("ts")
                    message(
                        os.getenv("NOTI"),
                        f"{block_missing} blocks missing now. React with ✅ and I will stop alerting in every 500 blocks.",
                        thread_id,
                    )
                else:
                    users_checked = checked(os.getenv("NOTI"), thread_id)
                    if (users_checked == None) or (
                        (os.getenv("MINH") not in users_checked)
                        and (os.getenv("DU") not in users_checked)
                        and (os.getenv("LONG") not in users_checked)
                    ):
                        message(
                            os.getenv("NOTI"),
                            getRandomMessage(
                                "missing_blocks",
                                user_1=os.getenv("MINH"),
                                user_2=os.getenv("LONG"),
                                user_3=os.getenv("DU"),
                                blocks=block_missing,
                            ),
                            thread_id,
                        )
                    elif block_missing % 500 == 0:
                        message(
                            os.getenv("NOTI"),
                            f"Our {name} still missing {block_missing} blocks",
                            thread_id,
                        )
        else: 
            if block_missing >= 20 and block_missing % 20 == 0:
                if block_missing == 20:
                    res = message(os.getenv("NOTI"), f"Our {name} missing blocks")
                    thread_id = res.get("ts")
                    message(
                        os.getenv("NOTI"),
                        f"{block_missing} blocks missing now. React with ✅ and I will stop alerting in every 500 blocks.",
                        thread_id,
                    )
                else:
                    users_checked = checked(os.getenv("NOTI"), thread_id)
                    if (users_checked == None) or (
                        (os.getenv("MINH") not in users_checked)
                        and (os.getenv("DU") not in users_checked)
                        and (os.getenv("LONG") not in users_checked)
                    ):
                        message(
                            os.getenv("NOTI"),
                            getRandomMessage(
                                "missing_blocks",
                                user_1=os.getenv("MINH"),
                                user_2=os.getenv("LONG"),
                                user_3=os.getenv("DU"),
                                blocks=block_missing,
                            ),
                            thread_id,
                        )
                    elif block_missing % 500 == 0:
                        message(
                            os.getenv("NOTI"),
                            f"Our {name} still missing {block_missing} blocks",
                            thread_id,
                        )


if __name__ == "__main__":
    chain = sys.argv[1]
    # Reads chains-data file relative to the location of this file.
    root_dir = parent_dir_name(parent_dir_name(os.path.realpath(__file__)))
    chains_data = os.path.join(root_dir, "chains-data.json")
    chains_data = json.load(open(chains_data))
    chainData = chains_data[chain]
    websocket_url = chainData["rpc"].replace("https://", "wss://") + "/websocket"

    # websocket.enableTrace(True)
    while True:
        ws = websocket.WebSocketApp(
            websocket_url,
            on_open=on_open,
            on_message=lambda ws, msg: on_message(ws, msg, chainData["name"], chainData["hash"]),
            on_error=on_error,
            on_close=on_close,
        )
        ws.run_forever()