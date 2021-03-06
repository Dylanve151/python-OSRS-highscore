#!/usr/bin/python3

from bs4 import BeautifulSoup
from config import config
import datetime
import requests
import psycopg2
import json

#Change these:
#osrsusers = "Zezima","Torvesta"
#timezone = "+00"

#stat links
hcuri = "https://secure.runescape.com/m=hiscore_oldschool/index_lite.ws"
hccaturi = "https://secure.runescape.com/m=hiscore_oldschool/overall"

#getting all categories (skills, minigames, bosses and etc)
hccatswr = requests.get(hccaturi).content
hccatsoup = BeautifulSoup(hccatswr, 'html.parser').find(id="contentCategory").getText()
hccats = [x for x in "".join([s for s in hccatsoup.splitlines(True) if s.strip("\r\n")]).replace("'","`").split("\n") if x]

osrsusers = open("/config/osrs_players","r").readline().replace('"','').replace("\n","").split(",")
timezone = open("/config/tz","r").readlines()

#loads of stuff i am too lazy to explain
HClist={}
SQLTables={}
SQLData={}

datetimestr=str(datetime.datetime.now()).split(".")[0]+timezone

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

def create_tables():
    conn = None
    try:
        # read the connection parameters
        params = config()
        # connect to the PostgreSQL server
        conn = psycopg2.connect(**params)
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
    create_tables()
