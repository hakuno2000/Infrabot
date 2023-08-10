import random

def getRandomMessage(type, **args):
    if type == "missing_blocks":
        return random.choice([
            f"Probably internet issue. Or hardware issue. Or I dont know",
            f"Are there anyone working on that yet?",
            f"<@{args['user_1']}> <@{args['user_2']}> <@{args['user_3']}> I think you should take a look on it.",
            f"Missing {args['blocks']} blocks now.",
            f"I have to spam in this thread if no one reacts to my message, because I dont know if anyone has noticed this or not.",
            f"{args['blocks']} blocks missed :'(",
        ])