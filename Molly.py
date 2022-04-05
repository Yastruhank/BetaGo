import requests
import json
import re
import time


class Molly(object):
    api_key = ''
    api_secret = ''
    __headers = {}

    def __init__(self, api_key, api_secret):
        requests.packages.urllib3.disable_warnings()
        self.api_key = api_key
        self.api_secret = api_secret
        self.__headers = {'Api-Key': self.api_key,
                          'Api-Secret': self.api_secret,
                          'Content-Type': 'application/json;charset=UTF-8'
                          }
        self.session = requests.Session()

    def contact(self, str, type, id, name, group=0, group_name=''):
        __json = {'content': str,
                  'type': type,
                  'from': id,
                  'fromName': name,
                  }
        if(type == 2):
            __json['to'] = group
            __json['toName'] = group_name
        submit = self.session.post('https://i.mly.app/reply',
                                   headers=self.__headers, json=__json)
        return submit
