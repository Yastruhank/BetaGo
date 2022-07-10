from graia.ariadne.app import Ariadne
from graia.ariadne.event.message import GroupMessage, MessageEvent, FriendMessage, TempMessage, StrangerMessage
from graia.ariadne.message.element import Plain, At, AtAll, Face, Image
from graia.ariadne.message.chain import MessageChain, Source
from graia.ariadne.connection.config import HttpClientConfig,WebsocketClientConfig,config
from graia.ariadne.model import Group, Stranger, Friend, Member, Client, Union, MemberPerm
from graia.ariadne.message.parser.base import DetectPrefix

from graia.saya import Channel
from graia.saya.builtins.broadcast.schema import ListenerSchema

from utils.tools import SendMessage,addtwodimdict
from modules.neu.NEU import NeuStu

channel = Channel.current()

@channel.use(ListenerSchema(listening_events=[MessageEvent],decorators=[DetectPrefix("绑定")]))
async def binding(app: Ariadne, event: MessageEvent, sender: Union[Friend, Member, Client, Stranger], source: Source, message: MessageChain):
    from core.load_param import sql
    str_prefix = ''
    if(event.type == 'GroupMessage'):
        str_prefix = '[本指令可以且推荐私聊完成]\n'
    if(len(str(message)) < 16 or str(message)[2] != ' ' or str(message)[11] != ' '):
        await SendMessage(app, MessageChain(str_prefix + "错误的指令格式\n应输入 绑定 [学号] [密码]"), sender, event.type)
        return
    account = str(message)[3:12]
    password = str(message)[12:]
    sender_id = str(sender.id)
    stu = NeuStu(int(account), password)
    await stu.init()
    if(stu.init_down == False):
        await SendMessage(app, MessageChain(str_prefix + "登录失败，请检查账号或密码"), sender, event.type)
        return
    if(await sql.select_one("eone_neu", "id", sender_id)):
        await sql.delete_one("eone_neu", "id", sender_id)
    param = (sender_id, account, password)
    await sql.insert_one("eone_neu", param)
    await SendMessage(app, MessageChain(str_prefix + "完成，你可以再次使用该指令替换绑定账号"), sender, event.type)