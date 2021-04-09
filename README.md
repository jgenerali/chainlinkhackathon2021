# chainlinkhackathon2021

## Friendly Wager Discord Bot

## Project Description (200 words):
Using Discord bot commands, two parties can enter into a friendly wager on an asset price at a future date. One party will be long, and the other short on a strike price of some asset. If both parties accept the wager, the bot will create and deploy a smart contract with the relevant info (strike price, claim date etc.) A method named `.claim()` on the smart contract needs to be called anytime on the agreed upon date, to determine the winner and dispense the funds. It can be called by either party directly, or by bot commands. Also, the bot has a daily recurring task to call the method sometime on the appropriate date. An example of creating a new wager invite is:
```
.wagerbot create @otheruser above 2000 on 2021-04-09
```
The currently supported bot commands are:
```
                          .wagerbot help - this tex
                          .wagerbot listdatafeeds - list of available data feeds
                          .wagerbot create <Recipient> (above/below) <Strike Price> on <Claim Date>
                                       - create a new friendly wager with <Recipient>
                          .wagerbot cancel - cancel wager and refund money if the other party is not accepting...
                          .wagerbot accept - accept the pending friendly wager invite
                          .wagerbot decline - decline the pending friendly wager invite
                          .wagerbot claim <smart_contract_id> - someone from either party needs to call this _on the claim date_ to execute the smart contract
                          .wagerbot setwallet <wallet_id> - set the wallet id associated with your discord user
```

## Usage:
```
docker run -d -e WEB3_INFURA_PROJECT_ID=58610e43REDACTED0e21058d2fb -e PRIVATE_KEY=189c2ab5318bc6b9dREDACTEDb850c59fdf939b7c194c2 -e DISCORD_TOKEN=NzkwMjkxMTQwODA1MDAxMjE3REDACTEDtnD7Rg_OgTAeHUZA -v $PWD:/mnt -it ivans3/wagerbot:latest
```

## Environment Variables:
Name | Description
--- | --- 
`DISCORD_TOKEN` |  from discord developers->bot page
`WEB3_INFURA_PROJECT_ID` | used to broadcast transactions 
`PRIVATE_KEY` | used to deploy and fund smart contracts

## 5 Minute Video Demo:
TODO
