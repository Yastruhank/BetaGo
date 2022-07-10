import numpy as np
import random
import time

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

channel = Channel.current()

@channel.use(ListenerSchema(listening_events=[GroupMessage]))
async def food(app: Ariadne, group: Group, message: MessageChain = DetectPrefix("谁带饭")):
    members = message[At]
    if(AtAll in message):
        group_member = await app.getMemberList(group)
        for member in group_member:
            members.append(At(member))
    if(len(members) == 0):
        await app.sendMessage(group, MessageChain("错误的指令格式\n应输入 谁带饭 [@第一个候选带饭候选人] [@第二个候选带饭候选人]..."))
        return
    random.seed(time.time())
    num = len(members)
    target = np.random.randint(0, num, 1)[0]
    await app.sendMessage(group, MessageChain(members[target], Plain(" ，就决定由你带饭了"), Face(name = 'doge')))