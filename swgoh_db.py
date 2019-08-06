import sqlite3
from sqlite3 import Error
def db_query_gp_date(conn,player_id,date_id):
     sql = '''SELECT gpchars,gpships, allycode, name
             FROM gp 
            INNER JOIN update_time on update_time.id = gp.updatetime_id
            INNER JOIN players on players.id=gp.player_id
            WHERE update_time.id=?
            AND players.id=?
      '''
     cur=conn.cursor()
     cur.execute(sql,[date_id,player_id])
     return cur.fetchone()
def db_insert_gp(conn,gp):
    sql = '''INSERT INTO gp(player_id,updatetime_id,gpships,gpchars)
             VALUES(?,?,?,?)'''
    cur = conn.cursor()
    cur.execute(sql, gp)
    return cur.lastrowid
def db_insert_timestamp(conn,time):
    sql = '''INSERT INTO update_time(snapshot) VALUES(?)'''
    cur = conn.cursor()
    cur.execute(sql,(time,))
    return cur.lastrowid
def db_query_player_id(conn,ally):
    cur=conn.cursor()
    cur.execute("SELECT id FROM players WHERE allycode=?",(ally,) )
    return cur.fetchone()[0]
def db_query_player_id_name(conn,ally):
    cur=conn.cursor()
    cur.execute("SELECT id, name FROM players WHERE allycode=?",(ally,) )
    return cur.fetchone()
def db_query_all_players_id_name(conn):
    cur=conn.cursor()
    cur.execute("SELECT id, name FROM players")
    return cur.fetchall()
def db_check_timestamp(conn,time):
    cur=conn.cursor()
    cur.execute("SELECT count(*) FROM update_time WHERE snapshot =?",(time,))
    data=cur.fetchone()[0]
    if data==0:
        return False
    else:
        return True
def db_get_timestamp(conn,time):
    cur=conn.cursor()
    cur.execute("SELECT count(),id FROM update_time WHERE snapshot =?",(time,))
    data=cur.fetchone()
    return data
def db_get_all_times(conn):
    cur=conn.cursor()
    cur.execute("SELECT * FROM update_time")
    data=cur.fetchall()
    return data
def db_insert_player(conn,player):
    #add a player to DB
    sql = '''INSERT INTO players(allycode, name)
             VALUES(?,?)'''
    cur = conn.cursor()
    cur.execute(sql, player)
    return cur.lastrowid

def db_player_in_guild(conn,allyC):
    cur=conn.cursor()
    cur.execute("SELECT count(*) FROM players where allycode =? AND updated = (SELECT max(updated) FROM players); ",(allyC,))
    data=cur.fetchone()[0]
    if data ==0:
        return False
    else:
        return True
def db_query_all_players(conn):
    """Get the GP data for all players that were in the guild on the last update"""
    sql = '''SELECT
    *
    FROM
    players
    WHERE
    updated = (SELECT max(updated) FROM players);'''
    cur = conn.cursor()
    cur.execute(sql)
    return cur.fetchall()
def db_update_player(conn,player):
    """Insert the new player data or update if the player is already in DB"""
    sql = '''UPDATE OR IGNORE players
            set updated=?, gpships = ?, gpchars = ?
            where allycode = ?'''
    cur = conn.cursor()
    cur.execute(sql,player[0:4])
    sql = '''INSERT OR IGNORE INTO
     players (updated, gpships,gpchars,allycode,name)
     VALUES(?,?,?,?,?)'''
    cur = conn.cursor()
    cur.execute(sql,player)   
    return cur.lastrowid

def db_add_warn(conn,warn):
    """Add a strike for a player"""
    sql = "INSERT INTO warnings (allycode, date, comment) VALUES(?,?,?)"
    cur = conn.cursor()
    cur.execute(sql,warn)   
    return cur.lastrowid

def db_list_warn(conn):
    sql = """
    SELECT 
	players.name,
	warnings.allycode,
	date,
	comment,
    warnings.id
    FROM warnings 
    INNER JOIN players on players.allycode=warnings.allycode
    """
    cur = conn.cursor()
    cur.execute(sql)
    return cur.fetchall()

def db_dell_warn(conn,id):
    sql = "DELETE FROM warnings WHERE id = ?"
    cur=conn.cursor()
    cur.execute(sql,(id,))
    return

def db_check_player(conn,allyC):
    cur=conn.cursor()
    cur.execute("SELECT count(*) FROM players where allycode =?",(allyC,))
    data=cur.fetchone()[0]
    if data ==0:
        return True
    else:
        return False
def db_create_connection(db_file):
    """ create a database connection to the SQLite database
        specified by db_file
    :param db_file: database file
    :return: Connection object or None
    """
    try:
        conn = sqlite3.connect(db_file)
        return conn
    except Error as e:
        print(e)
 
    return None
def db_create_table(conn, create_table_sql):
    """ create a table from the create_table_sql statement
    :param conn: Connection object
    :param create_table_sql: a CREATE TABLE statement
    :return:
    """
    try:
        c = conn.cursor()
        c.execute(create_table_sql)
    except Error as e:
        print(e)
def create_tables_in_db():
    database = "/home/motornyi/SWGOH_API/second.db"
 
    sql_create_projects_table = """ CREATE TABLE IF NOT EXISTS projects (
                                        id integer PRIMARY KEY,
                                        name text NOT NULL,
                                        begin_date text,
                                        end_date text
                                    ); """
 
    sql_create_tasks_table = """CREATE TABLE IF NOT EXISTS tasks (
                                    id integer PRIMARY KEY,
                                    name text NOT NULL,
                                    priority integer,
                                    status_id integer NOT NULL,
                                    project_id integer NOT NULL,
                                    begin_date text NOT NULL,
                                    end_date text NOT NULL,
                                    FOREIGN KEY (project_id) REFERENCES projects (id)
                                );"""
    sql_create_players_table = """ CREATE TABLE IF NOT EXISTS players (
                                        id integer PRIMARY KEY,
                                        allycode integer UNIQUE NOT NULL,
                                        name text NOT NULL
                                    ); """
    sql_create_time_table = """ CREATE TABLE IF NOT EXISTS update_time (
                                        id integer PRIMARY KEY,
                                        snapshot text UNIQUE NOT NULL
                                    ); """    
    sql_create_gp_table= """ CREATE TABLE IF NOT EXISTS gp (
                                        id integer PRIMARY KEY,
                                        player_id integer,
                                        updatetime_id integer,
                                        gpships integer,
                                        gpchars integer,
                                        FOREIGN KEY (player_id) REFERENCES players (id),
                                        FOREIGN KEY (updatetime_id) REFERENCES update_time (id)

                                    ); """
    # create a database connection
    conn = db_create_connection(database)
    with conn:
        # create projects table
#        create_table(conn, sql_create_projects_table)
        # create tasks table
 #       create_table(conn, sql_create_tasks_table)
 #       player=(928428534,'Lossberg')
 #       player_id=create_player(conn,player)
 #       print(player)
        # player=(3,'Lossberg')
        # player_id=create_player(conn,player);
        # print(player_id)
        #conn.close()
        db_create_table(conn, sql_create_players_table)
        db_create_table(conn,sql_create_time_table)
        db_create_table(conn,sql_create_gp_table)