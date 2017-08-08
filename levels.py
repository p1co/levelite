import asyncio
import discord
import cherrypy
import os

from lvlcommands import Commands
from server import Server

client = discord.Client()

TEST = False

cmd = Commands(discord, client, cfg_loc="settings.cfg")
cfg = cmd.cfg
db = cmd.db
srv = Server(db, cmd)

class display_levels(object):
    @cherrypy.expose
    def index(self):
        return srv.print_this_motherfucker()

@client.async_event
async def on_ready():
    # Retrieve server roles
    roles = [x.name for x in client.get_server(str(cfg['server_id'])).role_hierarchy]
    cmd.add_roles(roles[:-1])

    # Create/initialize database
    print("Attempting to create table and add default role: ", cmd.get_role(0))
    db.create_table(cmd.get_role(0))
    print('Logged in as {user}, ID: {uid}\n------'.format(
        user=client.user.name,
        uid=client.user.id))

    cherrypy.config.update(config="global.conf")
    cherrypy.tree.mount(display_levels(), '/', config="app.conf")
    cherrypy.engine.start()

# Announce to the chat room the level up
async def print_congrats(player, channel, lvl):
    msg = "GG {plr}, you just advanced to **level {lvl}**!".format(
            plr=player.mention,
            lvl=lvl)
    await client.send_message(channel, msg)

# async def translate_level(player):
#     return await cmd.player_level(int([x for x in db.get_record(player, "xp")][0]))[0]

async def action_message(message):
    player = message.author
    user = db.get_record(player)
    if not user:
        await cmd.create_player(player, cmd.get_role(0))
    else:
        # temp_lvl = await translate_level(player)
        await cmd.mod_player(player, user)
        # curr_lvl = await translate_level(player)

#         if curr_lvl > temp_lvl:
            # if not TEST:
#                 await print_congrats(player, message.channel, curr_lvl)


@client.event
async def on_message(message):
    # Do not continue if a bot sent the message
    if message.author.bot:
        return

    if message.content.startswith('!levels'):
        await cmd.levels(message)

    # Prints one record
    elif message.content.startswith('!rank'):
        await cmd.rank(message)

    # Set xp for one player
    elif message.content.startswith('!setxp'):
        await cmd.setxp(message)

    # Create a new record or modify an existing record with exp
    else:
        await action_message(message)

client.run(cfg['token'])
