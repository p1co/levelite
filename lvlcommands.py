from datetime import datetime, timedelta
from random import randint

from helper import Helper

class Commands(Helper):
    def __init__(self, discord, client, cfg_loc):
        Helper.__init__(self, cfg_loc)
        self.discord = discord
        self.client = client

    ########################
    #       Commands       #
    ########################

    async def setxp(self, message):
        if message.mentions:
            target = message.mentions[0]
            if target.bot:
                await self.client.send_message(message.channel,
                                               "Bots don't need exp.")
                return
        else:
            return
    
        msg_split = message.content.split()
        if len(msg_split) != 3:
            await self.client.send_message(
                    message.channel,
                    "Usage: !setxp @target numeric_value")
            return
        elif not msg_split[2].isdigit():
            await self.client.send_message(
                    message.channel,
                    "ERROR: XP is a number .. people today.")
            return
        else:
            xp_to_set = msg_split[2]
            self.db.mod_record(target, ["xp", xp_to_set])
            msg = "Set {plr}'s xp to {xp}.".format(
                    plr=target.mention,
                    xp=xp_to_set)
            await self.client.send_message(message.channel, msg)
        return
    
    async def levels(self, message):
        msg = "Go check **{srv}**'s leaderboard: <{url}>".format(
                srv=message.server.name,
                url=self.cfg['leaderboard_url'])
        em = self.discord.Embed(description=msg, colour=0x000FF)
        em.set_author(name='', icon_url=message.server.icon_url)
        await self.client.send_message(message.channel, embed=em)
        return
    
    async def rank(self, message):
        player = message.author
        
        # check if there's a mention of another player
        if message.mentions:
            player = message.mentions[0]
            if player.bot:
                return
    
        u_stat = self.user_data(player)
        # if a player does not exist in the db
        if not u_stat:
            await self.client.send_message(
                    message.channel,
                    "User does not exist in levels database.")
            return

        
        embed = self.discord.Embed(title='', colour=int('008cba', 16))
        embed.add_field(name='Rank',
                        value='{}/{}'.format(u_stat['rank'],
                                             u_stat['user_count']),
                        inline=True)
        embed.add_field(name='Lvl.', value=u_stat['level'], inline=True)
        embed.add_field(name='Exp.',
                        value='{}/{} (tot. {})'.format(u_stat['xp_in_lvl'],
                                                       u_stat['xp_next_lvl'],
                                                       u_stat['xp']),
                        inline=True)
        embed.set_author(name=player.name, icon_url=player.avatar_url)
        embed.set_footer(text=message.server.name,
                         icon_url=message.server.icon_url)
        await self.client.send_message(message.channel, embed=embed)
        return
   

    #######################
    #     Calculators     #
    #######################


    # Compare last user's message timestamp to
    # current time minus admin set frequency
    async def calc_last_msg(self, last_msg):
        mesg_time = datetime.strptime(last_msg, self.cfg['time_fmt'])
        test_time = datetime.now() - timedelta(seconds=self.cfg['time_to_wait'])
        return mesg_time < test_time
    
    #############################
    #    Player Manipulation    #
    #############################

    async def create_player(self, player, role):
        self.db.add_record(player.id,
                           player,
                           role,
                           player.display_name,
                           player.discriminator,
                           player.avatar_url.rsplit('.',1)[0]+".png",
                           str(datetime.now().strftime(self.cfg['time_fmt'])))
        print("Added {user}, UID: {uid}".format(user=player, uid=player.id))
    
    # update player info
    async def mod_player(self, player, user):
        # Check if message sent outside out of bounds time
        last_msg = user['last_msg']
        time_calc = self.calc_last_msg(last_msg)
        xp = user['xp']

        if time_calc:
            xp += randint(15, 25)
            last_msg = str(datetime.now().strftime(self.cfg['time_fmt']))
            print("Updated {plr}".format(plr=player))
        else:
            print("No exp added to {plr}".format(plr=player))
    
        self.db.mod_record(player,
                      ["display", player.display_name],
                      ["avatar", player.avatar_url.rsplit('.',1)[0]+".png"],
                      ["disc", player.discriminator],
                      ["xp", xp],
                      ["last_msg", last_msg])
    
