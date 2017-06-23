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
    score = ["{} - {}".format(user[0], user[4]) for user in results]
    return score

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

counter = 0
@client.event
async def on_message(message):
    global counter
    counter += 1
    if counter%15 == 0: 
        msg = await levels(message.server.name)
        print("\n".join(msg))

    # Do not continue if a bot sent the message
    if message.author.bot:
        return

    player = message.author

    # Capture time message received
    nowdate = datetime.now()

    # Retrieve a user record if it exists
    user = db.get_record(player)

    # If no user record is found in the database
    if not user:
        db.add_record(player,
                      player.display_name,
                      player.discriminator,
                      player.avatar_url,
                      str(nowdate.strftime(cfg['time_fmt'])))
        print("Added {user}".format(user=player))

    # If a user record exists in the database
    else:
        # update player info
        db.mod_record(player,
                      ["display", player.display_name],
                      ["avatar", player.avatar_url],
                      ["disc", player.discriminator],
                      ["level", player_level(user['xp'])[0]])

        # Check if message sent outside out of bounds time
        time_calc = await calc_last_msg(user['last_msg'])
        if time_calc:
            db.mod_record(player,
                          ["xp", user['xp']+randint(15, 25)],
                          ["last_msg", str(nowdate.strftime(cfg['time_fmt']))])
            print("Updated {user}".format(user=player))
        else:
            print("No exp added to {plr}".format(plr=player))

        # Code a thingy to check if user surpassed level threshold

    if message.content.startswith('!levels'):
        title = "**" + message.server.name + "**" + " leaderboard:"
        msg_fmt = await levels(message.server.name)
        msg = "\n".join(msg_fmt)
        em = discord.Embed(title=title, description=msg, colour=0x000FF)
        em.set_author(name='', icon_url=message.server.icon_url)
        await client.send_message(message.channel, embed=em)

    if message.content.startswith('!count'):
        await client.send_message(message.channel, str(db.count_recs()))

#@command(pattern="(^!rank$)|(^!rank <@!?[0-9]*>$)",
#         description="Get a player info and rank")
    if message.content.startswith('!rank'):
        if message.mentions:
            player = message.mentions[0]
        plr = db.get_record(player)
        if plr == None:
            return

        xp = int(plr['xp'])
        player_lvl = plr['level']
        lvl_xp = calc_level_xp(player_lvl)
        next_lvl_xp = calc_level_xp(player_lvl+1)

#        print("xp {}\nlvl {}\nremain lvl xp {}\nnext lvl_xp {}".format(xp, player_lvl, lvl_xp[1], next_lvl_xp))

        response = '{auth} : **{name}**\'s rank > **LEVEL {lvl}** | **XP {remain_lvl_xp}/{next_lvl_xp}** '\
            '| **TOTAL XP {tot_xp}** | **Rank {rank}/{plr_count}**'.format(
                auth=message.author,
                name=player.name,
                lvl=player_lvl,
                remain_lvl_xp=lvl_xp,
                next_lvl_xp=next_lvl_xp,
                tot_xp=plr['xp'],
                rank=777,
                plr_count= db.count_recs()
                )        
        print(response)
        em = discord.Embed(description=response, colour=0x000FF)
        em.set_author(name='', icon_url=message.server.icon_url)
        await client.send_message(message.channel, embed=em)

    if message.content.startswith('!setxp'):
        if message.mentions:
            target = message.mentions[0]
        else:
            return

        msg_split = message.content.split()
        if len(msg_split) > 3:
            return
        else:
            xp_to_set = msg_split[2]
        db.mod_record(target, ["xp", xp_to_set])
        await client.send_message(message.channel, "Set " + str(target) + "'s xp to " + xp_to_set + ".")

client.run(cfg['token'])
