import os
from slack_bolt import App
from dotenv import load_dotenv

load_dotenv()

# Initializes your app with your bot token and signing secret
app = App(
    token=os.getenv("BOT_OAUTH_TOKEN"),
    signing_secret=os.getenv("SIGNING_SECRET"),
)

def checked(channel, ts):
    res = app.client.reactions_get(channel=channel ,timestamp=ts)
    try:
        res = res["message"]["reactions"]
        for emojis in res:
            if emojis["name"] == "white_check_mark":
                return emojis["users"]
        return None
    except:
        return None

def message(channel, message, thread=None):
    if type(message) is str:
        if not thread:
            res = app.client.chat_postMessage(channel=channel, text=message)
            return res
        else:
            res = app.client.chat_postMessage(
                channel=channel, thread_ts=thread, text=message
            )
            return res
    elif type(message) is list:
        if not thread:
            res = app.client.chat_postMessage(channel=channel, attachments=message)
            return res
        else:
            res = app.client.chat_postMessage(
                channel=channel, thread_ts=thread, attachments=message
            )
            return res

@app.event("reaction_added")  # check if the message is checked
def reaction(event, say):
    if event.get("item").get("type") == "message":
        print(
            event.get("reaction"),
        )
        print(event)
        message = app.client.conversations_history(
            channel=event["item"]["channel"],
            inclusive=True,
            oldest=event["item"]["ts"],
            limit=1,
        )
        # print(res)
        message = message["messages"][0]["text"]
        if "missing blocks" in message and event["reaction"] == "white_check_mark":
            say(
                blocks = [
                    {
                        "type": "section",
                        "text": {
                            "type": "mrkdwn",
                            "text": f"Saw that <@{event['user']}> reacted with ✅. I will pause alerting for every 500 blocks.",
                        },
                    }
                ],
                thread_ts = event["item"]["ts"]
            )
            return (event["item"]["ts"], True)
        

# Start your app
if __name__ == "__main__":
    app.start(port=int(os.environ.get("PORT", 3000)))

# # Listens to incoming messages that contain "hello"
# # To learn available listener method arguments,
# # visit https://slack.dev/bolt-python/api-docs/slack_bolt/kwargs_injection/args.html
# @app.message("hello")
# def message_hello(message, say):
#     print(message)
#     # say() sends a message to the channel where the event was triggered
#     say(
#         blocks=[
#             {
#                 "type": "section",
#                 "text": {"type": "mrkdwn", "text": f"Hey there <@{message['user']}>!"},
#                 "accessory": {
#                     "type": "button",
#                     "text": {"type": "plain_text", "text": "Click Me"},
#                     "action_id": "button_click",
#                 },
#             }
#         ],
#         text=f"Hey there <@{message['user']}>!",
#     )


# @app.action("button_click")
# def action_button_click(body, ack, say):
#     # Acknowledge the action
#     ack()
#     say(f"<@{body['user']['id']}> clicked the button")