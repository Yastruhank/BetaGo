import asyncio
import random
from graia.ariadne.app import Ariadne
from graia.ariadne.event.message import GroupMessage, MessageEvent, FriendMessage, TempMessage, StrangerMessage
from graia.ariadne.message.element import Plain, At, AtAll, Face, Image
from graia.ariadne.message.chain import MessageChain, Source
from graia.ariadne.model import Group, MiraiSession, Stranger, Friend, Member, Client, Union, MemberPerm
import time
import re
import heapq
import requests
from NEU import NeuStu
import pickle
from Molly import Molly
import json
import numpy as np
from graia.scheduler import GraiaScheduler, timers
import tools
from sql import SQL
from graia.ariadne.message.parser.base import DetectPrefix, MentionMe, Mention
from setu import setu
from webvpn import WebVPN

config_json = {}
with open("./config.json", "r") as config_file:
    config_json = json.load(config_file)

app = Ariadne(
    MiraiSession(
        host=config_json['mirai_host'],
        verify_key=config_json['mirai_verify_key'],
        account=config_json['bot_account'],
    ),
    use_bypass_listener=True,
)
bcc = app.broadcast

sche = app.create(GraiaScheduler)

sql = SQL(config_json['sql_host'], config_json['sql_port'],
          config_json['sql_database_name'], config_json['sql_database_user'], config_json['sql_database_passwd'])
setu_bot = setu()
webvpn = WebVPN()
molly_bot = Molly(config_json['Molly_Api-Key'], config_json['Molly_Api-Secret'])

if(config_json['first_run']):
    param = ("id char(20) primary key",
             "eone_id char(9)", "eone_passwd char(20)")
    sql.create("eone_neu",param)
    param = ("id char(20) primary key","tag int")
    sql.create("jkdk_subscribe", param)
    config_json['first_run'] = False
    with open("./config.json", "w") as config_file:
        config_json = json.dump(config_file)

async def send_message(app: Ariadne, message: MessageChain, id: Union[Friend, Member, Client, Stranger], type: str, source: Source = None):
    if(type != 'GroupMessage'):
        await app.sendMessage(id, MessageChain.create(message))
    else:
        if(source == None):
            await app.sendMessage(id.group, MessageChain.create(At(id.id), "\n", message))
        else:
            await app.sendMessage(id.group, message, quote=source)


@bcc.receiver(GroupMessage)
async def food(app: Ariadne, group: Group, message: MessageChain = DetectPrefix("谁带饭")):
    members = message[At]
    if(len(members) == 0):
        await app.sendMessage(group, MessageChain.create("错误的指令格式\n应输入 谁带饭 [@第一个候选带饭候选人] [@第二个候选带饭候选人]..."))
    random.seed(time.time())
    num = len(members)
    target = np.random.randint(0, num-1, 1)[0]
    await app.sendMessage(group, MessageChain.create(members[target], Plain(" ，就决定由你带饭了"), Face(name = 'doge')))


@bcc.receiver(MessageEvent, decorators=[DetectPrefix("绑定")])
async def binding(app: Ariadne, event: MessageEvent, sender: Union[Friend, Member, Client, Stranger], source: Source, message: MessageChain):
    str_prefix = ''
    if(event.type == 'GroupMessage'):
        str_prefix = '[本指令可以且推荐私聊完成]\n'
    if(len(str(message)) < 16 or str(message)[2] != ' ' or str(message)[11] != ' '):
        await send_message(app, MessageChain.create(str_prefix + "错误的指令格式\n应输入 绑定 [学号] [密码]"), sender, event.type)
        return
    account = str(message)[3:12]
    password = str(message)[12:]
    sender_id = str(sender.id)
    stu = NeuStu(int(account), password)
    if(stu.init_down == False):
        await send_message(app, MessageChain.create(str_prefix + "登录失败，请检查账号或密码"), sender, event.type)
        return
    if(sql.select_one("eone_neu", "id", sender_id)):
        sql.delete_one("eone_neu", "id", sender_id)
    param = (sender_id, account, password)
    sql.insert_one("eone_neu", param)
    await send_message(app, MessageChain.create(str_prefix + "完成，你可以再次使用该指令替换绑定账号"), sender, event.type)


@bcc.receiver(MessageEvent)
async def GetBB(app: Ariadne, event: MessageEvent, sender: Union[Friend, Member, Client, Stranger], source: Source, message: MessageChain):
    if(str(message)[0:6] != '查询BB作业' and str(message)[0:6] != '查询bb作业'):
        return
    find_key = ''
    if(len(str(message)) > 6):
        find_key = str(message)[6:].strip()
    sender_id = str(sender.id)
    data = sql.select_one("eone_neu", "id", sender_id)
    if(not data):
        await send_message(app, MessageChain.create("你还没有绑定一网通账号，请使用 绑定 指令完成一网通账号绑定"), sender, event.type)
        return
    account = data[0]['eone_id']
    password = data[0]['eone_passwd']
    stu = NeuStu(int(account), password)
    if(stu.init_down == False):
        await send_message(app, MessageChain.create("登录BB平台失败，请检查你的账号密码并重新绑定"), sender, event.type)
        return
    await send_message(app, MessageChain.create("正在查询BB作业，该过程可能需要一些时间，请稍后..."), sender, event.type)
    stu.sign_bb()
    results = stu.getBBResult()
    output_str = ""
    heap = []
    for key1 in results:
        if(key1 == '课程名：'):
            continue
        for key2 in results[key1]:
            time_value = 0x7fffffff
            cnt_str = key1 + "\n" + key2 + \
                "\n" + results[key1][key2] + "\n\n"
            if(len(find_key) > 0):
                if(re.search(find_key, cnt_str) == None):
                    continue
            target = re.search('截止日期', results[key1][key2])
            if(target != None):
                time_value = 0
                start_id = target.span()[0]
                year = 0
                month = 0
                day = 0
                status = 0
                for i in results[key1][key2][start_id + 4:start_id + 15]:
                    if(i >= '0' and i <= '9'):
                        if(status == 0):
                            year = year * 10 + int(i)
                        if(status == 1):
                            month = month * 10 + int(i)
                        if(status == 2):
                            day = day * 10 + int(i)
                    if(i == '年' or i == '月' or i == '日'):
                        status += 1
                    time_value = year * 10000 + month * 100 + day
            heapq.heappush(heap, (time_value, cnt_str))
    while(len(heap) > 0):
        output_str += heap[0][1]
        heapq.heappop(heap)
    if(len(output_str) == 0):
        output = MessageChain.create("没有找到相应的BB作业")
    output = MessageChain.create(Plain(output_str))
    await send_message(app, output, sender, event.type)


@bcc.receiver(MessageEvent)
async def jkdk(app: Ariadne, event: MessageEvent, sender: Union[Friend, Member, Client, Stranger], source: Source, message: MessageChain):
    if(str(message)[0:4] != "健康打卡" and str(message)[0:4] != "健康上报"):
        return
    param = ''
    if(len(str(message))>4):
        param = str(message)[4:].strip()
    sender_id = str(sender.id)
    data = sql.select_one("eone_neu", "id", sender_id)
    if(not data):
        await send_message(app, MessageChain.create("你还没有绑定一网通账号，请使用 绑定 指令完成一网通账号绑定"), sender, event.type)
        return
    account = data[0]['eone_id']
    password = data[0]['eone_passwd']
    stu = NeuStu(int(account), password)
    if(stu.init_down == False):
        await send_message(app, MessageChain.create("登录一网通办失败，请检查你的账号密码并重新绑定"), sender, event.type)
        return
    ret = stu.sign_jkdk()
    if(not ret):
        await send_message(app, MessageChain.create("发生未知错误"), sender, event.type)
        return
    await send_message(app, MessageChain.create("健康打卡成功"), sender, event.type)
    if('早' in param):
        stu.sign_jkdk_detail(1)
        await send_message(app, MessageChain.create("早上健康打卡成功"), sender, event.type)
    if('中' in param):
        stu.sign_jkdk_detail(2)
        await send_message(app, MessageChain.create("中午健康打卡成功"), sender, event.type)
    if('晚' in param):
        stu.sign_jkdk_detail(3)
        await send_message(app, MessageChain.create("晚上健康打卡成功"), sender, event.type)
    


@bcc.receiver(MessageEvent, decorators=[MentionMe()])
async def contact_bot(app: Ariadne, event: MessageEvent, sender: Union[Friend, Member, Client, Stranger], source: Source, message: MessageChain):
    if(event.type == 'GroupMessage'):
        reply = molly_bot.contact(str(
            message[Plain][0]), 2, sender.id, sender.name, sender.group.id, sender.group.name)
    else:
        reply = molly_bot.contact(
            str(message[Plain][0]), 1, sender.id, sender.nickname)
    content = json.loads(reply.text).get('data')[0].get('content')
    await send_message(app, MessageChain.create(Plain(content)), sender, event.type)


@bcc.receiver(MessageEvent)
async def getup(app: Ariadne, event: MessageEvent, sender: Union[Friend, Member, Client, Stranger], source: Source, message: MessageChain):
    param = ''
    if(str(message)[0:4] == '来点涩图' or str(message)[0:4] == '来点色图'):
        if(len(str(message))>4):
            param = str(message)[4:].strip()
    else:
        if(str(message)[0:3] == '搜涩图' or str(message)[0:3] == '搜色图'):
            if(len(str(message)) > 3):
                param = str(message)[3:].strip()
        else:
            return
    reply = setu_bot.contact(param)
    info = json.loads(reply.text).get('data')
    if(len(info) == 0):
        await send_message(app, MessageChain.create("抱歉，未找到结果"), sender, event.type)
        return
    else:
        await send_message(app, MessageChain.create(Plain(str(info[0]))), sender, event.type)
    img_url = json.loads(reply.text).get(
        'data')[0].get('urls').get('regular')
    proxy = config_json['proxy']
    if(config_json['proxy_open']):
        r = requests.get(img_url, proxies=proxy)
    else:
        r = requests.get(img_url)
    data = r.content
    await send_message(app, MessageChain.create(Image(data_bytes=data)), sender, event.type)


@bcc.receiver(MessageEvent)
async def GetWebVPN(app: Ariadne, event: MessageEvent, sender: Union[Friend, Member, Client, Stranger], source: Source, message: MessageChain = DetectPrefix("webvpn解析")):
    url = str(message).strip()
    if(len(url) == 0):
        await send_message(app, MessageChain.create(Plain("指令格式: webvpn解析 [协议(支持http,https,ssh,rdp,vnc,默认http)]://[需要解析的地址]:[端口,http与https可不填]/[后续地址]\n"
                                                          + "示例： webvpn解析 https://baidu.com 或 webvpn解析 vnc://192.168.1.1:3389")), sender, event.type)
        return
    encryp_url = webvpn.get_encryp_url(url)
    await send_message(app, MessageChain.create(Plain("WebVPN解析完成,地址为：\n" + encryp_url +"\nWebVPN仅供校外访问,请注意")), sender, event.type)


@bcc.receiver(MessageEvent)
async def subscribe(app: Ariadne, event: MessageEvent, sender: Union[Friend, Member, Client, Stranger], source: Source, message: MessageChain = DetectPrefix("订阅")):
    param = str(message).strip()
    if(len(param) == 0):
        await send_message(app, MessageChain.create(Plain("指令格式: 订阅 [需要订阅的功能] [其他参数]")), sender, event.type)
        return
    if(param[0:4] == '健康打卡' or param[0:4] == '健康上报'):
        data = sql.select_one("eone_neu", "id", str(sender.id))
        if(not data):
            await send_message(app, MessageChain.create(Plain("你还没有绑定一网通账号，请使用 绑定 指令完成一网通账号绑定")), sender, event.type)
            return
        account = data[0]['eone_id']
        password = data[0]['eone_passwd']
        stu = NeuStu(int(account), password)
        if(stu.init_down == False):
            await send_message(app, MessageChain.create("登录一网通办失败，请检查你的账号密码并重新绑定"), sender, event.type)
            return
        parm = param[4:].strip()
        tag = 0
        if('早' in parm):
            tag += (1 << 0)
        if('中' in parm):
            tag += (1 << 1)
        if('晚' in parm):
            tag += (1 << 2)
        data = sql.select_one("jkdk_subscribe","id",str(sender.id))
        if(not data):
            insert_parm = (str(sender.id), str(tag))
            sql.insert_one("jkdk_subscribe", insert_parm)
        else:
            sql.update_one("jkdk_subscribe", "id",
                           str(sender.id), "tag", str(tag))
        str_ = ''
        if(tag & (1 << 0)):
            str_ += '早上 '
        if(tag & (1 << 1)):
            str_ +='中午 '
        if(tag & (1 << 2)):
            str_ += '晚上 '
        await send_message(app, MessageChain.create(Plain("订阅健康打卡 " + str_ + "成功")), sender, event.type)
        return
    await send_message(app, MessageChain.create(Plain("未知的参数，指令格式: 订阅 [需要订阅的功能] [其他参数]")), sender, event.type)


@bcc.receiver(MessageEvent)
async def subscribe(app: Ariadne, event: MessageEvent, sender: Union[Friend, Member, Client, Stranger], source: Source, message: MessageChain = DetectPrefix("取消订阅")):
    param = str(message).strip()
    if(len(param) == 0):
        await send_message(app, MessageChain.create(Plain("指令格式: 取消订阅 [需要取消订阅的功能]")), sender, event.type)
        return
    if(param[0:4] == '健康打卡' or param[0:4] == '健康上报'):
        parm = param[4:].strip()
        tag = 0
        if('早' in parm):
            tag += (1 << 0)
        if('中' in parm):
            tag += (1 << 1)
        if('晚' in parm):
            tag += (1 << 2)
        data = sql.select_one("jkdk_subscribe", "id", str(sender.id))
        if(not data):
            await send_message(app, MessageChain.create(Plain("您没有订阅健康打卡")), sender, event.type)
            return
        else:
            sql.delete_one("jkdk_subscribe", "id",str(sender.id))
        await send_message(app, MessageChain.create(Plain("取消订阅健康打卡 成功")), sender, event.type)
        return
    await send_message(app, MessageChain.create(Plain("未知的参数，指令格式: 取消订阅 [需要取消订阅的功能]")), sender, event.type)


@bcc.receiver(MessageEvent)
async def menu(app: Ariadne, event: MessageEvent, sender: Union[Friend, Member, Client, Stranger], source: Source, message: MessageChain = DetectPrefix("菜单")):
    param = str(message).strip()
    await send_message(app, MessageChain.create(Plain("BetaGo 菜单\n\n" +
                                                      "->特色功能\n    查询BB[bb]作业 [可选:搜索关键词] 查询BB平台包含搜索关键词的作业,若搜索关键词为空,则返回所有作业,按照截至日期先后排序\n" +
                                                      "    健康打卡[上报] [可选:早/中/晚] [可选:早/中/晚]... 进行健康打卡，若参数包含早\中\晚,将同时进行相应的打卡\n" +
                                                      "    webvpn解析 [协议(支持http,https,ssh,rdp,vnc,默认http)]://[需要解析的地址]:[端口,http与https可不填]/[后续地址] 获得webvpn打开指定地址的链接\n" +
                                                      "    查询课表、大物实验等功能开发中\n" + 
                                                      "->  订阅功能\n    订阅 健康打卡[上报] [可选:早/中/晚]... 机器人会每天自动进行健康打卡，若参数包含早\中\晚,将同时进行对应时间段的打卡\n" +
                                                      "    取消订阅 健康打卡 取消健康打卡的订阅\n" +
                                                      "    BB作业提醒订阅,大物实验提醒订阅,青年大学习提醒等订阅开发中\n" +
                                                      "->聊天功能\n    @robot [聊天内容] : 与机器人对话(api:茉莉机器人)\n" +
                                                      "->寝室功能\n    谁带饭 [@第一个候选带饭候选人] [@第二个候选带饭候选人]... 随机产生一名带饭人选\n" +
                                                      "    核酸信息统计,青年大学习信息统计等功能开发中\n" +
                                                      "->账号管理\n    绑定 [学号] [密码] 绑定你的东北大学一网通账号,本功能建议私聊完成\n"),Face(147),
                                                      Plain("本项目采用AGPL协议开源,地址为https://github.com/Yastruhank/BetaGo,欢迎各位参与开发")), sender, event.type)


@bcc.receiver(MessageEvent)
async def hide_menu(app: Ariadne, event: MessageEvent, sender: Union[Friend, Member, Client, Stranger], source: Source, message: MessageChain = DetectPrefix("隐藏菜单")):
    if(sender.permission == MemberPerm.Member):
        await send_message(app, MessageChain.create(Plain("权限不足,隐藏菜单仅限管理员查看")), sender, event.type)
        return
    param = str(message).strip()
    await send_message(app, MessageChain.create(Plain("BetaGo 隐藏菜单\n\n" +
                                                      "->涩图功能\n    来点涩图[来点色图][搜涩图][搜色图] [可选:搜索关键词] 发送一张包含关键词的色图,若关键词为空,则发送随机色图\n" + 
                                                      "")), sender, event.type)

@sche.schedule(timers.crontabify("0 7 * * * 0"))
async def auto_jkdk_morning(app: Ariadne):
    random_time = np.random.randint(0, 1800, 1)[0]
    asyncio.sleep(random_time)
    users = sql.select_all('jkdk_subscribe')
    for i in users:
        data = sql.select_one("eone_neu", "id", i['id'])
        if(not data):
            return
        account = data[0]['eone_id']
        password = data[0]['eone_passwd']
        stu = NeuStu(int(account), password)
        if(stu.init_down == False):
            return
        tag = i['tag']
        stu.sign_jkdk()
        if(tag & (1<<0)):
            stu.sign_jkdk_detail(1)


@sche.schedule(timers.crontabify("0 12 * * * 0"))
async def auto_jkdk_noon(app: Ariadne):
    random_time = np.random.randint(0, 1800, 1)[0]
    asyncio.sleep(random_time)
    users = sql.select_all('jkdk_subscribe')
    for i in users:
        data = sql.select_one("eone_neu", "id", i['id'])
        if(not data):
            return
        account = data[0]['eone_id']
        password = data[0]['eone_passwd']
        stu = NeuStu(int(account), password)
        if(stu.init_down == False):
            return
        tag = i['tag']
        stu.sign_jkdk()
        if(tag & (1 << 1)):
            stu.sign_jkdk_detail(2)


@sche.schedule(timers.crontabify("0 19 * * * 0"))
async def auto_jkdk_evening(app: Ariadne):
    random_time = np.random.randint(0, 1800, 1)[0]
    asyncio.sleep(random_time)
    users = sql.select_all('jkdk_subscribe')
    for i in users:
        data = sql.select_one("eone_neu", "id", i['id'])
        if(not data):
            return
        account = data[0]['eone_id']
        password = data[0]['eone_passwd']
        stu = NeuStu(int(account), password)
        if(stu.init_down == False):
            return
        tag = i['tag']
        stu.sign_jkdk()
        if(tag & (1 << 2)):
            stu.sign_jkdk_detail(3)




app.launch_blocking()
