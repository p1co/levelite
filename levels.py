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
    print('Logged in as {user}, ID: {uid}\n------'.format(
        user=client.user.name,
        uid=client.user.id))

# Compare last user's message timestamp to
# current time minus admin set frequency
async def calc_last_msg(last_msg):
    mesg_time = datetime.strptime(last_msg, cfg['time_fmt'])
    test_time = datetime.now() - timedelta(seconds=cfg['time_to_wait'])
    return mesg_time < test_time

# Outputs usernames organized by level
async def levels(srv, count=100):
    results = db.get_all_record()
    print("-----{}-----".format(srv))
    score = ["{} - {}".format(user[0], user[1]) for user in results]
    return score

@client.event
async def on_message(message):
    # Do not continue if a bot sent the message
    if message.author.bot:
        return

    # Capture time message received
    nowdate = datetime.now()

    # Retrieve a user record if it exists
    user = db.get_record(message.author)

    # If no user record is found in the database
    if not user:
        db.add_record(message.author,
                      str(nowdate.strftime(cfg['time_fmt'])))
        print("Added {user}".format(user=message.author))

    # If a user record exists in the database
    else:
        time_calc = await calc_last_msg(user[2])
        if time_calc:
            db.mod_record(message.author,
                          ["xp", user[1]+randint(15, 25)],
                          ["last_msg", str(nowdate.strftime(cfg['time_fmt']))])
            print("Updated {user}".format(user=message.author))
        else:
            print("No exp added to {}".format(message.author))

        # Code a thingy to check if user surpassed level threshold

    # Prints organized-by-level user rankings
    if message.content.startswith('!levels'):
        msg = await levels(message.server.name)
        await client.send_message(message.channel, "\n".join(msg))

client.run(cfg['token'])
