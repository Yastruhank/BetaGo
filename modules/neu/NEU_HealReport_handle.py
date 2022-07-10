import asyncio
import numpy as np
from tqdm import tqdm
from loguru import logger

from graia.ariadne.app import Ariadne
from graia.ariadne.event.message import GroupMessage, MessageEvent, FriendMessage, TempMessage, StrangerMessage
from graia.ariadne.message.element import Plain, At, AtAll, Face, Image
from graia.ariadne.message.chain import MessageChain, Source
from graia.ariadne.connection.config import HttpClientConfig,WebsocketClientConfig,config
from graia.ariadne.model import Group, Stranger, Friend, Member, Client, Union, MemberPerm

from graia.saya import Channel
from graia.scheduler.saya import SchedulerSchema
from graia.saya.builtins.broadcast.schema import ListenerSchema
from graia.scheduler import GraiaScheduler, timers

from modules.neu.NEU_HealReport import NEU_HealReport
from utils.tools import SendMessage

channel = Channel.current()

@channel.use(ListenerSchema(listening_events=[MessageEvent]))
async def jkdk(app: Ariadne, event: MessageEvent, sender: Union[Friend, Member, Client, Stranger], source: Source, message: MessageChain):
    from core.load_param import sql
    if(str(message)[0:4] != "健康打卡" and str(message)[0:4] != "健康上报"):
        return
    param = ''
    if(len(str(message))>4):
        param = str(message)[4:].strip()
    sender_id = str(sender.id)
    data = await sql.select_one("eone_neu", "id", sender_id)
    if(not data):
        await SendMessage(app, MessageChain("你还没有绑定一网通账号，请使用 绑定 指令完成一网通账号绑定"), sender, event.type)
        return
    account = data[0]['eone_id']
    password = data[0]['eone_passwd']
    stu = NEU_HealReport(int(account), password)
    await stu.init()
    if(stu.init_down == False):
        await SendMessage(app, MessageChain("登录一网通办失败，请检查你的账号密码并重新绑定"), sender, event.type)
        return
    ret = await stu.sign_jkdk()
    if(not ret):
        await SendMessage(app, MessageChain("发生未知错误"), sender, event.type)
        return
    await SendMessage(app, MessageChain("健康打卡成功"), sender, event.type)
    if('早' in param):
        await stu.sign_jkdk_detail(1)
        await SendMessage(app, MessageChain("早上健康打卡成功"), sender, event.type)
    if('中' in param):
        await stu.sign_jkdk_detail(2)
        await SendMessage(app, MessageChain("中午健康打卡成功"), sender, event.type)
    if('晚' in param):
        await stu.sign_jkdk_detail(3)
        await SendMessage(app, MessageChain("晚上健康打卡成功"), sender, event.type)

@channel.use(SchedulerSchema(timers.crontabify("0 7 * * * 0")))
async def auto_jkdk_morning(app: Ariadne):
    from core.load_param import sql
    random_time = np.random.randint(0, 1800, 1)[0]
    asyncio.sleep(random_time)
    users = await sql.select_all('jkdk_subscribe')
    logger.info('开始早上健康打卡')
    for i in tqdm(users):
        data = await sql.select_one("eone_neu", "id", i['id'])
        if(not data):
            return
        account = data[0]['eone_id']
        password = data[0]['eone_passwd']
        stu = NEU_HealReport(int(account), password)
        await stu.init()
        if(stu.init_down == False):
            return
        tag = i['tag']
        await stu.sign_jkdk()
        if(tag & (1<<0)):
            await stu.sign_jkdk_detail(1)

@channel.use(SchedulerSchema(timers.crontabify("0 12 * * * 0")))
async def auto_jkdk_noon(app: Ariadne):
    from core.load_param import sql
    random_time = np.random.randint(0, 1800, 1)[0]
    asyncio.sleep(random_time)
    users = await sql.select_all('jkdk_subscribe')
    logger.info('开始中午健康打卡')
    for i in tqdm(users):
        data = await sql.select_one("eone_neu", "id", i['id'])
        if(not data):
            return
        account = data[0]['eone_id']
        password = data[0]['eone_passwd']
        stu = NEU_HealReport(int(account), password)
        await stu.init()
        if(stu.init_down == False):
            return
        tag = i['tag']
        await stu.sign_jkdk()
        if(tag & (1 << 1)):
            await stu.sign_jkdk_detail(2)

@channel.use(SchedulerSchema(timers.crontabify("0 19 * * * 0")))
async def auto_jkdk_evening(app: Ariadne):
    from core.load_param import sql
    random_time = np.random.randint(0, 1800, 1)[0]
    asyncio.sleep(random_time)
    users = await sql.select_all('jkdk_subscribe')
    logger.info('开始晚上健康打卡')
    for i in tqdm(users):
        data = await sql.select_one("eone_neu", "id", i['id'])
        if(not data):
            return
        account = data[0]['eone_id']
        password = data[0]['eone_passwd']
        stu = NEU_HealReport(int(account), password)
        await stu.init()
        if(stu.init_down == False):
            return
        tag = i['tag']
        await stu.sign_jkdk()
        if(tag & (1 << 2)):
            await stu.sign_jkdk_detail(3)