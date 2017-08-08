import os
from jinja2 import Environment, FileSystemLoader

import cherrypy

class Server(object):
    def __init__(self, db, cmd):
        self.db = db
        self.cmd = cmd
        self.PATH = os.path.dirname(os.path.abspath(__file__))
        self.TEMPLATE_ENVIRONMENT = Environment(
            autoescape=False,
            loader=FileSystemLoader(os.path.join(self.PATH, 'templates')),
            trim_blocks=False)
    
    
    def render_template(self, template_filename, context):
        return self.TEMPLATE_ENVIRONMENT.get_template(template_filename).render(context)
   

    def get_users(self):
        return self.db.get_all_record('display, disc, avatar, xp, role, rep')

    def convert_user(self, user):
        # Calculate players level and percent of exp in curr elvel
        xp_lvl = self.cmd.player_level(user[3])
        next_lvl = self.cmd.calc_level_xp(xp_lvl[0])
        if xp_lvl[1] == 0:
            xp_pct = 0
        else:
            xp_pct = 100 * float(xp_lvl[1])/float(next_lvl)
        return {
              "role":user[4],
              "level":xp_lvl[0],
              "name":user[0],
              "disc":user[1],
              "xp":user[3],
              "xp_in_lvl":xp_lvl[1],
              "xp_pct":xp_pct,
              "xp_next_lvl":next_lvl,
              "avatar":user[2],
              "rep":user[5]}

    
    def create_index_html(self, results):
        context = { 'results': results }
        return self.render_template('leaderboard.html', context)
    
    
    def jinja2_main(self):
        records = self.get_users()
        results = []
        for user in records:
           results.append(self.convert_user(user))
        return self.create_index_html(results)
