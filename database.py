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
    def create_table(self, role):
        params = ('uid TEXT PRIMARY KEY,'
                  'author TEXT,'
                  'role TEXT NOT NULL DEFAULT \'{starting_role}\','
                  'rep TEXT DEFAULT 0,'
                  'display TEXT,'
                  'disc TEXT,'
                  'xp INTEGER DEFAULT 0,'
                  'avatar TEXT DEFAULT 0,'
                  'last_msg TEXT'.format(starting_role=role))
        new_table = """CREATE TABLE IF NOT EXISTS {table}({params})
                    """.format(table=self.table, params=params)
        self.sql_action(new_table)

    # Add a new author to the table
    def add_record(self, uid, author, role, display, disc, avatar, msg_time):
        conn = self.connect()
        tbl_param = "uid, author, role, display, disc, avatar, last_msg"
        val_param = ('"{uid}", "{author}", "{role}", "{display}",'
                     '"{disc}", "{avatar}", "{msg_time}"'.format(
                          uid=uid,
                          author=author,
                          role=role,
                          display=display,
                          disc=disc,
                          avatar=avatar,
                          msg_time=msg_time))

        new_record = """INSERT INTO {table} ({tbl_param}) VALUES ({val_param})
                     """.format(table=self.table,
                                tbl_param=tbl_param,
                                val_param=val_param)
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
    def get_record(self, uid, field="*"):
        conn = self.connect()
        conn.row_factory = sqlite3.Row
        cur = conn.cursor()
        get_record = """SELECT {field} 
                        FROM {table} 
                        WHERE uid="{uid}" 
                        ORDER BY "xp" DESC
                     """.format(table=self.table,
                                uid=uid,
                                field=field)
        try:
            with conn:
                cur.execute(get_record)
        except sqlite3.Error as e:
            print("sqlite3.Error: ", e)
            return False
        data = cur.fetchone()
        if data is None:
            return False
        else:
            return self.convert_data(data)

    def convert_data(self, row):
        if "discordapp.com" not in row[7]:
            avatar = None
        else:
            avatar = row[7]
        return {
                "uid":row[0],
                "author":row[1],
                "role":row[2],
                "rep":row[3],
                "display":row[4],
                "disc":row[5],
                "xp":row[6],
                "avatar":avatar,
                "last_msg":row[8]}


    # Will be used for "levels" printout
    def get_all_record(self, limit="*"):
        conn = self.connect()
        cur = conn.cursor()
        get_record = """SELECT *
                        FROM {table} 
                        ORDER BY "xp" DESC
                        LIMIT {limit}
                     """.format(table=self.table, limit=limit)
        try:
            with conn:
                cur.execute(get_record)
        except sqlite3.Error as e:
            print(e)
            return False

        data = cur.fetchall()
        processed_rows = []
        for row in data:
            processed_rows.append(self.convert_data(row))
        return processed_rows

    def find_user_rank(self, target):
        print("finding user rank for {}".format(target))
        conn = self.connect()
        cur = conn.cursor()
        get_record = """SELECT COUNT(author)
                        FROM {table} 
                        ORDER BY "xp" DESC
                     """.format(table=self.table, author=target)
        #                WHERE author="{author}"
        try:
            with conn:
                cur.execute(get_record)
        except sqlite3.Error as e:
            print(e)
        data = cur.fetchone()[0]
        print(data)
        return cur.fetchone()[0]


    def count_recs(self):
        conn = self.connect()
        cur = conn.cursor()
        get_record = """SELECT COUNT(1) FROM {table};
                     """.format(table=self.table)
        try:
            with conn:
                cur.execute(get_record)
        except sqlite3.Error as e:
            print(e)
        return cur.fetchone()[0]

