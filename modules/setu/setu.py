import aiohttp
import json

import numpy as np
from fuzzywuzzy import fuzz
import asyncio

class setu(object):
    api_key = ''
    api_secret = ''

    def __init__(self):
        self.session = aiohttp.ClientSession()
        
    def __del__(self):
        loop = asyncio.get_event_loop()
        if loop.is_running():
            loop.create_task(self.session.close())
        else:
            loop.run_until_complete(self.session.close())
        
    async def contact_lolicon(self, param='', r18: int = 0):
        ret = {}
        __json = {'proxy': 'i.pixiv.re',
                  'r18': r18,
                  'size': ["regular"]
                  }
        if(param !=''):
            __json['tag'] = param.split()
        try:
            async with self.session.post('https://api.lolicon.app/setu/v2', json=__json,timeout=2) as submit:
                info = await submit.json()
                info = info.get('data')
        except:
            return ret
        
        if(len(info) == 0):
            return ret
        
        ret['title'] = info[0]['title']
        ret['author'] = info[0]['author']
        ret['tags'] = info[0]['tags']
        ret['pid'] = info[0]['pid']
        ret['uid'] = info[0]['uid']
        ret['url'] = info[0]['urls']['regular']
        return ret

    async def contact_lolisuki(self, param='', r18: int = 0,level: str = ''):
        ret = {}
        if(level == ''):
            if(r18):
                level='5-6'
            else:
                level='0-4'
        __json = {'proxy': 'i.pixiv.re',
                  'num': 1,
                  'r18': r18,
                  'level': level
                  }
        if(param !=''):
            __json['tag'] = param.split()
            __json['num'] = 1
        try:
            async with self.session.post('https://lolisuki.cc/api/setu/v1', json=__json,timeout=2) as submit:
                info = await submit.json()
                info = info.get('data')
        except:
            return ret
        
        if(len(info) == 0):
            return ret
        
        ret['title'] = info[0]['title']
        ret['author'] = info[0]['author']
        ret['tags'] = info[0]['tags']
        ret['pid'] = info[0]['pid']
        ret['uid'] = info[0]['uid']
        ret['url'] = info[0]['urls']['regular']
        return ret
        

    async def contact_local(self, param='', r18: int = 0):
        from core.load_param import setu_json
        list_len = len(setu_json)
        ret = {}
        if(param == ''):
            target = np.random.randint(0, list_len, 1)[0]
            r18_info = setu_json[target]['r18']
            while(r18_info ^ r18):
                target = np.random.randint(0, list_len, 1)[0]
                r18_info = setu_json[target]['r18']
            ret = setu_json[target]
        else:
            result_list = []
            for i in range(list_len):
                cnt = setu_json[i]
                r18_info = cnt['r18']
                if(r18_info ^ r18):
                    continue
                title = cnt['artwork']['title']
                author = cnt['author']
                author_name = author['name']
                img_tag = cnt['tags']
                look_str = title + ' ' + author_name + ' '
                for t in img_tag:
                    look_str = look_str + t + ' '
                param_list = param.split()
                rate = 0
                for p in param_list:
                    rate = rate + fuzz.partial_token_sort_ratio(p,look_str)
                rate = rate / len(param_list)
                if(rate > 80):
                    result_list.append(i)
            if(len(result_list)>0):
                target = np.random.randint(0, len(result_list), 1)[0]
                ret = setu_json[result_list[target]]
        if(ret == {}):
            return ret
        ret_dict={}
        ret_dict['title'] = ret['artwork']['title']
        ret_dict['author'] = ret['author']['name']
        ret_dict['tags'] = ret['tags']
        ret_dict['pid'] = ret['artwork']['id']
        ret_dict['uid'] = ret['author']['id']
        ret_dict['url'] = ret['urls']['large'].replace('https://i.pximg.net','https://i.pixiv.re').replace('_webp','')
        return ret_dict

    async def contact(self, param='', r18: int = 0):
        ret = {}
        chose = np.random.randint(0, 3, 1)[0]
        if(chose == 0):
            ret = await self.contact_lolicon(param,r18)
            if(ret == {}):
                ret = await self.contact_lolisuki(param,r18)
                chose = 1
        elif(chose == 1):
            ret = await self.contact_lolisuki(param,r18)
            if(ret == {}):
                ret = await self.contact_lolicon(param,r18)
                chose = 0
        if(ret == {}):
            ret = await self.contact_local(param,r18)
            chose = 2
            if(ret == {}):
                chose = np.random.randint(0, 2, 1)[0]
                if(chose == 0):
                    ret = await self.contact_lolicon(param,r18)
                    if(ret == {}):
                        ret = await self.contact_lolisuki(param,r18)
                        chose = 1
                elif(chose == 1):
                    ret = await self.contact_lolisuki(param,r18)
                    if(ret == {}):
                        ret = await self.contact_lolicon(param,r18)
                        chose = 0
                if(ret == {}):
                    return ret
        ret['chose'] = chose
        return ret
            
    async def get_image(self,url):
        from core.load_param import config_json
        proxy = config_json['proxy']
        if(config_json['proxy_open']):
            async with self.session.get(url, proxies=proxy) as r:
                data = await r.read()
        else:
            async with self.session.get(url) as r:
                data = await r.read()
        
        return data
    
setu_bot = setu()
        