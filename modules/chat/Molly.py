import aiohttp
import asyncio

class Molly(object):
    api_key = ''
    api_secret = ''
    __headers = {}

    def __init__(self, api_key, api_secret):
        self.api_key = api_key
        self.api_secret = api_secret
        self.__headers = {'Api-Key': self.api_key,
                          'Api-Secret': self.api_secret,
                          'Content-Type': 'application/json;charset=UTF-8'
                          }
        self.session = aiohttp.ClientSession()
        
    def __del__(self):
        loop = asyncio.get_event_loop()
        if loop.is_running():
            loop.create_task(self.session.close())
        else:
            loop.run_until_complete(self.session.close())

    async def contact(self, str, type, id, name, group=0, group_name=''):
        __json = {'content': str,
                  'type': type,
                  'from': id,
                  'fromName': name,
                  }
        if(type == 2):
            __json['to'] = group
            __json['toName'] = group_name
        submit = await self.session.post('https://i.mly.app/reply',
                                   headers=self.__headers, json=__json)
        json_data = await submit.json()
        return json_data.get('data')[0].get('content')

from core.load_param import config_json
molly_bot = Molly(config_json['Molly_Api-Key'], config_json['Molly_Api-Secret'])
