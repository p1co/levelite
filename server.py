import cherrypy

class Server(object):
    def __init__(self, db, cmd):
        self.db = db
        self.cmd = cmd
        self.image_size=50

    def print_this_motherfucker(self):
        records = self.db.get_all_record()

        all_records = []
        for record in range(len(records)):
            all_records.append(self.addtags(records[record], record))

        top = """<html> <head> <link href="static/style.css" type="text/css" rel="stylesheet" /> <link href="https://mee6.xyz/static/css/bootstrap.css" type="text/css" rel="stylesheet" /> </head> <body> <div class="divTable paleBlueRows"> <div class="container"> <div class="row">
              """
        bot = "\n</div></div></div>\n</body>\n</html>"
    
        return top+"\n".join(all_records)+"\n"+bot

    def addtags(self, item, rank):
        print(item)
        xp_lvl = self.cmd.player_level(item[5])
        print("xp level list: ",xp_lvl)
        print("curr xp left: ",xp_lvl[1])
        xp_thresh_to_next_lvl = self.cmd.calc_level_xp(xp_lvl[0])
        xp_pct = int(xp_thresh_to_next_lvl/xp_lvl[1])*100
        print("exp pct: ",xp_pct)

        line = """
        \t<div class="col-md-1 col-sm-1 col-xs-1">{rank}</div>
        \t<div class="col-md-1 col-sm-1 hidden-xs" style="padding:0"><img src="{avatar}" width={sz} height={sz} class="img-circle"></div>
        \t<div class="col-md-4 col-sm-4 col-xs-5">{name} <small>#{disc}</small></div>
        \t<div class="col-md-4 col-sm-4 col-xs-4"><center><h5>{left} / {thresh} <strong>XP</strong> [{exp}]</h5></center><div class="progress progress-striped"><div class="progress-bar progress-bar-info" style="width: {xp_pct}%"></div></div></div>
        \t<div class="col-md-2 col-sm-2 col-xs-2"><h3>Reputation {rep}</h3></div>
        \t<div class="col-md-2 col-sm-2 col-xs-2"><h3>Level {level}</h3></div>
        </div>

               """.format(
                       rank=rank,
                       avatar=item[7],
                       name=item[4],
                       disc=item[5],
                       num=item[3],
                       exp=item[6],
                       left=xp_lvl[1],
                       thresh=xp_thresh_to_next_lvl,
                       xp_pct=xp_pct,
                       rep=item[3],
                       level=self.cmd.player_level(item[5])[0],
                       sz=self.image_size)
        return line

