#!/usr/bin/python3
# -*- coding:utf-8 -*-
import re
import time
from lxml import etree
import platform
import subprocess
from utils.tools import SendMessage,addtwodimdict
from .NEU import NeuStu
import heapq

class NEU_EduSys(NeuStu):
    async def getScore(self):
        param = '-n' if platform.system().lower() == 'windows' else '-c'
        command = 'ping' + " " + param + " " + '1' + " -w 1 " + 'bb.neu.edu.cn'
        ping_code = subprocess.getstatusoutput(command)
        
        url_header=''
        if(ping_code[0] == 0):
            url_header = 'http://219.216.96.4/eams'
        if(ping_code[0] == 1):
            url_header = 'https://webvpn.neu.edu.cn/http/77726476706e69737468656265737421a2a618d275613e1e275ec7f8/eams'
            await self.login_vpn()
            
        page = await self.session.get(url_header + '/teach/grade/course/person.action')
        page_text = await page.text()
        target = re.search('semesterId=', page_text)
        start_id = target.span()[1]
        interest_text = page_text[start_id:start_id+10]
        target = re.search('&', interest_text)
        start_id = target.span()[0]
        
        page = await self.session.get(url_header + '/teach/grade/course/person!search.action?semesterId=' + interest_text[0:start_id] + '&projectType=')
        html = etree.HTML(await page.text())
        score_data = html.xpath(
            '/html/body/div[1]')
        return score_data[0].text[6:]
    
    async def getClassScore(self):
        param = '-n' if platform.system().lower() == 'windows' else '-c'
        command = 'ping' + " " + param + " " + '1' + " -w 1 " + 'bb.neu.edu.cn'
        ping_code = subprocess.getstatusoutput(command)
        
        url_header=''
        if(ping_code[0] == 0):
            url_header = 'http://219.216.96.4/eams'
        if(ping_code[0] == 1):
            url_header = 'https://webvpn.neu.edu.cn/http/77726476706e69737468656265737421a2a618d275613e1e275ec7f8/eams'
            await self.login_vpn()
            
        page = await self.session.get(url_header + '/teach/grade/course/person.action')
        page_text = await page.text()
        target = re.search('semesterId=', page_text)
        start_id = target.span()[1]
        interest_text = page_text[start_id:start_id+10]
        target = re.search('&', interest_text)
        start_id = target.span()[0]
        
        page = await self.session.get(url_header + '/teach/grade/course/person!search.action?semesterId=' + interest_text[0:start_id] + '&projectType=')
        html = etree.HTML(await page.text())
        class_name = html.xpath('/html/body/div[2]/table/tbody/tr/td[4]')
        class_weight = html.xpath('/html/body/div[2]/table/tbody/tr/td[7]')
        class_score = html.xpath('/html/body/div[2]/table/tbody/tr/td[13]')
        ret = []
        ret.append(class_name)
        ret.append(class_weight)
        ret.append(class_score)
        return ret