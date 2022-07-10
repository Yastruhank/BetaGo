#!/usr/bin/python3
# -*- coding:utf-8 -*-
import re
import json
from modules.neu.NEU import NeuStu

import asyncio

class NEU_HealReport(NeuStu):
    async def sign_jkdk(self):
        start_page = await self.session.get(
            'https://ehall.neu.edu.cn/infoplus/form/JKXXSB/start',max_redirects=30)
        get_profiles = await self.session.get(
            'https://e-report.neu.edu.cn/api/profiles/'+self.id)
        prof_dict = await get_profiles.json()
        post_data = {
            '_token': re.findall("\"csrf-token\" content=\"(.*?)\">", await start_page.text())[0],
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

        post_notes = await self.session.post(
            'https://e-report.neu.edu.cn/api/notes', data=post_data)
        # if post_notes.text == '':
            # print('[ + ] Sign success.')

        verify = await self.session.get(
            'https://e-report.neu.edu.cn/notes')
        verify_text = await verify.text()
        if verify_text.find("上报成功") != -1:
            # print('[ + ] Verify success.')
            return True
        return False

    async def sign_jkdk_detail(self, t):
        create_page = await self.session.get(
            'https://e-report.neu.edu.cn/inspection/items/%d/records/create' % t)
        post_data = {
            '_token': re.findall("\"csrf-token\" content=\"(.*?)\">", await create_page.text())[0],
            'temperature': 36.5,
            'suspicious_respiratory_symptoms': 0,
            'symptom_descriptions': ''
        }
        post_insp = await self.session.post(
            'https://e-report.neu.edu.cn/inspection/items/%d/records' % t, data=post_data)
        return True
    
