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

now_time = datetime.now()

@client.event
async def on_message(message):
    if not db.get_record(message.author):
        db.add_record(message.author, datetime.now())
        print("Added {user}".format(user=message.author))
    else:
        db.mod_record(message.author, "xp", randint(15, 25))
        db.mod_record(message.author, "last_msg", datetime.now())
        print("Updated {user}".format(user=message.author))
    print(db.get_record(message.author))

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
