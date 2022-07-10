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

channel = Channel.current()

@channel.use(ListenerSchema(listening_events=[MessageEvent],decorators=[MentionMe()]))
async def contact_bot(app: Ariadne, event: MessageEvent, sender: Union[Friend, Member, Client, Stranger], source: Source, message: MessageChain):
    from modules.chat.Molly import molly_bot
    if(event.type == 'GroupMessage'):
        reply = await molly_bot.contact(str(
            message[Plain][0]), 2, sender.id, sender.name, sender.group.id, sender.group.name)
    else:
        reply = await molly_bot.contact(
            str(message[Plain][0]), 1, sender.id, sender.nickname)
    content = reply.get('data')[0].get('content')
    await SendMessage(app, MessageChain(Plain(content)), sender, event.type)