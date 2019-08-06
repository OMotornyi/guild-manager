#!/usr/bin/python3

import sys
import json
import requests
from datetime import datetime, timedelta
from swgoh_api import *
from swgoh_db import *
import sqlite3
from sqlite3 import Error
def user_input_date():
    isValid=False
    while not isValid:
        guild_update_time = input("Type Date dd/mm/yyyy: ") 
        try: # strptime throws an exception if the input doesn't match the pattern
            d1 = datetime.strptime(guild_update_time, "%d/%m/%Y")
            isValid=True
        except ValueError:
            #print (what_error)
            print ("Try again! dd/mm/yyyy\n")
    return guild_update_time
def compare_player_gp (conn,time1, time2,player):
    database = "second.db"
    conn = db_create_connection(database)
    time1_id=db_get_timestamp(conn,time1)
    time2_id=db_get_timestamp(conn,time2)
    if   time1_id[0]==0 or time2_id[0]==0:
        print ("This character GP is not present in DB")
        return
    comp1 = db_query_gp_date(conn,player[0],time1_id[1])  
    comp2 = db_query_gp_date(conn,player[0],time2_id[1])   
    if (comp1 is not None) and (comp2 is not None):
        print(player[1],"Character GP delta:",abs(comp1[0]-comp2[0]),"Ships GP delta:",abs(comp1[1]-comp2[1]))
        return (comp1,comp2)
    else:
        return None

def compare_all_guild_gp (conn, time1, time2, to_file):
    all_guild_player=db_query_all_players_id_name(conn)
    if to_file: 
        file = open("test_file.dat","w")
        file.write("%-28s %-10s %-10s \n"%("Name","Characters","Ships"))
    for player in all_guild_player:
        player_gp_dif=compare_player_gp(conn,time1,time2,player)
        if to_file and (player_gp_dif is not None): 
            file.write("%-28s %10i %10i \n"%(player[1],abs(player_gp_dif[0][0]-player_gp_dif[1][0]),abs(player_gp_dif[0][1]-player_gp_dif[1][1])))
    if to_file: file.close()
    return
def players_gp_snapshot (conn):
    guild_roster = api_swgoh_guilds(CONFIG,{
    #        'structure':True,
            'language': 'eng_us',
            'allycodes': [ 928428534 ],
            'project': {
                'roster': {
                    'allyCode': 1,
                    'name': 1,
                    'gp': 1,
                    'gpChar':1,
                    'gpShip': 1,
                },
                'updated': 1,
            },
    })
    
    updated_datetime = datetime.fromtimestamp(guild_roster[0]['updated']/1000)
    updated_date=updated_datetime.strftime('%d/%m/%Y')

    if db_get_timestamp(conn,updated_date)[0]==0:
        timestamp_id=db_insert_timestamp(conn,updated_date)
        for player_full in guild_roster[0]['roster']:
            player=(player_full['allyCode'],player_full['name'])
            if db_check_player(conn,player_full['allyCode']):
                player_id=db_insert_player(conn,player)
            else:
                player_id=db_query_player_id(conn,player_full['allyCode'])   
            gp_sql=(player_id,timestamp_id,player_full['gpShip'],player_full['gpChar'])
            #gp_id=
            db_insert_gp(conn,gp_sql)
        return updated_date
    else:
        print("You have already updated the database today")
        return updated_date
    
