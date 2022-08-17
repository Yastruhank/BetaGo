from graia.ariadne.app import Ariadne
from graia.ariadne.event.message import GroupMessage, MessageEvent, FriendMessage, TempMessage, StrangerMessage
from graia.ariadne.message.element import Plain, At, AtAll, Face, Image
from graia.ariadne.message.chain import MessageChain, Source
from graia.ariadne.model import Group, Stranger, Friend, Member, Client, Union

import asyncio
from graia.ariadne.app import Ariadne
from graia.ariadne.event.message import GroupMessage, MessageEvent, FriendMessage, TempMessage, StrangerMessage
from graia.ariadne.message.element import Plain, At, AtAll, Face, Image
from graia.ariadne.message.chain import MessageChain, Source
from graia.ariadne.connection.config import HttpClientConfig,WebsocketClientConfig,config
from graia.ariadne.model import Group, Stranger, Friend, Member, Client, Union, MemberPerm

from graia.saya import Channel
from graia.saya.builtins.broadcast.schema import ListenerSchema

from utils.tools import SendMessage


channel = Channel.current()

@channel.use(ListenerSchema(listening_events=[MessageEvent]))
async def getup(app: Ariadne, event: MessageEvent, sender: Union[Friend, Member, Client, Stranger], source: Source, message: MessageChain):
    from .setu import setu_bot
    param = ''
    if(str(message)[0:4] == '来点涩图' or str(message)[0:4] == '来点色图'):
        if(len(str(message))>4):
            param = str(message)[4:].strip()
    else:
        if(str(message)[0:3] == '搜涩图' or str(message)[0:3] == '搜色图'):
            if(len(str(message)) > 3):
                param = str(message)[3:].strip()
        else:
            return
    r18 = 0
    if(param[0:3]=='r18'):
        r18 = 1
        param = param[3:].strip()
    reply = await setu_bot.contact(param,r18)
    if(reply == {}):
        await SendMessage(app, MessageChain("抱歉，未找到结果"), sender, event.type)
        return
    else:
        reply_str = '欧尼酱,你的色图哒哟\n'
        reply_str = reply_str + '标题:' + reply['title'] + '\n'
        reply_str = reply_str + '作品id:' + str(reply['pid']) + '\n'
        reply_str = reply_str + '作者:' + reply['author'] + '\n'
        reply_str = reply_str + '作者id:' + str(reply['uid']) + '\n'
        reply_str = reply_str + '作品tags::' + str(reply['tags']) + '\n'
        if(reply['chose'] == 0):
            reply_str = reply_str + '来源:' + 'Lolicon.api'
        elif(reply['chose'] == 1):
            reply_str = reply_str + '来源:' + 'Lolisuki.api'
        elif(reply['chose'] == 2):
            reply_str = reply_str + '来源:' + 'Local'
        else:
            reply_str = reply_str + '发生错误,来源未知'
        await SendMessage(app, MessageChain(Plain(reply_str)), sender, event.type)
    img_url = reply['url']
    data = await setu_bot.get_image(img_url)
    try:
        await SendMessage(app, MessageChain(Image(data_bytes=data)), sender, event.type,no_group_mention=1)
    except Exception as e:
        await SendMessage(app, MessageChain(Plain('发送图片时发生错误,错误信息为:' + str(e) + '\n需要发送的图片url为:' + img_url)), sender, event.type)