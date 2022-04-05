#!/usr/bin/python
# -*- coding: UTF-8 -*-

import pymysql
import pickle
import tools
import time


class SQL:
    time_out_time = 3600

    def __init__(self,host,port,db,user,password):
        self.host = host
        self.port = port
        self.db = db
        self.user = user
        self.password = password
        self.conn = pymysql.connect(host=self.host, port=self.port, db=self.db,
                               user=self.user, password=self.password)
        self.cursor = self.conn.cursor(pymysql.cursors.DictCursor)
        self.last_connect_time = time.time()

    def reconnect(self):
        try:
            self.cursor.close()
            self.conn.close()
        except:
            print('close error')
        conn = pymysql.connect(host=self.host, port=self.port, db=self.db,
                               user=self.user, password=self.password)
        self.cursor = self.conn.cursor(pymysql.cursors.DictCursor)
        self.last_connect_time = time.time()

    def check_recon(self):
        cnt_time = time.time()
        if(cnt_time - self.last_connect_time > self.time_out_time):
            self.reconnect()

    def select_one(self, table, index, param):
        self.check_recon()
        self.cursor.execute("select * from " + table +
                            " where " + index + " = " + param)
        data = self.cursor.fetchall()
        return data

    def select_all(self,table):
        self.check_recon()
        self.cursor.execute("select * from " + table)
        data = self.cursor.fetchall()
        return data

    def insert_one(self, table, param):
        self.check_recon()
        str_ = ''
        for i in param:
            if(len(str_) > 0):
                str_ += ',%s'
            else:
                str_ += '%s'
        self.cursor.execute("insert into " + table +
                            " values(" + str_ + ")", param)
        self.conn.commit()

    def delete_one(self, table, index, param):
        self.check_recon()
        self.cursor.execute("delete from " + table +
                            " where " + index + " = " + param)
        self.conn.commit()

    def update_one(self, table, select_index, select_param, update_index, update_param):
        self.check_recon()
        self.cursor.execute("update " + table +
                            " set " + update_index + " = " + update_param + " where " + select_index + " = " + select_param)
        self.conn.commit()

    def create_table(self,table,param):
        self.check_recon()
        str_ = ''
        for i in param:
            if(len(str_) > 0):
                str_ += ',%s'
            else:
                str_ += '%s'
        self.cursor.execute("create table " + table +
                            "(" + str_ + ")")
        self.conn.commit()
        

    def __exit__(self, *exc_info):
        self.cursor.close()
        self.conn.close()
