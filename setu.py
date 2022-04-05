import requests
import json
import re
from graia.ariadne.app import Ariadne
from graia.ariadne.adapter import Adapter
from graia.ariadne import get_running
from graia.ariadne.event.message import GroupMessage, MessageEvent, FriendMessage, TempMessage, StrangerMessage
from graia.ariadne.message.element import Plain, At, AtAll, Face, Image
from graia.ariadne.message.chain import MessageChain, Source
from graia.ariadne.model import Group, MiraiSession, Stranger, Friend, Member, Client, Union
from graia.ariadne.app import MultimediaMixin
import time

class setu(object):
    api_key = ''
    api_secret = ''

    def __init__(self):
        requests.packages.urllib3.disable_warnings()
        self.session = requests.Session()

    def contact(self, str='', r18: int = 0):
        __json = {'proxy': 'i.pixiv.cat',
                  'keyword': str,
                  'r18': r18,
                  'size': ["regular"]
                  }
        submit = self.session.post(
            'https://api.lolicon.app/setu/v2', json=__json)
        return submit
