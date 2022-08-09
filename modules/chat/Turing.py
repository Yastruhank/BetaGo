import aiohttp
import asyncio

class Turing(object):
    api_key = ''
    api_secret = ''
    __headers = {}

    def __init__(self, api_key):
        self.api_key = api_key
        self.__headers = {'Content-Type': 'application/json;charset=UTF-8'}
        self.session = aiohttp.ClientSession()
        
    def __del__(self):
        loop = asyncio.get_event_loop()
        if loop.is_running():
            loop.create_task(self.session.close())
        else:
            loop.run_until_complete(self.session.close())

    async def contact(self, str, type, id, name, group=0, group_name=''):
        __json = {'reqType':0,
                  'perception': {
                        "inputText": {
                            "text": str,
                        },       
                    },
                    'userInfo': {
                        "apiKey": self.api_key,
                        "userId": id,
                        "userIdName": name,
                    },
                  }
        if(type == 2):
            __json['userInfo']['groupId	'] = group
        submit = await self.session.post('http://openapi.turingapi.com/openapi/api/v2',
                                   headers=self.__headers, json=__json)
        return await submit.json(content_type='text/plain')

from core.load_param import config_json
turing_bot = Turing(config_json['Turing_Api-Key'])
