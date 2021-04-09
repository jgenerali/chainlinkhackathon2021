#!/usr/bin/python3
import os
from brownie import FriendlyWager, accounts, network, config
import time

# mainnet_eth_usd_address = '0x5f4eC3Df9cbd43714FE2740f5E3616155c5b8419'
# kovan_eth_usd_address = '0x9326BFA02ADD2366b30bacB125260Af641031331'


def main():
    if network.show_active() in ['kovan']:  #, 'rinkeby', 'mainnet', 'mainnet-fork', 'binance-fork', 'matic-fork']:
        dev = accounts.add(os.getenv(config['wallets']['from_key']))
        network.gas_limit(6700000)
        print ('gas_lmiit is: '+str(network.gas_limit()))
        creator = '0x2c3a87EC330768BdcfBe227F8e98B8aE810925C1';
        accepter = '0x66242A1824CE49e5E3f2944f642f3cb9D3305b3e';
        claim_date = 1617753600;
        strike_price = 200050455332; #//2000 + [,50,455,332] =  $2000
        creator_is_long = True;
        total_amount = '0.1 ether';
        #TODO: figure out how to deploy & fund smart contract in one step:
        deployed_object = FriendlyWager.deploy(config['networks'][network.show_active()]['eth_usd_price_feed'],  #AggregatorAddress
                                               creator, accepter, strike_price, claim_date, creator_is_long,
                                               {'from': dev, 'allow_revert': True})
        print('your smart contract address is: '+str(deployed_object.address))
        accounts[0].transfer(deployed_object.address, total_amount); 
        tx=deployed_object.claim({'allow_revert': True})
        print (str(tx))
        print (str(tx.traceback()))

    else:
        print('Please pick a supported network, or fork a chain')
