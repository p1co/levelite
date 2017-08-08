# levelite

Currently: somewhat usable, if you like pain.

settings.cfg should look like this:
token: your_discord_bot_token
database: whatever_you_want_your_db_to_be_called.db
table: whatever_you_want_your_table_to_be_called.db


Project aims:
Create a player scoring system where their participation is rewarded. Participation is rewarded with a random number of experience points per message they type into chat. A promotion to the next role is done once an experience point threshold is reached.

This functionality will be similar to the level plugin in mee6. I'm writing this because I only use that mee6 plugin, and would like to have more options when it comes levels.

One thing I am planning on adding is periodic loss in experience due to inactivity. I'll need to make this thing stable before I even consider that.



Currently, it utilizes sqlite3 to store various bits of user data, and cherrypy to run as a standalone application server that hosts the output for a "top 100" list of players that users can trigger via a bot command.

The code is atrocious because I'm basically learning about databases, accessing APIs, and hosting an application server all in one go. Any suggestions and criticisms are welcome.
