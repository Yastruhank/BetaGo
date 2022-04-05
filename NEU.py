#!/usr/bin/python3
# -*- coding:utf-8 -*-
import requests
import json
import re
import time
import random
import getopt
import sys
from lxml import etree
import platform
import subprocess
import tools


class NeuStu(object):
    result = {'课程名：': {'作业名：': '详细信息'}}
    bb_url_header = ''
    init_down = False
    id = '00000000'
    password = '000000'
    # 初始化

    def __init__(self, stu_id, pwd):
        requests.packages.urllib3.disable_warnings()
        self.__headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/56.0.2911.0 Safari/537.36'}
        self.id = str(stu_id)
        self.password = str(pwd)
        self.pass_cookies = {'Language': 'zh_CN'}
        self.session = requests.Session()
        # self.session.headers.update(self.__headers)
        # self.session.cookies.update(self.pass_cookies)
        self.__index_login()

    def __index_login(self):
        login_page = self.session.get('https://pass.neu.edu.cn/tpass/login')
        self.pass_cookies['jsessionid_tpass'] = login_page.cookies['jsessionid_tpass']
        lt = re.findall("name=\"lt\" value=\"(.*?)\" />", login_page.text)[0]
        execution = re.findall(
            "name=\"execution\" value=\"(.*?)\" />", login_page.text)[0]
        post_data = {
            'rsa': self.id + self.password + lt,
            'ul': len(self.id),
            'pl': len(self.password),
            'lt': lt,
            'execution': execution,
            '_eventId': 'submit'
        }
        login_post = self.session.post('https://pass.neu.edu.cn/tpass/login',
                                       headers=self.__headers, cookies=login_page.cookies, data=post_data)
        for i in login_post.history:
            if 'CASTGC' in i.cookies:
                self.pass_cookies['CASTGC'] = i.cookies['CASTGC']
            if 'tp_up' in i.cookies:
                self.index_cookies = i.cookies
                self.init_down = True
                print('[ + ] Login success.')

    def __index_login_vpn(self):
        login_page = self.session.get(
            'https://webvpn.neu.edu.cn/http/77726476706e69737468656265737421e0f6528f693e6d45300d8db9d6562d/tpass/login')
        lt = re.findall("name=\"lt\" value=\"(.*?)\" />", login_page.text)[0]
        execution = re.findall(
            "name=\"execution\" value=\"(.*?)\" />", login_page.text)[0]
        post_data = {
            'rsa': self.id + self.password + lt,
            'ul': len(self.id),
            'pl': len(self.password),
            'lt': lt,
            'execution': execution,
            '_eventId': 'submit'
        }
        login_post = self.session.post('https://webvpn.neu.edu.cn/http/77726476706e69737468656265737421e0f6528f693e6d45300d8db9d6562d/tpass/login',
                                       headers=self.__headers, cookies=login_page.cookies, data=post_data)

    def sign_bb(self):
        self.result = {'课程名：': {'作业名：': '详细信息'}}
        param = '-n' if platform.system().lower() == 'windows' else '-c'
        command = 'ping' + " " + param + " " + '1' + " -w 1 " + 'bb.neu.edu.cn'
        ping_code = subprocess.getstatusoutput(command)

        if(ping_code[0] == 0):
            self.bb_url_header = 'https://bb.neu.edu.cn'
        if(ping_code[0] == 1):
            self.bb_url_header = 'https://webvpn.neu.edu.cn'

        if(self.bb_url_header[8:14] == "webvpn"):
            self.__index_login_vpn()
            page = self.session.get(
                self.bb_url_header + '/https/77726476706e69737468656265737421f2f50f92222526557a1dc7af96' + '/webapps/bb-sso-BBLEARN/index.jsp')
        else:
            page = self.session.get(
                self.bb_url_header + '/webapps/bb-sso-BBLEARN/index.jsp')
        html = etree.HTML(page.text)
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
            self.get_content(url)

    def get_content(self, url):
        page = self.session.get(url)
        html = etree.HTML(page.text)
        html_data = html.xpath(
            '/html/body/div[5]/div[2]/nav/div/div[2]/div/div[2]/ul/li/a')
        for i in html_data:
            span_title = i.xpath('span')[0].text
            if span_title == '主页' or span_title == '讨论' or span_title == '小组' or span_title == '工具' or span_title == '帮助':
                continue
            url_inside = self.bb_url_header + i.xpath('@href')[0]
            self.get_homework(url_inside)

    def get_homework(self, url):
        page = self.session.get(url)
        html = etree.HTML(page.text)
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
                self.get_homework(self.bb_url_header + url_inside_path)
            if(url_inside_path[front_head+9:front_head+19] != 'assignment'):
                continue
            url_inside = self.bb_url_header + url_inside_path
            self.get_homework_detail(url_inside)

    def get_homework_detail(self, url):
        page = self.session.get(url)
        html = etree.HTML(page.text)
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
        tools.addtwodimdict(self.result, lession, title, all_content)

    def sign_jkdk(self):
        start_page = self.session.get(
            'https://ehall.neu.edu.cn/infoplus/form/JKXXSB/start', verify=False)
        get_profiles = self.session.get(
            'https://e-report.neu.edu.cn/api/profiles/'+self.id)
        prof_dict = json.loads(get_profiles.text)
        post_data = {
            '_token': re.findall("\"csrf-token\" content=\"(.*?)\">", start_page.text)[0],
            'jibenxinxi_shifoubenrenshangbao': '1',
            'profile[xuegonghao]': self.id,
            'profile[xingming]': prof_dict['data']['xingming'],
            'profile[suoshubanji]': prof_dict['data']['suoshubanji'],
            'jiankangxinxi_muqianshentizhuangkuang': '正常',
            'xingchengxinxi_weizhishifouyoubianhua': '0',
            'cross_city': '无',
            'qitashixiang_qitaxuyaoshuomingdeshixiang': '',
            'credits': '1',
            'travels': []
        }

        post_notes = self.session.post(
            'https://e-report.neu.edu.cn/api/notes', data=post_data, verify=False)
        if post_notes.text == '':
            print('[ + ] Sign success.')

        verify = self.session.get(
            'https://e-report.neu.edu.cn/notes', verify=False)
        if verify.text.find("上报成功") != -1:
            print('[ + ] Verify success.')
            return True
        return False

    def sign_jkdk_detail(self, t):
        create_page = self.session.get(
            'https://e-report.neu.edu.cn/inspection/items/%d/records/create' % t)
        post_data = {
            '_token': re.findall("\"csrf-token\" content=\"(.*?)\">", create_page.text)[0],
            'temperature': 36.5,
            'suspicious_respiratory_symptoms': 0,
            'symptom_descriptions': ''
        }
        post_insp = self.session.post(
            'https://e-report.neu.edu.cn/inspection/items/%d/records' % t, data=post_data, verify=False)
        return True

    def getBBResult(self):
        return self.result
