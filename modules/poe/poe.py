import poe
import logging
import datetime
from graia.ariadne.app import Ariadne
from graia.ariadne.event.message import MessageEvent
from graia.ariadne.message.chain import MessageChain, Source
from graia.ariadne.model import Stranger, Friend, Member, Client, Union
from graia.ariadne.message.parser.base import DetectPrefix
from graia.saya.builtins.broadcast.schema import ListenerSchema
from graia.saya import Channel
from utils.tools import SendMessage
from core.load_param import config_json


poe.headers = {
  "User-Agent": "Mozilla/5.0 (Linux; U; Android 4.0.2; en-us; Galaxy Nexus Build/ICL53F) AppleWebKit/534.30 (KHTML, like Gecko) Version/4.0 Mobile Safari/534.30",
  "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8",
  "Accept-Encoding": "gzip, deflate, br",
  "Accept-Language": "en-US,en;q=0.5",
  "Te": "trailers",
  "Upgrade-Insecure-Requests": "1"
}
poe.logger.setLevel(logging.INFO)
token = config_json["poe_api"]
client = poe.Client(token, proxy="socks5:"+config_json["proxy"]["socks5"])
last_chat_time = datetime.datetime.now()
channel = Channel.current()
name = config_json["poe_name"]

@channel.use(ListenerSchema(listening_events=[MessageEvent]))
async def poe_sent(app: Ariadne, event: MessageEvent, sender: Union[Friend, Member, Client, Stranger], source: Source,  message: MessageChain = DetectPrefix("/poe")):
    global last_chat_time, name
    if (datetime.datetime.now() - last_chat_time).total_seconds()<20.0:
        await SendMessage(app, MessageChain('禁止频繁对话'), sender, event.type)
    input_str = str(message).strip()
    if len(input_str) == 0:
        await SendMessage(app, MessageChain('错误的文本输入'), sender, event.type)
        return
    for chunk in client.send_message(name, message):
        pass
    result = chunk["text"]
    await SendMessage(app, MessageChain(result), sender, event.type)
    pass


@channel.use(ListenerSchema(listening_events=[MessageEvent]))
async def poe_sent(app: Ariadne, event: MessageEvent, sender: Union[Friend, Member, Client, Stranger], source: Source,  message: MessageChain = DetectPrefix("/poetoken")):
    global token,client
    token = str(message).strip()
    client = poe.Client(token,proxy="socks5:"+config_json["proxy"]["socks5"])
    await SendMessage(app, MessageChain("token更新完成"), sender, event.type)
    pass

@channel.use(ListenerSchema(listening_events=[MessageEvent]))
async def poe_sent(app: Ariadne, event: MessageEvent, sender: Union[Friend, Member, Client, Stranger], source: Source,  message: MessageChain = DetectPrefix("/poeclear")):
    global name
    client.send_chat_break(name)
    await SendMessage(app, MessageChain("对话清空"), sender, event.type)
    pass
