import discord
import asyncio
import requests
import json
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
def calc_last_msg(last_msg):
    mesg_time = datetime.strptime(last_msg, cfg['time_fmt'])
    test_time = datetime.now() - timedelta(seconds=cfg['time_to_wait'])
    return mesg_time < test_time

# Outputs usernames organized by level
async def get_levels():
    results = db.get_all_record(thing="rowid, author")
    score = []
    for user in results:
        u_stat = await user_data(user[1])

        u_string = (':small_blue_diamond: {rank:<5}'
                    '{plr:30} {levels:30}  '
                    'Level **{lvl}**'.format(
                        rank=u_stat['rank'],
                        plr='**{}** #{}'.format(u_stat['name'], u_stat['disc']),
                        levels='{}/{} **XP** \[{}\]'.format(
                            u_stat['xp_in_current_level'],
                            u_stat['xp_until_next_level'],
                            u_stat['xp']),
                        lvl=u_stat['lvl']))

        score.append(u_string)
    return score

async def user_data(plr):
    user = db.get_record(plr)
    if not user:
        return False

    xp_lvl = player_level(user['xp'])

    report = {"author":user['author'],
              "avatar":user['avatar'],
              "disc":user['disc'],
              "name":user['display'],
              "lvl":xp_lvl[0],
              "xp":user['xp'],
              "xp_in_current_level":xp_lvl[1],
              "xp_until_next_level":calc_level_xp(xp_lvl[0]),
              "rank":db.find_user_rank(user['author'])[0],
              "count":db.count_recs()}

    return report

# Calculate how much exp is needed to reach a level
def calc_level_xp(lvl):
    return 5*(lvl**2)+50*lvl+100

# Calculate the player level
def player_level(xp):
    remaining_xp = int(xp)
    level = 0
    while remaining_xp >= calc_level_xp(level):
        remaining_xp -= calc_level_xp(level)
        level += 1
    return (level, remaining_xp)

def create_player(player, nowdate):
    db.add_record(player,
                  player.display_name,
                  player.discriminator,
                  player.avatar_url,
                  str(nowdate.strftime(cfg['time_fmt'])))
    print("Added {user}".format(user=player))

# Announce to the chat room the level up
async def print_congrats(player, channel):
    await client.send_message(channel, str(player) + " leveled up!!!!")

# update player info
async def mod_player(player, user, nowdate, channel):
    # Check if message sent outside out of bounds time
    last_msg = user['last_msg']
    time_calc = calc_last_msg(last_msg)

    xp = user['xp']
    lvl = player_level(xp)[0]
    if time_calc:
        grant_xp = randint(15, 25)
        xp = xp + grant_xp
        temp_lvl = player_level(xp)[0]
        if int(temp_lvl) > int(lvl):
            await print_congrats(player, channel)
        last_msg = str(nowdate.strftime(cfg['time_fmt']))
        print("Updated {plr}".format(plr=player))
    else:
        print("No exp added to {plr}".format(plr=player))

    db.mod_record(player,
                  ["display", player.display_name],
                  ["avatar", player.avatar_url],
                  ["disc", player.discriminator],
                  ["xp", xp],
                  ["last_msg", last_msg])

async def action_message(message):
    player = message.author
    nowdate = datetime.now()
    user = db.get_record(player)
    if not user:
        create_player(player, nowdate)
    else:
        await mod_player(player, user, nowdate, message.channel)

async def setxp(message):
    if message.mentions:
        target = message.mentions[0]
    else:
        return

    msg_split = message.content.split()
    if len(msg_split) != 3:
        await client.send_message(message.channel,
                                  "Usage: !setxp @target numeric_value")
        return
    elif not msg_split[2].isdigit():
        await client.send_message(message.channel,
                                  "ERROR: XP is a number .. people today.")
        return
    else:
        xp_to_set = msg_split[2]
        db.mod_record(target, ["xp", xp_to_set])
        await client.send_message(
                message.channel,
                "Set " + str(target) + "'s xp to " + xp_to_set + ".")
    return


async def levels(message):
    title = "**" + message.server.name + "**" + " leaderboard:"
    msg_fmt = await get_levels()
    msg = "\n".join(msg_fmt)
    em = discord.Embed(title=title, description=msg, colour=0x000FF)
    em.set_author(name='', icon_url=message.server.icon_url)
    await client.send_message(message.channel, embed=em)
    return


async def rank(message):
    player = message.author
    if message.mentions:
        player = message.mentions[0]

    u_stat = await user_data(player)

    response = ('**{name}**\'s rank > '
                '**LEVEL {lvl}** | '
                '**XP {xp_in_current_level}/{xp_until_next_level}** | '
                '**TOTAL XP {total_xp}** | '
                '**Rank {rank}/{user_count}**'.format(
            name=u_stat['name'],
            lvl=u_stat['lvl'],
            xp_in_current_level=u_stat['xp_in_current_level'],
            xp_until_next_level=u_stat['xp_until_next_level'],
            total_xp=u_stat['xp'],
            rank=u_stat['rank'],
            user_count=u_stat['count']))

    print(response)

    em = discord.Embed(description=response, colour=0x000FF)
    em.set_author(name='', icon_url=message.server.icon_url)
    await client.send_message(message.channel, embed=em)
    return


@client.event
async def on_message(message):
    # Do not continue if a bot sent the message
    if message.author.bot:
        return

    ################
    ### commands ###
    ################

    if message.content.startswith('!levels'):
        await levels(message)

    # Returns the total number of stored records
    elif message.content.startswith('!count'):
        await client.send_message(message.channel, str(db.count_recs()))

    # Prints one record
    elif message.content.startswith('!rank'):
        await rank(message)

    # Set xp for one player
    elif message.content.startswith('!setxp'):
        await setxp(message)

    # Create a new record or modify an existing record with exp
    else:
        await action_message(message)

client.run(cfg['token'])
