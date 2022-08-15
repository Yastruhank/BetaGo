from graia.ariadne.app import Ariadne
from graia.ariadne.event.message import GroupMessage, MessageEvent, FriendMessage, TempMessage, StrangerMessage
from graia.ariadne.message.element import Plain, At, AtAll, Face, Image
from graia.ariadne.message.chain import MessageChain, Source
from graia.ariadne.connection.config import HttpClientConfig,WebsocketClientConfig,config
from graia.ariadne.model import Group, Stranger, Friend, Member, Client, Union, MemberPerm
from graia.ariadne.message.parser.base import DetectPrefix, MentionMe

from graia.saya import Channel
from graia.saya.builtins.broadcast.schema import ListenerSchema

from utils.tools import SendMessage

from modules.chat.Molly import molly_bot
from modules.chat.Turing import turing_bot
from modules.chat.DialogBot import dialogbot

channel = Channel.current()

@channel.use(ListenerSchema(listening_events=[MessageEvent],decorators=[MentionMe()]))
async def contact_bot(app: Ariadne, event: MessageEvent, sender: Union[Friend, Member, Client, Stranger], source: Source, message: MessageChain):
    from core.load_param import config_json
    bot = dialogbot
    if config_json['chat_type'] == 1:
        bot = turing_bot
    if config_json['chat_type'] == 2:
        bot = molly_bot
                             
    if(event.type == 'GroupMessage'):
        content = await bot.contact(str(message), 2, sender.id, sender.name, sender.group.id, sender.group.name)
    else:
        content = await bot.contact(str(message), 1, sender.id, sender.nickname)

        
    await SendMessage(app, MessageChain(Plain(content)), sender, event.type)
    
    
@channel.use(ListenerSchema(listening_events=[MessageEvent]))
async def set_chat(app: Ariadne, event: MessageEvent, sender: Union[Friend, Member, Client, Stranger], source: Source, message: MessageChain = DetectPrefix("设置聊天机器人")):
    if sender.id != 359360997:
        await SendMessage(app, MessageChain(Plain('权限不足')), sender, event.type)
        return
    param = str(message).strip()
    try:
        from core.load_param import config_json
        id = int(param)
        if id < 3 and id >= 0:
            config_json['chat_type'] = id
            await SendMessage(app, MessageChain(Plain('设置成功')), sender, event.type)
        else:
            await SendMessage(app, MessageChain(Plain('错误的参数')), sender, event.type)
    except:
        await SendMessage(app, MessageChain(Plain('错误的参数')), sender, event.type)