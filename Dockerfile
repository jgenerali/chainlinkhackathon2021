FROM faucet/python3

#Install "ganache" for "brownie console...":
RUN apk add -U nodejs npm
RUN npm install -g ganache-cli
#Install web3 and brownie:
RUN apk add -U gcc python3-dev musl-dev linux-headers
RUN pip3 install web3 
RUN pip3 install eth-brownie
#Install discord stuff:
RUN pip3 install discord

COPY chainlink chainlink
WORKDIR /chainlink
CMD python3 -u /usr/bin/brownie run scripts/friendly_wager_scripts/bot_main.py --network kovan



