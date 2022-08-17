import re
from datetime import datetime
import os
import json

from loguru import logger
import asyncio
from graia.ariadne.app import Ariadne
from graia.ariadne.event.message import GroupMessage, MessageEvent, FriendMessage, TempMessage, StrangerMessage
from graia.ariadne.message.element import Plain, At, AtAll, Face, Image, ForwardNode, Forward, Voice
from graia.ariadne.message.chain import MessageChain, Source
from graia.ariadne.connection.config import HttpClientConfig,WebsocketClientConfig,config
from graia.ariadne.model import Group, Stranger, Friend, Member, Client, Union, MemberPerm
from graia.ariadne.message.parser.base import DetectPrefix, MentionMe
from graiax import silkcoder

from graia.saya import Channel
from graia.saya.builtins.broadcast.schema import ListenerSchema
from graia.ariadne.util.interrupt import FunctionWaiter

from utils.tools import SendMessage
from .MoeGoe import MoeGoe
from .translate import tencent_translater
from .voice_recognition import tencent_voice_recognition

channel = Channel.current()

logger.info('Loading TTS model...')
moegoe = MoeGoe('modules/voice_chat/module/365_epochs.pth', 'modules/voice_chat/module/config.json')
if moegoe.init_done:
    logger.info('TTS model loaded.')

@channel.use(ListenerSchema(listening_events=[MessageEvent]))
async def tts(app: Ariadne, event: MessageEvent, sender: Union[Friend, Member, Client, Stranger], source: Source, message: MessageChain = DetectPrefix("语音生成")):
    input_str = str(message).strip()
    if len(input_str) == 0:
        await SendMessage(app, MessageChain('错误的文本输入'), sender, event.type)
        return
    voice_type = 0
    if input_str[0] >='0' and input_str[0] <='6' and input_str[1] == ' ':
        voice_type = int(input_str[0])
        input_str = input_str[2:].strip()
    voice_path = await moegoe.text_to_voice(input_str, voice_type)
    if voice_path == None:
        await SendMessage(app, MessageChain('错误的文本输入'), sender, event.type)
    else:
        await SendMessage(app, MessageChain(Voice(data_bytes=await silkcoder.async_encode(voice_path, rate=48000, codec = 1))), sender, event.type, no_group_mention=1)
        os.remove(voice_path)
        
        
@channel.use(ListenerSchema(listening_events=[MessageEvent]))
async def voice_chat(app: Ariadne, event: MessageEvent, sender: Union[Friend, Member, Client, Stranger], source: Source, message: MessageChain = DetectPrefix("语音聊天模式")):
    async def detected_event(new_event: MessageEvent, new_sender: Union[Friend, Member, Client, Stranger], new_message: MessageChain, source: Source):
        if sender.id == new_sender.id:
            if(type == 'GroupMessage'):
                if sender.group == new_sender.group:
                    return new_message, source
            else:
                return new_message, source
            
    from core.load_param import config_json
    await SendMessage(app, MessageChain('进入语音聊天模式,请使用 退出 指令退出模式\n此模式下任何发言都将会触发机器人语音聊天,2分钟后自动退出'), sender, event.type)
    
    voice_type = 0
    with_text = False
    with_feedback = False
    
    while True:
        try:
            ret_msg, source = await FunctionWaiter(detected_event, [MessageEvent]).wait(timeout=120)
        except asyncio.exceptions.TimeoutError:
            await SendMessage(app, MessageChain(Plain("超时,语音聊天模式自动退出")), sender, event.type)
            return
        
        try:
            if config_json['chat_type'] == 1:
                from modules.chat.Turing import turing_bot
                bot = turing_bot
            elif config_json['chat_type'] == 2:
                from modules.chat.Molly import molly_bot
                bot = molly_bot
            else:
                from modules.chat.DialogBot import dialogbot
                bot = dialogbot
        except:
            logger.error('Chat module was not loaded correctly.')
            await SendMessage(app, MessageChain(Plain("错误:聊天模块未加载,请联系机器人管理员")), sender, event.type)
        
        if Voice in ret_msg:
            voice = Voice(ret_msg)
            if voice.url == None:   #在graia旧版本中存在Voice类的url元素为空的bug,下方为临时解决方案
                json_info = json.loads(str(voice.json()))
                voice.url = json_info['id'][1]['url']
            
            recog_word = tencent_voice_recognition.recognize(voice.url,sender.id)
            
            if with_feedback:
                await SendMessage(app, MessageChain(Plain("语音识别结果:"+recog_word)), sender, event.type)
            
            if(event.type == 'GroupMessage'):
                content = await bot.contact(str(recog_word), 2, sender.id, sender.name, sender.group.id, sender.group.name)
            else:
                content = await bot.contact(str(recog_word), 1, sender.id, sender.nickname)
                
            content.replace('BetaGo','我')
            
            jp_content = tencent_translater.translate(content)
            voice_path = await moegoe.text_to_voice(jp_content, voice_type)
            if voice_path == None:
                await SendMessage(app, MessageChain('文本出错'), sender, event.type)
            else:
                await SendMessage(app, MessageChain(Voice(data_bytes=await silkcoder.async_encode(voice_path, rate=48000, codec = 1))), sender, event.type, no_group_mention=1)
                if with_text:
                    await SendMessage(app, MessageChain(content), sender, event.type)
                os.remove(voice_path)
                
            continue
        
        else:
            if str(ret_msg) == '退出':
                await SendMessage(app, MessageChain(Plain("退出成功")), sender, event.type)
                return
            
            if str(ret_msg) == '开启文本信息':
                await SendMessage(app, MessageChain(Plain("设置成功")), sender, event.type)
                with_text = True
                continue
            
            if str(ret_msg) == '关闭文本信息':
                await SendMessage(app, MessageChain(Plain("设置成功")), sender, event.type)
                with_text = False
                continue
            
            if str(ret_msg) == '开启输入信息':
                await SendMessage(app, MessageChain(Plain("设置成功")), sender, event.type)
                with_feedback = True
                continue
            
            if str(ret_msg) == '关闭输入信息':
                await SendMessage(app, MessageChain(Plain("设置成功")), sender, event.type)
                with_feedback = False
                continue
            
            if str(ret_msg) == '设置音色':
                output_str, speaker_num = moegoe.get_speakers()
                await SendMessage(app, MessageChain(Plain("请选择音色\n" + output_str)), sender, event.type)
                try:
                    ret_msg, source = await FunctionWaiter(detected_event, [MessageEvent]).wait(timeout=120)
                except asyncio.exceptions.TimeoutError:
                    await SendMessage(app, MessageChain(Plain("超时,语音聊天模式自动退出")), sender, event.type)
                    return
                try:
                    chose = int(str(ret_msg))
                    if(chose >=0 and chose < speaker_num):
                        voice_type = chose
                        await SendMessage(app, MessageChain(Plain("设置成功")), sender, event.type)
                    else:
                        await SendMessage(app, MessageChain(Plain("错误的选择,请重新使用 设置音色 指令")), sender, event.type)
                except:
                    await SendMessage(app, MessageChain(Plain("错误的选择,请重新使用 设置音色 指令")), sender, event.type)
                continue
            
            if(event.type == 'GroupMessage'):
                content = await bot.contact(str(ret_msg), 2, sender.id, sender.name, sender.group.id, sender.group.name)
            else:
                content = await bot.contact(str(ret_msg), 1, sender.id, sender.nickname)
                
            content.replace('BetaGo','我')
                
            jp_content = tencent_translater.translate(content)
            voice_path = await moegoe.text_to_voice(jp_content, voice_type)
            if voice_path == None:
                await SendMessage(app, MessageChain('错误的文本输入'), sender, event.type)
            else:
                await SendMessage(app, MessageChain(Voice(data_bytes=await silkcoder.async_encode(voice_path, rate=48000, codec = 1))), sender, event.type, no_group_mention=1)
                if with_text:
                    await SendMessage(app, MessageChain(content), sender, event.type)
                os.remove(voice_path)
            
            