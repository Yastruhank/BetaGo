import sys
import os

from graia.ariadne.app import Ariadne
from graia.ariadne.console import Console
from graia.ariadne.console.saya import ConsoleSchema
from graia.ariadne.message.parser.twilight import Twilight,MatchResult, ParamMatch
from graia.saya import Channel
from prompt_toolkit.styles import Style
from loguru import logger

channel = Channel.current()

@channel.use(ConsoleSchema([Twilight.from_command("stop")]))
async def stop(app: Ariadne, console: Console):
    res: str = await console.prompt(
        l_prompt=[("class:warn", " 你确定要退出吗? "), ("", " (y/n) ")],
        style=Style([("warn", "bg:#cccccc fg:#d00000")]),
    )
    if res.lower() in ("y", "yes"):
        await app.stop()
        console.stop()
        
@channel.use(ConsoleSchema([Twilight.from_command("restart")]))
async def stop(app: Ariadne, console: Console):
    res: str = await console.prompt(
        l_prompt=[("class:warn", " 你确定要重启吗? "), ("", " (y/n) ")],
        style=Style([("warn", "bg:#cccccc fg:#d00000")]),
    )
    if res.lower() in ("y", "yes"):
        p = sys.executable
        os.execl(p, p, *sys.argv)
        console.stop()
        sys.exit()
        await app.stop()
        
@channel.use(ConsoleSchema([Twilight.from_command("clear")]))
async def stop(app: Ariadne, console: Console):
    os.system('clear')
        
        
@channel.use(ConsoleSchema([Twilight.from_command("send {type} {id} {message}")]))
async def console_chat(app: Ariadne,type: MatchResult, id: MatchResult, message: MatchResult):
    event_type = type.result.display
    if(event_type == "group"):
        group_id = id.result.display
        await app.send_group_message(int(group_id), message.result)
    elif(event_type == "friend"):
        friend_id = id.result.display
        await app.send_friend_message(int(friend_id), message.result)
    else:
        logger.error("错误的消息类型 {" + event_type + "}\n\t类型应为 {friend} {group} 或 {temp}\n\t当类型为{temp}时需额外指定{group_id}")

@channel.use(ConsoleSchema([Twilight.from_command("send temp {id} {group} {message}")]))
async def console_chat(app: Ariadne,id: MatchResult, group_id: MatchResult, message: MatchResult):
    await app.send_temp_message(target=int(id), group=int(group_id),message=message.result)

@channel.use(ConsoleSchema([Twilight.from_command("reload {module_name}")]))
async def console_chat(app: Ariadne,module_name: MatchResult):
    name = module_name.result.display
    from core.load_param import saya,channel_list
    if(not name in channel_list):
        logger.error("错误的module名称 {" + name + "}")
        return
    try:
        saya.reload_channel(channel_list[name])
    except Exception as e:
        del channel_list[name]
        logger.error('重载module {' + str(name) + '}失败,错误信息为\n' + str(e))
    logger.info('重载module {' + str(name) + '} 完成')
    
@channel.use(ConsoleSchema([Twilight.from_command("load {module_name}")]))
async def console_chat(app: Ariadne,module_name: MatchResult):
    name = module_name.result.display
    from core.load_param import saya,channel_list
    if(name in channel_list):
        logger.error("错误:module {" + name + "} 已被加载")
        return
    channel_list[name] = saya.require(name)
    logger.info('加载module {' + str(name) + '} 完成')

@channel.use(ConsoleSchema([Twilight.from_command("remove {module_name}")]))
async def console_chat(app: Ariadne,module_name: MatchResult):
    name = module_name.result.display
    from core.load_param import saya,channel_list
    if(not name in channel_list):
        logger.error("错误的module名称 {" + name + "}")
        return
    try:
        saya.uninstall_channel(channel_list[name])
    except Exception as e:
        logger.error('卸载module {' + str(name) + '}失败,错误信息为\n' + str(e))
    del channel_list[name]
    logger.info('卸载module {' + str(name) + '} 完成')

@channel.use(ConsoleSchema([Twilight.from_command("list")]))
async def console_chat(app: Ariadne):
    output = '已加载以下module:\n'
    from core.load_param import channel_list
    for key in channel_list:
        output = output + '\t{' + key + '}' + '\n'
    logger.info(output.strip())

@channel.use(ConsoleSchema([Twilight.from_command("help")]))
async def console_chat(app: Ariadne):
    output = '包含以下指令:\n'
    output = output + ' > load {module_name}\t\t\t\t\t加载指定module' + '\n'
    output = output + ' > reload {module_name}\t\t\t\t\t重新加载指定module' + '\n'
    output = output + ' > remove {module_name}\t\t\t\t\t卸载指定module' + '\n'
    output = output + ' > list\t\t\t\t\t\t\t列出所有加载的module' + '\n'
    output = output + ' > send {type} {id} ({group_id}) {message}\t\t向好友或群或者群中陌生人发送对话' + '\n'
    output = output + ' > clear\t\t\t\t\t\t清屏' + '\n'
    output = output + ' > restart\t\t\t\t\t\t重启程序' + '\n'
    output = output + ' > stop\t\t\t\t\t\t\t停止程序' + '\n'
    logger.info(output.strip())
