import discord
import asyncio
from datetime import datetime, timedelta
from yaml import load
from random import randint

from database import Database
from pprint import pprint


with open('settings.cfg') as file:
    cfg = load(file)

client = discord.Client()
db = Database(cfg['database'], cfg['table'])
db.create_table()

@client.async_event
def on_ready():
    print('Logged in as')
    print(client.user.name)
    print(client.user.id)
    print('------')

async def calc_last_msg(last_msg):
    mesg_time = datetime.strptime(last_msg, cfg['time_fmt'])
    test_time = datetime.now() - timedelta(seconds=cfg['time_to_wait'])
    return True if mesg_time < test_time else False

# Outputs usernames organized by level
async def levels(count=100):
    results = db.get_all_record()
    print("----------")
    for user in results:
        print("{name} - {xp}".format(name=user[0], xp=user[1]))

@client.event
async def on_message(message):
    # Do not continue if a bot sent the message
    if message.author.bot:
        return

    user = db.get_record(message.author)

    # If no user entry is found in the database
    if not user:
        db.add_record(message.author, str(datetime.now().strftime(cfg['time_fmt'])))
        print("Added {user}".format(user=message.author))

    # If a user exists in the database
    else:
        time_calc = await calc_last_msg(user[2])
        if time_calc:
            db.mod_record(message.author,
                          ["xp", user[1]+randint(15, 25)],
                          ["last_msg", str(datetime.now().strftime(cfg['time_fmt']))])
            print("Updated {user}".format(user=message.author))
        else:
            print("No exp added to {}".format(message.author))

        # Code a thingy to check if user surpassed level threshold
    #print(db.get_record(message.author))

    if message.content.startswith('!levels'):
        await levels()

    if message.content.startswith('!purge'):
        deleted = await client.purge_from(channel=message.channel,before=now_time)
        print('Deleted {} message(s)'.format(len(deleted)))

    if message.mentions:
        msg = [message.author, message.content]
        await client.send_message(message.channel, *msg)
        await client.add_reaction(message, '\U0001F44D')
    if message.content.startswith('!test'):
        counter = 0
        tmp = await client.send_message(message.channel, 'Calculating messages...')
        async for log in client.logs_from(message.channel, limit=100):
            if log.author == message.author:
                counter += 1

        await client.edit_message(tmp, 'You have {} messages.'.format(counter))
    elif message.content.startswith('!sleep'):
        await asyncio.sleep(5)
        await client.send_message(message.channel, 'Done sleeping')

client.run(cfg['token'])
