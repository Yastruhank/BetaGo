#!/usr/bin/python
# -*- coding: UTF-8 -*-

import pymysql
import pickle
import time


class SQL:
    time_out_time = 300

    def __init__(self,host,port,db,user,password):
        self.host = host
        self.port = port
        self.db = db
        self.user = user
        self.password = password

    async def connect(self):
        self.conn = pymysql.connect(host=self.host, port=self.port, db=self.db,
                               user=self.user, password=self.password)
        self.cursor = self.conn.cursor(pymysql.cursors.DictCursor)
    
    async def disconnect(self):
        self.cursor.close()
        self.conn.close()

    async def select_one(self, table, index, param):
        await self.connect()
        self.cursor.execute("select * from " + table +
                            " where " + index + " = " + param)
        data = self.cursor.fetchall()
        await self.disconnect()
        return data

    async def select_all(self,table):
        await self.connect()
        self.cursor.execute("select * from " + table)
        data = self.cursor.fetchall()
        await self.disconnect()
        return data

    async def insert_one(self, table, param):
        await self.connect()
        str_ = ''
        for i in param:
            if(len(str_) > 0):
                str_ += ',%s'
            else:
                str_ += '%s'
        self.cursor.execute("insert into " + table +
                            " values(" + str_ + ")", param)
        self.conn.commit()
        await self.disconnect()

    async def delete_one(self, table, index, param):
        await self.connect()
        self.cursor.execute("delete from " + table +
                            " where " + index + " = " + param)
        self.conn.commit()
        await self.disconnect()

    async def update_one(self, table, select_index, select_param, update_index, update_param):
        await self.connect()
        self.cursor.execute("update " + table +
                            " set " + update_index + " = " + update_param + " where " + select_index + " = " + select_param)
        self.conn.commit()
        await self.disconnect()

    async def create_table(self,table,param):
        await self.connect()
        str_ = ''
        for i in param:
            if(len(str_) > 0):
                str_ += ',%s'
            else:
                str_ += '%s'
        self.cursor.execute("create table " + table +
                            "(" + str_ + ")")
        self.conn.commit()
        await self.disconnect()
        

    def __exit__(self, *exc_info):
        self.cursor.close()
        self.conn.close()
