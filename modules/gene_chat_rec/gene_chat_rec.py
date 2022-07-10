import re
from datetime import datetime

from loguru import logger
import asyncio
from graia.ariadne.app import Ariadne
from graia.ariadne.event.message import GroupMessage, MessageEvent, FriendMessage, TempMessage, StrangerMessage
from graia.ariadne.message.element import Plain, At, AtAll, Face, Image, ForwardNode, Forward
from graia.ariadne.message.chain import MessageChain, Source
from graia.ariadne.connection.config import HttpClientConfig,WebsocketClientConfig,config
from graia.ariadne.model import Group, Stranger, Friend, Member, Client, Union, MemberPerm
from graia.ariadne.message.parser.base import DetectPrefix, MentionMe

from graia.saya import Channel
from graia.saya.builtins.broadcast.schema import ListenerSchema
from graia.ariadne.util.interrupt import FunctionWaiter

from utils.tools import SendMessage

channel = Channel.current()

@channel.use(ListenerSchema(listening_events=[MessageEvent],decorators=[DetectPrefix("生成聊天记录")]))
async def record(app: Ariadne, event: MessageEvent, sender: Union[Friend, Member, Client, Stranger], source: Source, message: MessageChain):
    await SendMessage(app, MessageChain(Plain("请输入聊天记录的内容\n格式为[@发言人] 内容\n用 输入完成 结束\n可用 创建用户 [目标QQ号] [目标群名片] 来创建一个虚拟用户\n2分钟内无应答自动退出")), sender, event.type)
    fwd_nodeList = []
    cnt = 0
    async def detected_event(self, new_event: MessageEvent, new_sender: Union[Friend, Member, Client, Stranger], new_message: MessageChain, source: Source):
        if sender.id == new_sender.id:
            if(type == 'GroupMessage'):
                if sender.group == new_sender.group:
                    return new_message, source
            else:
                return new_message, source
    while(True):
        cnt += 1
        try:
            ret_msg, source = await FunctionWaiter(detected_event, [MessageEvent]).wait(timeout=120)
        except asyncio.exceptions.TimeoutError:
            await SendMessage(app, MessageChain(Plain("超时,聊天记录生成模式自动退出")), sender, event.type)
            return
        msg_str = str(ret_msg)
        if(msg_str == "输入完成"):
            break
        if(msg_str[0:4] == "创建用户"):
            param = msg_str[4:].strip()
            div = re.search(' ', param)
            if(div == None):
                await SendMessage(app, MessageChain(Plain("错误的格式,应为 创建用户 [目标QQ号] [目标群名片]")), sender, event.type, source=source, force_quote=1)
                cnt -= 1
                continue
            id = int(param[0:div.span()[0]])
            name = param[div.span()[0]+1:].strip()
            await SendMessage(app, MessageChain(Plain("完成,请输入消息")), sender, event.type, source=source,force_quote=1)
            try:
                txt_msg, source = await FunctionWaiter(detected_event, [MessageEvent]).wait(timeout=120)
            except asyncio.exceptions.TimeoutError:
                await SendMessage(app, MessageChain(Plain("超时,聊天记录生成模式自动退出")), sender, event.type)
                return
            text = str(txt_msg[Plain][0]).strip()
        else:
            if(len(ret_msg[At]) == 0):
                if(type == 'GroupMessage'):
                    await SendMessage(app, MessageChain(Plain("错误的格式,应为 [@发言人] 内容\n或者使用创建用户指令")), sender, event.type, source=source, force_quote=1)
                else:
                    await SendMessage(app, MessageChain(Plain("错误的格式,应使用创建用户指令")), sender, event.type, source=source, force_quote=1)
                cnt -= 1
                continue
            at_member = ret_msg[At][0]
            member: Member = await app.getMember(group=sender.group, member_id=int(at_member.target))
            name = member.memberName
            id = member.id
            text = str(ret_msg[Plain][0]).strip()
        logger.info("记录完成")
        fwd_nodeList.append(
            ForwardNode(
                target=id,
                senderName=name,
                time=datetime.now(),
                message=MessageChain(Plain(text)),
            ))
        await SendMessage(app, MessageChain(Plain("记录完成，目前已有" + str(cnt) + "条")), sender, event.type, source=source,force_quote=1)
    if(cnt > 0):
        await SendMessage(app, MessageChain(Forward(nodeList=fwd_nodeList)), sender, event.type, no_group_mention=1)
    else:
        await SendMessage(app, MessageChain(Plain("无有效记录,跳过发送")), sender, event.type)