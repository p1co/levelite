import asyncio
from yaml import load
from database import Database

class Helper(object):
    def __init__(self, cfg_loc):
        self.roles = {}
        self.cfg = self.load_cfg(cfg_loc)
        self.db = Database(self.cfg['database'], self.cfg['table'])

    def load_cfg(self, cfg_loc):
        with open(cfg_loc) as cfg_file:
            return load(cfg_file)

    def user_data(self, plr):
        user = self.db.get_record(plr)
        if not user:
            return False
    
        # Calculate players level and percent of exp in curr elvel
        xp_lvl = self.player_level(user['xp'])
        next_lvl = self.calc_level_xp(xp_lvl[0])
        if xp_lvl[1] == 0:
            xp_pct = 0
        else:
            xp_pct = int(next_lvl/xp_lvl[1])*100

        return {
              "uid":user['uid'],
              "author":user['author'],
              "role":user['role'],
              "level":xp_lvl[0],
              "name":user['display'],
              "disc":user['disc'],
              "xp":user['xp'],
              "xp_in_lvl":xp_lvl[1],
              "xp_pct":xp_pct,
              "xp_next_lvl":next_lvl,
              "avatar":user['avatar'],
              "last_msg":user['last_msg'],
              "rank":self.db.find_user_rank(user['author'])[0],
              "user_count":self.db.count_recs(),
              "rep":user['rep']}


    # Calculate how much exp is needed to reach a level
    def calc_level_xp(self, lvl):
        return 5*(lvl**2)+50*lvl+100
    
    # Calculate the player level
    def player_level(self, xp):
        print("player_level() -> ",xp)
        remaining_xp = int(xp)
        level = 0
        remaining = self.calc_level_xp(level)
        while remaining_xp >= remaining:
            asyncio.sleep(0)
            remaining_xp -= self.calc_level_xp(level)
            level += 1
        return (level, remaining_xp)
   
    def add_roles(self, roles):
        roles.reverse()
#         tasks = {self.roles[role]: roles[role].strip() for role in range(len(roles))}
#         await asyncio.wait(tasks)
        for role in range(len(roles)):
            self.roles[role] = roles[role].strip()

    def get_role(self, rid):
        return self.roles[rid]
