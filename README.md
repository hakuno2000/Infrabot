# RWRMaAS
Infra monitoring bot

## add a new chain
To add new chain, add **both** chain's data in `chain-data.json` and add worker in `Services/validator.target`. Below is an example of adding Passage:
 - Adding to worker:
 <img width="1232" alt="image" src="https://user-images.githubusercontent.com/49267398/199881184-eb29b28b-87db-4038-ae17-a36486a0f502.png">

 - Adding chain's data:

![image](https://github.com/notional-labs/Infrasmonitor/assets/49267398/6a54a984-f7fd-4bd6-a767-c9c1da653a69)

with `hash` is the validator's hash so that the bot can check if this validator is in the signatures list or not. Then restart bot: `systemctl restart validator.target`.
