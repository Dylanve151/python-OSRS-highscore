#!/usr/bin/python3

from bs4 import BeautifulSoup
from datetime import datetime
import requests
import psycopg2
import json
import re
from dotenv import load_dotenv
import os

load_dotenv()

db_database = os.getenv('db_database')
db_host = os.getenv('db_host')
db_password = os.getenv('db_password')
db_user = os.getenv('db_user')
osrs_players = os.getenv('osrs_players')

conn_string = "host='"+db_host+"' dbname='"+db_database+"' user='"+db_user+"' password='"+db_password+"'"

#stat links
hcuri = "https://secure.runescape.com/m=hiscore_oldschool/index_lite.ws"
hccaturi = "https://runescape.wiki/w/Application_programming_interface"

#getting all categories (skills, minigames, bosses and etc)
hccatswr = requests.get(hccaturi).content
hccatsoupSTAT = BeautifulSoup(hccatswr, 'html.parser').find("pre", string=re.compile("Attack")).getText()
hccatsoupMG = BeautifulSoup(hccatswr, 'html.parser').find("pre", string=re.compile("TzTok-Jad")).getText()
#hccatsoup = hccatsoupSTAT + "----\n" + hccatsoupMG
hccatsoup = hccatsoupSTAT + hccatsoupMG
hccats = [x for x in "".join([s for s in hccatsoup.splitlines(True) if s.strip("\r\n")]).replace("'","`").split("\n") if x]

osrsusers = osrs_players.replace('"','').replace("\n","").split(",")

#loads of stuff i am too lazy to explain
HClist={}
SQLTables={}
SQLData={}

datetimestr=str(datetime.now().astimezone().isoformat(" ","seconds")[:-3])

for osrsuser in osrsusers:
    hcwr = BeautifulSoup(requests.get(hcuri+"?player="+osrsuser).content, 'html.parser').getText().split("\n")
    HCu={}
    n=0
    SQLTables[osrsuser]="""
        CREATE TABLE IF NOT EXISTS \""""+osrsuser+"""\"
        (
            highscore_id SERIAL PRIMARY KEY,
            stats JSON NOT NULL,
            datetime timestamp with time zone NOT NULL
        );
        """
    for cat in hccats:
        if n < 24:
            HCu[cat]={
                "Rank": hcwr[n].split(",")[0],
                "Level": hcwr[n].split(",")[1],
                "XP": hcwr[n].split(",")[2]
            }
        else:
            HCu[cat]={
                "Rank": hcwr[n].split(",")[0],
                "Score": hcwr[n].split(",")[1]
            }
        n+=1
    #HClist[osrsuser]=HCu
    SQLData[osrsuser]="""
        INSERT INTO \""""+osrsuser+"""\" (stats, datetime)
        VALUES(\'"""+json.dumps(HCu)+"""\',\'"""+datetimestr+"""\');
        """

def create_tables(params):
    conn = None
    try:
        # connect to the PostgreSQL server
        conn = psycopg2.connect(params)
        cur = conn.cursor()
        # create table one by one
        for osrsuser in osrsusers:
            cur.execute(SQLTables[osrsuser])
            cur.execute(SQLData[osrsuser])
        # close communication with the PostgreSQL database server
        cur.close()
        # commit the changes
        conn.commit()
    except (Exception, psycopg2.DatabaseError) as error:
        print(error)
    finally:
        if conn is not None:
            conn.close()

if __name__ == '__main__':
    create_tables(conn_string)
