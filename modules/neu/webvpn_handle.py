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

@channel.use(ListenerSchema(listening_events=[MessageEvent]))
async def GetWebVPN(app: Ariadne, event: MessageEvent, sender: Union[Friend, Member, Client, Stranger], source: Source, message: MessageChain = DetectPrefix("webvpn解析")):
    from modules.neu.webvpn import webvpn
    url = str(message).strip()
    if(len(url) == 0):
        await SendMessage(app, MessageChain(Plain("指令格式: webvpn解析 [协议(支持http,https,ssh,rdp,vnc,默认http)]://[需要解析的地址]:[端口,http与https可不填]/[后续地址]\n"
                                                          + "示例： webvpn解析 https://baidu.com 或 webvpn解析 vnc://192.168.1.1:3389")), sender, event.type)
        return
    encryp_url = webvpn.get_encryp_url(url)
    await SendMessage(app, MessageChain(Plain("WebVPN解析完成,WebVPN仅供校外访问,请注意.地址为:")), sender, event.type)
    await SendMessage(app, MessageChain(Plain(encryp_url)), sender, event.type)