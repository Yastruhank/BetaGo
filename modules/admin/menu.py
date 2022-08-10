import os
import json
import pkgutil
import re
from loguru import logger

import asyncio
from graia.ariadne.app import Ariadne
from graia.ariadne.event.message import GroupMessage, MessageEvent, FriendMessage, TempMessage, StrangerMessage
from graia.ariadne.message.element import Plain, At, AtAll, Face, Image
from graia.ariadne.message.chain import MessageChain, Source
from graia.ariadne.connection.config import HttpClientConfig,WebsocketClientConfig,config
from graia.ariadne.model import Group, Stranger, Friend, Member, Client, Union, MemberPerm
from graia.ariadne.message.parser.base import DetectPrefix

from graia.saya import Channel
from graia.saya.builtins.broadcast.schema import ListenerSchema

from utils.tools import SendMessage

class Menu(object):
    module_to_json = {}
    command_list = []
    
    def __init__(self, channel_list,hidden:int = 0):
        self.hidden = hidden
        self.channel_list = channel_list
        
    async def get_module(self):
        module_list = []
        for channel in self.channel_list:
            div = re.split(r'\.',channel)
            if(len(div) < 3):
                continue
            json_path = './' + div[0] + '/' + div[1] + '/module.json'
            if not os.path.exists(json_path):
                continue
            with open(json_path, "r") as json_file:
                json_content = json.load(json_file)
                for command in json_content['command']:
                    if(command['from'] in self.channel_list and command['hidden'] == self.hidden):
                        if(not json_content['name'] in module_list):
                            module_list.append(json_content['name'])
                            self.module_to_json[json_content['name']] = json_path
                        break
        return module_list
    
    async def get_command_list(self,name):
        await self.get_module()
        if(not name in self.module_to_json):
            return '',[]
        command_name_list = []
        description = ''
        with open(self.module_to_json[name], "r") as json_file:
                json_content = json.load(json_file)
                description = json_content['description']
                for command in json_content['command']:
                    if(command['from'] in self.channel_list and command['hidden'] == self.hidden):
                        command_name_list.append(command['name'])
                        self.command_list.append(command)
                        
        return description,command_name_list
    
    async def get_command_info(self,module_name,command_name):
        await self.get_command_list(module_name)
        for command in self.command_list:
            if(command['name'] == command_name):
                return command
        return None

channel = Channel.current()

@channel.use(ListenerSchema(listening_events=[MessageEvent]))
async def menu(app: Ariadne, event: MessageEvent, sender: Union[Friend, Member, Client, Stranger], source: Source, message: MessageChain = DetectPrefix("菜单")):
    from core.load_param import channel_list
    param = str(message).strip()
    param_list = param.split()
    menu = Menu(channel_list,0)
    if(len(param_list) == 0):
        modules = await menu.get_module()
        reply = ' BetaGo菜单:\n当前包含以下模块\n'
        for module  in modules:
            reply = reply + '\t->' + module +'\n'
        reply = reply + '可以使用 菜单 [模块名] 进一步查看模块的信息\n'
        reply = reply + '本项目采用AGPL开源,开源地址为https://github.com/Yastruhank/BetaGo,欢迎参与开发'
        await SendMessage(app, MessageChain(Plain(reply)), sender, event.type)
    elif(len(param_list)==1):
        desc,comm = await menu.get_command_list(param_list[0])
        if(len(comm) == 0):
            await SendMessage(app, MessageChain(Plain('未找到指定模块:{' + str(param_list[0]) + '}')), sender, event.type)
        reply = 'BetaGo菜单:\n模块名称: ' + param_list[0] + '\n'
        reply = reply + '模块描述: ' + desc + '\n'
        reply = reply +'包含以下指令:\n'
        for c in comm:
            reply = reply + '\t->' + c +'\n'
        reply = reply + '可以使用 菜单 [模块名] [指令名] 进一步查看指令的用法\n'
        reply = reply + '本项目采用AGPL开源,开源地址为https://github.com/Yastruhank/BetaGo,欢迎参与开发'
        await SendMessage(app, MessageChain(Plain(reply)), sender, event.type)
    elif(len(param_list)==2):
        comm = await menu.get_command_info(param_list[0],param_list[1])
        if(comm == None):
            await SendMessage(app, MessageChain(Plain('未找到指定模块{' + str(param_list[0]) + '}下的指定指令{' + str(param_list[1]) + '}')), sender, event.type)
        reply = 'BetaGo菜单:\n指令名称: ' + param_list[1] + '\n'
        reply = reply + '指令描述: ' + comm['description'] + '\n'
        reply = reply + '指令用法: ' + comm['usage'] + '\n'
        reply = reply + '本项目采用AGPL开源,开源地址为https://github.com/Yastruhank/BetaGo,欢迎参与开发'
        await SendMessage(app, MessageChain(Plain(reply)), sender, event.type)
    else:
        await SendMessage(app, MessageChain(Plain('错误的指令用法: 参数过多')), sender, event.type)
    
    
@channel.use(ListenerSchema(listening_events=[MessageEvent]))
async def hide_menu(app: Ariadne, event: MessageEvent, sender: Union[Friend, Member, Client, Stranger], source: Source, message: MessageChain = DetectPrefix("隐藏菜单")):
    if(event.type == 'GroupMessage' and sender.permission == MemberPerm.Member):
        await SendMessage(app, MessageChain(Plain("权限不足,隐藏菜单仅限群管理员查看")), sender, event.type)
        return
    from core.load_param import channel_list
    param = str(message).strip()
    param_list = param.split()
    menu = Menu(channel_list,1)
    if(len(param_list) == 0):
        modules = await menu.get_module()
        reply = ' BetaGo隐藏菜单:\n当前包含以下模块\n'
        for module  in modules:
            reply = reply + '\t->' + module +'\n'
        reply = reply + '可以使用 隐藏菜单 [模块名] 进一步查看模块的信息\n'
        reply = reply + '本项目采用AGPL开源,开源地址为https://github.com/Yastruhank/BetaGo,欢迎参与开发'
        await SendMessage(app, MessageChain(Plain(reply)), sender, event.type)
    elif(len(param_list)==1):
        desc,comm = await menu.get_command_list(param_list[0])
        if(len(comm) == 0):
            await SendMessage(app, MessageChain(Plain('未找到指定模块:{' + str(param_list[0]) + '}')), sender, event.type)
        reply = 'BetaGo隐藏菜单:\n模块名称: ' + param_list[0] + '\n'
        reply = reply + '模块描述: ' + desc + '\n'
        reply = reply +'包含以下指令:\n'
        for c in comm:
            reply = reply + '\t->' + c +'\n'
        reply = reply + '可以使用 隐藏菜单 [模块名] [指令名] 进一步查看指令的用法\n'
        reply = reply + '本项目采用AGPL开源,开源地址为https://github.com/Yastruhank/BetaGo,欢迎参与开发'
        await SendMessage(app, MessageChain(Plain(reply)), sender, event.type)
    elif(len(param_list)==2):
        comm = await menu.get_command_info(param_list[0],param_list[1])
        if(comm == None):
            await SendMessage(app, MessageChain(Plain('未找到指定模块{' + str(param_list[0]) + '}下的指定指令{' + str(param_list[1]) + '}')), sender, event.type)
        reply = 'BetaGo隐藏菜单:\n指令名称: ' + param_list[1] + '\n'
        reply = reply + '指令描述: ' + comm['description'] + '\n'
        reply = reply + '指令用法: ' + comm['usage'] + '\n'
        reply = reply + '本项目采用AGPL开源,开源地址为https://github.com/Yastruhank/BetaGo,欢迎参与开发'
        await SendMessage(app, MessageChain(Plain(reply)), sender, event.type)
    else:
        await SendMessage(app, MessageChain(Plain('错误的指令用法: 参数过多')), sender, event.type)