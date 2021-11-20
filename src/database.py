#!/usr/bin/python3
import sqlite3
from sqlite3 import Error

class Database:
    def __init__(self, db):
        #Error handling
        if db is None: raise('Must indicate a db file')

        #Defaults
        self.conn = None

        #Connection
        try:
            self.conn = sqlite3.connect(db)
        except Error as e:
            raise(e)

    def execute_query(self, query, args=None):
        try:
            cursor = self.conn.cursor()
            if(args is not None):
                cursor.execute(query, args)
            else:
                cursor.execute(query)
            self.conn.commit()
            return cursor.fetchall()
        except Error as e:
            print(e)

    def create_database(self, set_config):
        sqlCreateUsuariosTable = """ CREATE TABLE IF NOT EXISTS usuarios (
                                            id integer PRIMARY KEY,
                                            disc_id char(200) NOT NULL UNIQUE,
                                            risk int,
                                            value int,
                                            close_umbrall tinyint NOT NULL,
                                            auto_operate boolean
                                        ); """

        sqlCreateTradesTable = """CREATE TABLE IF NOT EXISTS trades (
                                            id integer PRIMARY KEY,
                                            opentime timestamp NOT NULL,
                                            closetime timestamp UNIQUE,
                                            stoploss int NOT NULL,
                                            takeprofit int NOT NULL,
                                            symbol char(10) NOT NULL,
                                            usuarios char(256)
                                    );"""
        sqlCreateBotConfigTable = """CREATE TABLE IF NOT EXISTS bot_config (
                                        id integer PRIMARY KEY,
                                        interval char(4) NOT NULL,
                                        symbols char(200) NOT NULL,
                                        channel char(30)
                                    );"""        
        sqlCreateStrategiesTable = """CREATE TABLE IF NOT EXISTS strategies  (
                                        id integer PRIMARY KEY,
                                        nombre char(20) NOT NULL UNIQUE,
                                        margin integer NOT NULL
                                    );"""        
        if(set_config):
            sqlInsertDefaultConfig = """INSERT INTO bot_config VALUES(1, '1h','BTCUSDT,ETHUSDT,LINKUSDT,CAKEUSDT,LUNAUSDT,SOLUSDT', NULL)"""
        
            
        # create tables
        self.execute_query(sqlCreateBotConfigTable)
        self.execute_query(sqlCreateUsuariosTable)
        self.execute_query(sqlCreateTradesTable)        
        self.execute_query(sqlCreateStrategiesTable)
        if(set_config):
            self.execute_query(sqlInsertDefaultConfig)                
