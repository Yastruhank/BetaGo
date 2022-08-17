import re

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
from .NEU_EduSys import NEU_EduSys

channel = Channel.current()

@channel.use(ListenerSchema(listening_events=[MessageEvent]))
async def GetScore(app: Ariadne, event: MessageEvent, sender: Union[Friend, Member, Client, Stranger], source: Source, message: MessageChain = DetectPrefix("查询绩点")):
    from core.load_param import sql
    sender_id = str(sender.id)
    data = await sql.select_one("eone_neu", "id", sender_id)
    if(not data):
        await SendMessage(app, MessageChain("你还没有绑定一网通账号，请使用 绑定 指令完成一网通账号绑定"), sender, event.type)
        return
    account = data[0]['eone_id']
    password = data[0]['eone_passwd']
    stu = NEU_EduSys(int(account), password)
    await SendMessage(app, MessageChain("正在查询,请稍候"), sender, event.type)
    await stu.init()
    if(stu.init_down == False):
        await SendMessage(app, MessageChain("登录一网通办失败，请检查你的账号密码并重新绑定"), sender, event.type)
        return
    score = await stu.getScore()
    await SendMessage(app, MessageChain("查询成功,你的总平均绩点为：" + str(score)), sender, event.type)

@channel.use(ListenerSchema(listening_events=[MessageEvent]))
async def GetSubjectScore(app: Ariadne, event: MessageEvent, sender: Union[Friend, Member, Client, Stranger], source: Source, message: MessageChain = DetectPrefix("查询学科成绩")):
    from core.load_param import sql
    search_str = str(message).strip()
    sender_id = str(sender.id)
    data = await sql.select_one("eone_neu", "id", sender_id)
    if(not data):
        await SendMessage(app, MessageChain("你还没有绑定一网通账号，请使用 绑定 指令完成一网通账号绑定"), sender, event.type)
        return
    account = data[0]['eone_id']
    password = data[0]['eone_passwd']
    stu = NEU_EduSys(int(account), password)
    await SendMessage(app, MessageChain("正在查询,请稍候"), sender, event.type)
    await stu.init()
    if(stu.init_down == False):
        await SendMessage(app, MessageChain("登录一网通办失败，请检查你的账号密码并重新绑定"), sender, event.type)
        return
    score = await stu.getClassScore()
    txt = ''
    for i in range(len(score[0])):
        class_name = score[0][i].text.strip()
        if(len(search_str)>0):
            target = re.search(search_str, class_name)
            if(target == None):
                continue
        txt = txt + '学科:' + class_name + '\n'
        class_weight = score[1][i].text.strip()
        txt = txt + '学分:' + class_weight + '\n'
        class_score = score[2][i].text.strip()
        txt = txt + '成绩:' + class_score + '\n\n'
    await SendMessage(app, MessageChain("查询成功,结果如下:\n" + txt.strip()), sender, event.type)