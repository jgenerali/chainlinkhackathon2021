#!/usr/bin/python3
import os,time,random,re,datetime,math
from brownie import FriendlyWager, accounts, network, config, interface
import discord
from discord.ext import commands,tasks
import sys

import bot_db

#Global variables:
discord_token = os.environ['DISCORD_TOKEN']  #from discord developers->bot page
total_wager_amount = '0.1 ether' 
data_feed_name = 'ETHUSD'
wager_bot_commands = ['help','listdatafeeds','create','cancel','accept','decline','claim','setwallet']
the_gas_limit = 6700000
etherscan_contract_base_url = 'https://kovan.etherscan.io/address/'
etherscan_tx_base_url = 'https://kovan.etherscan.io/tx/'
dev = accounts.add(os.getenv(config['wallets']['from_key']))

client = commands.Bot(command_prefix = '.')
bot_db.createDB()

#Note: 'client' name in @client decorator below corresponds to the variable named client above...
@client.event
async def on_ready():
   auto_claim.start()
   print('Bot is ready.')

@client.command()
async def ping(ctx):
    await ctx.send('pong')

@client.command(aliases=['wagerbot'])
async def _main_handler(ctx,wagerbotcmd,*args):
    #print('here wagerbotcmd='+wagerbotcmd+', args'+str(args)+', locals()='+str(globals()))
    if wagerbotcmd in wager_bot_commands:
      subcmd_func_name='subcmd_'+wagerbotcmd
      await globals()[subcmd_func_name](ctx,args)
    else:
      await ctx.send(f'Unknown command, please try `.wagerbot help`')

#
# Help Subcommand
#
#TODO: redirect the bare ".wagerbot" here  (figure out "Ignoring exception ... discord.ext.commands.errors.MissingRequiredArgument)
async def subcmd_help(ctx,args):
     await ctx.send(f'Welcome to friendly wagerbot\n\n'
                    +f'Commands:\n'
                    +f'      .wagerbot help - this text\n'
                    +f'      .wagerbot listdatafeeds - list of available data feeds\n'
                    +f'      .wagerbot create <Recipient> (above/below) <Strike Price> on <Claim Date>\n'
                    +f'                   - create a new friendly wager with <Recipient>\n'
                    +f'      .wagerbot cancel - cancel wager and refund money if the other party is not accepting...\n'
                    +f'      .wagerbot accept - accept the pending friendly wager invite\n'
                    +f'      .wagerbot decline - decline the pending friendly wager invite\n'
                    +f'      .wagerbot claim <smart_contract_id> - someone from either party needs to call this _on the claim date_ to execute the smart contract\n'
                    +f'      .wagerbot setwallet <wallet_id> - set the wallet id associated with your discord user\n');


#
# Listdatafeeds Subcommand
#
async def subcmd_listdatafeeds(ctx,args):
     await ctx.send(f'ETHUSD TODO')


#
# Create Subcommand
#   .wagerbot create <Invitee> [above/below] <Strike Price> [on] <Date>
#
async def subcmd_create(ctx,args):
     (invitee_text,above_below_text,strike_price_text,on_text,claim_date_text) = args

     #TODO: sanitize input!

     #bail if the caller never set a wallet_id:
     if bot_db.getWalletForUser(ctx.author.id) is None:
       await ctx.send('<@!{}>: You need to set a wallet first using the `.wagerbot setwallet` command first!'.format(ctx.author.id))
       return False

     invitee_id = extract_discord_id(invitee_text)

     #bail if invitee already has a pending invite!
     if bot_db.getPendingInvite(invitee_id) is not None: 
       await ctx.send('<@!{}>: That user already has a pending friendly wager invite. Can you please get them to `accept` or `decline` their pending wager invite and try again?'.format(ctx.author.id))
       return False

     creator_is_long = True if above_below_text.startswith('above') else False
     bot_db.createNewWager(ctx.author.id, extract_discord_id(invitee_text), datetime.date.fromisoformat(claim_date_text), int(strike_price_text), creator_is_long)

     #Now compose and send invitation:
     opposite_direction_text = 'below' if above_below_text.startswith('above') else 'above'
     invitation_text = '{}: Will you accept a friendly wager from <@!{}> that {} will be {} {} on {}? Please Answer by using `.wagerbot accept` or `.wagerbot decline`'.format(invitee_text, ctx.author.id, data_feed_name, opposite_direction_text, strike_price_text, claim_date_text)
     await ctx.send(invitation_text)


#
# Cancel Subcommand
#
async def subcmd_cancel(ctx,args):
     await ctx.send(f'TODO')


#
# Accept Subcommand
#
async def subcmd_accept(ctx,args):
     #0. bail with a message if they never set a walletid
     accepter_wallet_id = bot_db.getWalletForUser(ctx.author.id)
     if accepter_wallet_id is None:
       await ctx.send('<@!{}>: You need to set a wallet first using the `.wagerbot setwallet` command first!'.format(ctx.author.id))
       return False
     #1. determine wager to accept
     wager_row = bot_db.getPendingInvite(ctx.author.id)
     if wager_row is None: 
       await ctx.send('<@!{}>: Couldnt determine the wager to accept!'.format(ctx.author.id))
       return False
     #print ('wager_row is: '+str(wager_row))
     #2. deploy & fund smart contract
     await ctx.send('<@!{}>: OK, Thank you for accepting! Trying to deploy smart contract now, please wait...'.format(ctx.author.id))
     creator_wallet_id = bot_db.getWalletForUser(wager_row['creator_id'])
     deployed_object = deploy_smart_contract(creator_wallet_id,accepter_wallet_id,wager_row['strike_price'],datetime.date.fromisoformat(wager_row['claim_date']),wager_row['creator_is_long'])
     #3. update wager db row
     smart_contract_id = deployed_object.address
     bot_db.updateWagerAccept(wager_row['id'], smart_contract_id)
     #4. emit message with etherscan link to deployed contract
     await ctx.send('<@!{}> <@!{}>: Friendly Wager accepted! A new smart contract was created and deployed: {}/{}'.format(ctx.author.id,wager_row['creator_id'],etherscan_contract_base_url,smart_contract_id))


#
# Decline Subcommand
#
async def subcmd_decline(ctx,args):
     #1. determine wager to decline
     wager_row = bot_db.getPendingInvite(ctx.author.id)
     if wager_row is None: 
       await ctx.send('<@!{}>: Couldnt determine the wager to decline!'.format(ctx.author.id))
       return False
     #2. update wager db row
     bot_db.updateWagerDecline(wager_row['id'])
     #3. emit message:
     await ctx.send('<@!{}> <@!{}>: Friendly Wager declined!'.format(ctx.author.id,wager_row['creator_id']))

#
# Claim Subcommand
#
async def subcmd_claim(ctx,args):
     #A. if no args, check if any claimable contracts for this user for today:
     if len(args) == 0:
       smart_contract_ids=bot_db.getContractsClaimableTodayForUser(ctx.author.id)
       if len(smart_contract_ids) > 0: 
         await ctx.send('<@!{}>: These smart contracts are claimable today: {}'.format(ctx.author.id, str(smart_contract_ids)))
       else:
         await ctx.send('<@!{}>: You dont have any claimable contracts today....'.format(ctx.author.id))
     else:  #B. if an arg, try to call .claim() on it,then send out an eterscan link:
       the_smart_contract_id=args[0]
       #TODO: satanize input!!
       fetched_contract=interface.FriendlyWager(the_smart_contract_id)
       #TODO: check fetched_contract!
       #await ctx.send('<@!{}>: Calling `.claim()` on smart contract `{}`, Please wait...'.format(ctx.author.id,the_smart_contract_id))
       result = fetched_contract.claim({'from': dev})
       await ctx.send('<@!{}>: Called `.claim()` on smart contract `{}`, result: {}'.format(ctx.author.id,the_smart_contract_id,str(result)))
       #TODO: emit etherscan link...

#
# Setwallet Subcommand
#
async def subcmd_setwallet(ctx,args):
     #TODO: sanitize input!
     bot_db.addWalletForUser(ctx.author.id, args[0])
     await ctx.send('<@!{}>: Your wallet is now set to: `{}`'.format(ctx.author.id,args[0]))

#
# Helper func
#
def extract_discord_id(id_text):
    return int(re.findall('(\d+)', id_text)[0])

#
# Helper function that returns a deployed smart contract object:
#
def deploy_smart_contract(_creator_wallet_id,_accepter_wallet_id,_strike_price,_claim_date,_creator_is_long):
    if network.show_active() in ['kovan']:  #, 'rinkeby', 'mainnet', 'mainnet-fork', 'binance-fork', 'matic-fork']:
        dev = accounts.add(os.getenv(config['wallets']['from_key']))
        network.gas_limit(the_gas_limit)
        #print ('gas_lmiit is: '+str(network.gas_limit()))
        creator = _creator_wallet_id
        accepter = _accepter_wallet_id
        #calculate the timestamp for this date:
        claim_date = datetime.datetime.combine(_claim_date, datetime.datetime.min.time()).timestamp()
        #caclculate the number format for the strike price value thats compatible with the chainlink smart contract:
        strike_price=_strike_price*math.pow(10,8)
        creator_is_long = _creator_is_long;
        #TODO: figure out how to deploy & fund smart contract in one step:
        deployed_object = FriendlyWager.deploy(config['networks'][network.show_active()]['eth_usd_price_feed'],  #AggregatorAddress
                                               creator, accepter, strike_price, claim_date, creator_is_long,
                                               {'from': dev, 'allow_revert': True})
        print('your smart contract address is: '+str(deployed_object.address))
        accounts[0].transfer(deployed_object.address, total_wager_amount); 
        return deployed_object
    else:
        print('Please pick a supported network, or fork a chain')
    return False

@tasks.loop(seconds=86400)  #run this daily...
async def auto_claim():
    smart_contract_ids=bot_db.getContractsClaimableToday()
    print('auto_claim(): starting at '+time.ctime()+', smart_contract_ids are: '+str(smart_contract_ids)) 
    for the_smart_contract_id in smart_contract_ids:
       fetched_contract=interface.FriendlyWager(the_smart_contract_id)
       #TODO: check fetched_contract!
       result = fetched_contract.claim({'from': dev})
       #TODO: notify both parties!
       print ('auto_claim(): result for: '+the_smart_contract_id+' was: '+str(result))
    print('auto_claim(): ending at '+time.ctime())


#<-- brownie run entry point...
def main():   

    client.run(discord_token)


