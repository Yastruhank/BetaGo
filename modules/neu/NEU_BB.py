#!/usr/bin/python3
# -*- coding:utf-8 -*-
import re
import time
from lxml import etree
import platform
import subprocess
from utils.tools import SendMessage,addtwodimdict
from modules.neu.NEU import NeuStu
import heapq

import asyncio
from graia.ariadne.app import Ariadne
from graia.ariadne.event.message import GroupMessage, MessageEvent, FriendMessage, TempMessage, StrangerMessage
from graia.ariadne.message.element import Plain, At, AtAll, Face, Image
from graia.ariadne.message.chain import MessageChain, Source
from graia.ariadne.connection.config import HttpClientConfig,WebsocketClientConfig,config
from graia.ariadne.model import Group, Stranger, Friend, Member, Client, Union, MemberPerm

from graia.saya import Channel
from graia.saya.builtins.broadcast.schema import ListenerSchema


class NEU_BB(NeuStu):
    async def sign_bb(self):
        self.result = {'课程名：': {'作业名：': '详细信息'}}
        param = '-n' if platform.system().lower() == 'windows' else '-c'
        command = 'ping' + " " + param + " " + '1' + " -w 1 " + 'bb.neu.edu.cn'
        ping_code = subprocess.getstatusoutput(command)

        if(ping_code[0] == 0):
            self.bb_url_header = 'https://bb.neu.edu.cn'
        if(ping_code[0] == 1):
            self.bb_url_header = 'https://webvpn.neu.edu.cn'

        if(self.bb_url_header[8:14] == "webvpn"):
            await self.login_vpn()
            page = await self.session.get(
                self.bb_url_header + '/https/77726476706e69737468656265737421f2f50f92222526557a1dc7af96' + '/webapps/bb-sso-BBLEARN/index.jsp')
        else:
            page = await self.session.get(
                self.bb_url_header + '/webapps/bb-sso-BBLEARN/index.jsp')
        html = etree.HTML(await page.text())
        html_data = html.xpath(
            '/html/body/div[5]/div/div/div[2]/div[2]/div/div/div/div[4]/div[1]/div[2]/div[2]/ul/li/a')
        time_data = time.localtime(time.time())
        year = time_data.tm_year
        month = time_data.tm_mon
        term = 0
        if(month <= 1):
            term = 1
        else:
            if(month <= 7):
                term = 2
            else:
                term = 3
        term_name = ''
        if(term == 1):
            term_name = str(year-1) + '-' + str(year) + '-1'
        if(term == 2):
            term_name = str(year-1) + '-' + str(year) + '-2'
        if(term == 3):
            term_name = ('%d' % year) + '-' + ('%d' % year+1) + '-1'
        for i in html_data:
            if(i.text[0:11] != term_name):
                continue
            url = self.bb_url_header + '/' + i.xpath('@href')[0][1:]
            await self.get_content(url)

    async def get_content(self, url):
        page = await self.session.get(url)
        html = etree.HTML(await page.text())
        html_data = html.xpath(
            '/html/body/div[5]/div[2]/nav/div/div[2]/div/div[2]/ul/li/a')
        for i in html_data:
            span_title = i.xpath('span')[0].text
            if span_title == '主页' or span_title == '讨论' or span_title == '小组' or span_title == '工具' or span_title == '帮助':
                continue
            url_inside = self.bb_url_header + i.xpath('@href')[0]
            await self.get_homework(url_inside)

    async def get_homework(self, url):
        page = await self.session.get(url)
        html = etree.HTML(await page.text())
        html_data = html.xpath(
            '/html/body/div[5]/div[2]/div/div/div/div/div[2]/ul/li/div[1]/h3/a')
        front_head = 0
        if(self.bb_url_header[8:14] == "webvpn"):
            front_head = 65
        for i in html_data:
            url_inside_path = i.xpath('@href')[0]
            if(url_inside_path[front_head+1:front_head+8] != 'webapps'):
                continue
            if(url_inside_path[front_head+9:front_head+27] == 'blackboard/content'):
                await self.get_homework(self.bb_url_header + url_inside_path)
            if(url_inside_path[front_head+9:front_head+19] != 'assignment'):
                continue
            url_inside = self.bb_url_header + url_inside_path
            await self.get_homework_detail(url_inside)

    async def get_homework_detail(self, url):
        page = await self.session.get(url)
        html = etree.HTML(await page.text())
        check_data = html.xpath(
            '/html/body/div[5]/div[2]/div/div/div/div/div[2]/div/div[3]/div[3]/form/h3/label/span[2]/text()')
        if(len(check_data) > 0 and check_data[0] == '最后评分的尝试'):
            return
        html_data = html.xpath(
            '/html/body/div[5]/div[2]/div/div/div/div/div[2]/form/div/div[2]/div/ol/li/div/div/div')
        title_data = html.xpath(
            '/html/body/div[5]/div[2]/div/div/div/div/div[1]/div/h1/span')
        title = title_data[0].text
        lession_data = html.xpath(
            '/html/body/div[5]/div[2]/nav/div/div[2]/div/div[2]/div/div/h3[1]/a')
        lession = lession_data[0].text

        # print(lession, end=" ")
        # print(title[9:])
        all_content = ""
        for i in html_data:
            header_data = i.xpath('div[1]')
            content_data = i.xpath('div[2]')
            if(len(header_data) == 0 or len(content_data) == 0):
                continue
            header = header_data[0].text
            content = content_data[0].text
            header = header.strip()
            content = content.strip()
            time = ''
            if(header == '截止日期'):
                time = content_data[0].xpath('span')[0].text
            time = time.strip()
            # print(header, end=" ")
            # print(content + time)
            all_content = all_content + header + " " + content + time + '\n'
        addtwodimdict(self.result, lession, title, all_content)
        
    async def getBBResult(self,find_key):
        results = self.result
        output_str = ""
        heap = []
        for key1 in results:
            if(key1 == '课程名：'):
                continue
            for key2 in results[key1]:
                time_value = 0x7fffffff
                cnt_str = key1 + "\n" + key2 + \
                    "\n" + results[key1][key2] + "\n\n"
                if(len(find_key) > 0):
                    if(re.search(find_key, cnt_str) == None):
                        continue
                target = re.search('截止日期', results[key1][key2])
                if(target != None):
                    time_value = 0
                    start_id = target.span()[0]
                    year = 0
                    month = 0
                    day = 0
                    status = 0
                    for i in results[key1][key2][start_id + 4:start_id + 15]:
                        if(i >= '0' and i <= '9'):
                            if(status == 0):
                                year = year * 10 + int(i)
                            if(status == 1):
                                month = month * 10 + int(i)
                            if(status == 2):
                                day = day * 10 + int(i)
                        if(i == '年' or i == '月' or i == '日'):
                            status += 1
                        time_value = year * 10000 + month * 100 + day
                heapq.heappush(heap, (time_value, cnt_str))
        while(len(heap) > 0):
            output_str += heap[0][1]
            heapq.heappop(heap)
        return output_str
        
channel = Channel.current()

@channel.use(ListenerSchema(listening_events=[MessageEvent]))
async def GetBB(app: Ariadne, event: MessageEvent, sender: Union[Friend, Member, Client, Stranger], source: Source, message: MessageChain):
    from core.load_param import sql
    if(str(message)[0:6] != '查询BB作业' and str(message)[0:6] != '查询bb作业'):
        return
    find_key = ''
    if(len(str(message)) > 6):
        find_key = str(message)[6:].strip()
    sender_id = str(sender.id)
    data = await sql.select_one("eone_neu", "id", sender_id)
    if(not data):
        await SendMessage(app, MessageChain("你还没有绑定一网通账号,请使用 绑定 指令完成一网通账号绑定"), sender, event.type)
        return
    account = data[0]['eone_id']
    password = data[0]['eone_passwd']
    stu = NEU_BB(int(account), password)
    await SendMessage(app, MessageChain("正在查询BB作业,该过程可能需要一些时间,请稍候..."), sender, event.type)
    await stu.init()
    if(stu.init_down == False):
        await SendMessage(app, MessageChain("登录BB平台失败,请检查你的账号密码并重新绑定"), sender, event.type)
        return
    await stu.sign_bb()
    output_str = await stu.getBBResult(find_key)
    if(len(output_str) == 0):
        output = MessageChain("没有找到相应的BB作业")
    output = MessageChain(Plain(output_str))
    await SendMessage(app, output, sender, event.type)