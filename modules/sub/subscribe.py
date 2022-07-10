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
from modules.neu.NEU import NeuStu

channel = Channel.current()

@channel.use(ListenerSchema(listening_events=[MessageEvent]))
async def subscribe(app: Ariadne, event: MessageEvent, sender: Union[Friend, Member, Client, Stranger], source: Source, message: MessageChain = DetectPrefix("订阅")):
    from core.load_param import sql
    param = str(message).strip()
    if(len(param) == 0):
        await SendMessage(app, MessageChain(Plain("指令格式: 订阅 [需要订阅的功能] [其他参数]")), sender, event.type)
        return
    if(param[0:4] == '健康打卡' or param[0:4] == '健康上报'):
        data = await sql.select_one("eone_neu", "id", str(sender.id))
        if(not data):
            await SendMessage(app, MessageChain(Plain("你还没有绑定一网通账号，请使用 绑定 指令完成一网通账号绑定")), sender, event.type)
            return
        account = data[0]['eone_id']
        password = data[0]['eone_passwd']
        stu = NeuStu(int(account), password)
        await stu.init()
        if(stu.init_down == False):
            await SendMessage(app, MessageChain("登录一网通办失败，请检查你的账号密码并重新绑定"), sender, event.type)
            return
        parm = param[4:].strip()
        tag = 0
        if('早' in parm):
            tag += (1 << 0)
        if('中' in parm):
            tag += (1 << 1)
        if('晚' in parm):
            tag += (1 << 2)
        data = await sql.select_one("jkdk_subscribe","id",str(sender.id))
        if(not data):
            insert_parm = (str(sender.id), str(tag))
            await sql.insert_one("jkdk_subscribe", insert_parm)
        else:
            await sql.update_one("jkdk_subscribe", "id",
                           str(sender.id), "tag", str(tag))
        str_ = ''
        if(tag & (1 << 0)):
            str_ += '早上 '
        if(tag & (1 << 1)):
            str_ +='中午 '
        if(tag & (1 << 2)):
            str_ += '晚上 '
        await SendMessage(app, MessageChain(Plain("订阅健康打卡 " + str_ + "成功")), sender, event.type)
        return
    await SendMessage(app, MessageChain(Plain("未知的参数，指令格式: 订阅 [需要订阅的功能] [其他参数]")), sender, event.type)

@channel.use(ListenerSchema(listening_events=[MessageEvent]))
async def desubscribe(app: Ariadne, event: MessageEvent, sender: Union[Friend, Member, Client, Stranger], source: Source, message: MessageChain = DetectPrefix("取消订阅")):
    from core.load_param import sql
    param = str(message).strip()
    if(len(param) == 0):
        await SendMessage(app, MessageChain(Plain("指令格式: 取消订阅 [需要取消订阅的功能]")), sender, event.type)
        return
    if(param[0:4] == '健康打卡' or param[0:4] == '健康上报'):
        parm = param[4:].strip()
        tag = 0
        if('早' in parm):
            tag += (1 << 0)
        if('中' in parm):
            tag += (1 << 1)
        if('晚' in parm):
            tag += (1 << 2)
        data = await sql.select_one("jkdk_subscribe", "id", str(sender.id))
        if(not data):
            await SendMessage(app, MessageChain(Plain("您没有订阅健康打卡")), sender, event.type)
            return
        else:
            await sql.delete_one("jkdk_subscribe", "id",str(sender.id))
        await SendMessage(app, MessageChain(Plain("取消订阅健康打卡 成功")), sender, event.type)
        return
    await SendMessage(app, MessageChain(Plain("未知的参数，指令格式: 取消订阅 [需要取消订阅的功能]")), sender, event.type)