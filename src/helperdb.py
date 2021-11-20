#!/usr/bin/python3
from database import Database

import re


class HelperDB:
    instance = None

    def __init__(self):
        self.db = Database("botimoku.db")
        # self.db.create_database(True)


    def setChannel(self, channel):
        return self.db.execute_query(f"UPDATE bot_config SET channel=? WHERE id=1", (channel,))
    
    def getChannel(self):
        return int(self.db.execute_query("SELECT channel FROM bot_config;")[0][0])

    def getInterval(self):
        return self.db.execute_query("SELECT interval FROM bot_config;")[0][0]

    def newTrade(self):
        pass

    def updateTrade(self, trade):
        pass

    def fromIntervalToSeconds(self, string):
        if(string.find("h")):
            return int(''.join(re.findall(r'\d+', string))) * 60 * 60
        # elif(string.find("m")):
        #     print(string)
        #     return int(''.join(re.findall(r'\d+', string))) * 60 
HelperDB.instance = HelperDB()
# print(HelperDB.instance.getChannel())
