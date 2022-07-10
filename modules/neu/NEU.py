#!/usr/bin/python3
# -*- coding:utf-8 -*-
import asyncio
import aiohttp
import json
import re
from lxml import etree
import platform
import subprocess

class NeuStu(object):
    result = {'课程名：': {'作业名：': '详细信息'}}
    bb_url_header = ''
    init_down = False
    id = '00000000'
    password = '000000'
    # 初始化

    def __init__(self, stu_id, pwd):
        self.__headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/56.0.2911.0 Safari/537.36'}
        self.id = str(stu_id)
        self.password = str(pwd)
        # self.pass_cookies = {'Language': 'zh_CN'}
        self.session = aiohttp.ClientSession()
        self.session.headers.update(self.__headers)
        # self.session.cookies.update(self.pass_cookies)
        
    def __del__(self):
        loop = asyncio.get_event_loop()
        if loop.is_running():
            loop.create_task(self.session.close())
        else:
            loop.run_until_complete(self.session.close())
    
    async def init(self):
        ret = await self.__index_login()
        if(ret):
            self.init_down = True

    async def __index_login(self):
        login_page = await self.session.get('https://pass.neu.edu.cn/tpass/login')
        # self.pass_cookies['jsessionid_tpass'] = login_page.cookies['jsessionid_tpass']
        page_text = await login_page.text()
        lt = re.findall("name=\"lt\" value=\"(.*?)\" />", page_text)[0]
        execution = re.findall(
            "name=\"execution\" value=\"(.*?)\" />", page_text)[0]
        post_data = {
            'rsa': self.id + self.password + lt,
            'ul': len(self.id),
            'pl': len(self.password),
            'lt': lt,
            'execution': execution,
            '_eventId': 'submit'
        }
        login_post = await self.session.post('https://pass.neu.edu.cn/tpass/login',
                                       headers=self.__headers, cookies=login_page.cookies, data=post_data)
        for i in login_post.history:
            # if 'CASTGC' in i.cookies:
            #     self.pass_cookies['CASTGC'] = i.cookies['CASTGC']
            if 'tp_up' in i.cookies:
                self.index_cookies = i.cookies
                # print('[ + ] Login success.')
                return True
        return False

    async def login_vpn(self):
        login_page = await self.session.get(
            'https://webvpn.neu.edu.cn/http/77726476706e69737468656265737421e0f6528f693e6d45300d8db9d6562d/tpass/login')
        lt = re.findall("name=\"lt\" value=\"(.*?)\" />", await login_page.text())[0]
        execution = re.findall(
            "name=\"execution\" value=\"(.*?)\" />", await login_page.text())[0]
        post_data = {
            'rsa': self.id + self.password + lt,
            'ul': len(self.id),
            'pl': len(self.password),
            'lt': lt,
            'execution': execution,
            '_eventId': 'submit'
        }
        login_post = await self.session.post('https://webvpn.neu.edu.cn/http/77726476706e69737468656265737421e0f6528f693e6d45300d8db9d6562d/tpass/login',
                                       headers=self.__headers, cookies=login_page.cookies, data=post_data)

    
    
    