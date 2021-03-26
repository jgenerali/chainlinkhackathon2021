import discord
from discord.ext import commands
import random
import os

client = commands.Bot(command_prefix = '.')

#Note: 'client' name in @client decorator below corresponds to the variable named client above...
@client.event
async def on_ready():
   print('Bot is ready.')

@client.command()
async def ping(ctx):
    await ctx.send('pong')

@client.command(aliases=['wagerbot'])
async def _main_handler(ctx,wagerbotcmd,*args):
  
    print('here wagerbotcmd='+wagerbotcmd+', args'+str(args)+', locals()='+str(globals()))
    if wagerbotcmd in ['help','listdatafeeds','create','cancel','accept','claim']:
      subcmd_func_name='subcmd_'+wagerbotcmd
      await globals()[subcmd_func_name](ctx,args)
    else:
      await ctx.send(f'Unknown command, please try .wagerbot help')


#
# Help Subcommand
#
#TODO: redirect the bare ".wagerbot" here  (figure out "Ignoring exception ... discord.ext.commands.errors.MissingRequiredArgument)
async def subcmd_help(ctx,args):
     await ctx.send(f'Welcome to friendly wagerbot\n\n'
                    +f'Commands:\n'
                    +f'      .wagerbot help - this text\n'
                    +f'      .wagerbot listdatafeeds - list of data available data feeds\n'
                    +f'      .wagerbot create <Amount> <Recipient> <Data Feed Name> (above/below) <Strike Price> [on] <Date>\n'
                    +f'                   - create a new friendly wager with <Recipient>\n'
                    +f'      .wagerbot cancel - cancel wager and refund money if the other party is not accepting...\n'
                    +f'      .wagerbot accept <Sender> - accept the friendly wager from <Sender>\n'
                    +f'      .wagerbot claim - someone from either party needs to call this _on the strike date_ to execute the smart contract\n');


#
# Listdatafeeds Subcommand
#
async def subcmd_listdatafeeds(ctx,args):
     await ctx.send(f'ETHUSD')
     #TODO:...


#
# Create Subcommand
#
async def subcmd_create(ctx,args):
     await ctx.send(f'ethusd')
     #todo:...


#
# Cancel Subcommand
#
async def subcmd_cancel(ctx,args):
     await ctx.send(f'ETHUSD')
     #TODO:...


#
# Accept Subcommand
#
async def subcmd_accept(ctx,args):
     print('subcmd_accept: args[0]='+args[0])
     await ctx.send(f'ETHUSD, args[0]='+str(args[0]))
     #TODO:...


#
# Claim Subcommand
#
async def subcmd_claim(ctx,args):
     await ctx.send(f'CLAIM')
     #TODO:...

#from discord developers->bot page:
token = os.environ['DISCORD_TOKEN']

client.run(token)


