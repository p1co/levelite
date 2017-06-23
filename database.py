import sqlite3

class Database():
    def __init__(self, database_loc="test.db", table="testtable"):
        self.name = database_loc
        self.table = table

    # Open database
    def connect(self):
        try:
            conn = sqlite3.connect(self.name)
            return conn
        except sqlite3.Error as e:
            print(e)
        return None

    # Clean up methods from repetitive self.connect() statements
    # and use connection object as a context manager
    def sql_action(self, exec_string):
        conn = self.connect()
        try:
            with conn:
                conn.execute(exec_string)
        except sqlite3.Error as e:
            print(e)

    # Creates initial table used in the levels database
    def create_table(self):
        params = ('author TEXT PRIMARY KEY,'
                  'display TEXT,'
                  'disc TEXT,'
                  'avatar TEXT,'
                  'xp INTEGER DEFAULT 0,'
                  'level INTEGER DEFAULT 0,'
                  'last_msg TEXT')
        new_table = """CREATE TABLE IF NOT EXISTS {table}({params})
                    """.format(table=self.table, params=params)
        self.sql_action(new_table)

    # Add a new author to the table
    def add_record(self, author, display, disc, avatar, msg_time):
        print("{}, {}, {}, {}, {}".format(author, display, disc, avatar, msg_time))
        conn = self.connect()
        new_record = """INSERT INTO {table} (author, display, disc, avatar, last_msg) VALUES 
                        ("{author}",
                         "{display}",
                         "{disc}",
                         "{avatar}",
                         "{msg_time}") 
                     """.format(table=self.table,
                                author=author,
                                display=display,
                                disc=disc,
                                avatar=avatar,
                                msg_time=msg_time)
        try:
            with conn:
                conn.execute(new_record)
        except sqlite3.IntegrityError as e:
            print("{}: user already exists".format(e))
            return False

    # Modifies a record
    # Input: 'author', *[column, value]
    # Output: None
    def mod_record(self, author, *modify):
        for item in modify:
            mod_record = """UPDATE {table} SET {column}="{value}" WHERE author="{author}"
                         """.format(table=self.table,
                                    column=item[0],
                                    value=item[1],
                                    author=author)
            self.sql_action(mod_record)

    # Retrieves a single record
    # Input: 'author'
    # Output ('text', int, 'text')
    def get_record(self, author):
        conn = self.connect()
        conn.row_factory = sqlite3.Row
        cur = conn.cursor()
        get_record = """SELECT * FROM {table} WHERE author="{author}"
                     """.format(table=self.table,
                                author=author)
        try:
            with conn:
                cur.execute(get_record)
        except sqlite3.Error as e:
            print(e)
            return False
        return cur.fetchone()

    # Will be used for "levels" printout
    def get_all_record(self):
        conn = self.connect()
        cur = conn.cursor()
        get_record = """SELECT * from {table} ORDER BY "xp" DESC
                     """.format(table=self.table)
        try:
            with conn:
                cur.execute(get_record)
        except sqllite3.Error as e:
            print(e)
        return cur.fetchall()

    def count_recs(self):
        conn = self.connect()
        cur = conn.cursor()
        get_record = """SELECT * FROM {table};
                     """.format(table=self.table)
        try:
            with conn:
                cur.execute(get_record)
        except sqllite3.Error as e:
            print(e)
        # Using len() on a larger db might cause some slowdown
        # I'll refactor if needed
        return len(cur.fetchall())

