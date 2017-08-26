import os
from jinja2 import Environment, FileSystemLoader

import cherrypy
from helper import Helper

class Server(Helper):
    def __init__(self):
        Helper.__init__(self)
        self.PATH = os.path.dirname(os.path.abspath(__file__))
        self.TEMPLATE_ENVIRONMENT = Environment(
            autoescape=False,
            loader=FileSystemLoader(os.path.join(self.PATH, 'templates')),
            trim_blocks=False)
    
    def render_template(self, template_filename, context):
        return self.TEMPLATE_ENVIRONMENT.get_template(template_filename).render(context)

    def get_users(self):
        return self.db.get_all_record(99)

    def create_index_html(self, results):
        context = { 'results': results }
        return self.render_template('leaderboard.html', context)
    
    def jinja2_main(self):
        records = self.get_users()
        results = []
        for user in records:
            results.append(self.convert_user(user))
        return self.create_index_html(results)
