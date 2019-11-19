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

def db_query_gp_history(conn,codes):
    """Get the GP history data for all players that were in the guild on the last update"""
    sql = '''SELECT
    *
    FROM
    gp_history
    WHERE
    allycode IN (%s)'''% ','.join("?"*len(codes))
    cur = conn.cursor()
    print(sql)
    cur.execute(sql,codes)
    return cur.fetchall()

def db_search_all_players(conn,name):
    """Get the GP data for all players with matching names that were in the guild on the last update"""
    sql = '''SELECT
    *
    FROM
    players
    WHERE
    updated = (SELECT max(updated) FROM players)
    AND name like ?;'''
    cur = conn.cursor()
    cur.execute(sql,(f"%{name}%",))
    return cur.fetchall()

def db_update_player(conn,player):
    """Insert the new player data or update if the player is already in DB"""
    sql = '''UPDATE OR IGNORE players
            set updated=?, gpships = ?, gpchars = ?, name = ?
            where allycode = ?'''
    cur = conn.cursor()
    cur.execute(sql,player[:])
    sql = '''INSERT OR IGNORE INTO
     players (updated, gpships,gpchars,name,allycode)
     VALUES(?,?,?,?,?)'''
    cur = conn.cursor()
    cur.execute(sql,player)
    player = list(player)   
    print(player)
    player.pop(3)
    print(player)
    sql = '''INSERT INTO
     gp_history (updated, gpships,gpchars,allycode)
     VALUES(?,?,?,?)'''
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
