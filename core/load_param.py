import json
import os

import pkgutil
import asyncio
from graia.ariadne.connection.config import HttpClientConfig,WebsocketClientConfig,config
from graia.ariadne.app import Ariadne
from utils.sql import SQL
from graia.saya import Saya
from graia.scheduler import GraiaScheduler
from creart import create
from graia.ariadne.console import Console
from prompt_toolkit.formatted_text import HTML
from prompt_toolkit.styles import Style
from graia.ariadne.console.saya import ConsoleBehaviour

config_json = {}
modules_list = []
with open("./config/config.json", "r") as json_file:
    config_json = json.load(json_file)
    
with open("./modules/setu/setu.json", "r") as json_file:
    setu_json = json.load(json_file)
            
for module_info in pkgutil.iter_modules(["core"]):
    json_path = f"./core/{module_info.name}/module.json"
    if not os.path.exists(json_path):
        continue
    with open(json_path, "r") as json_file:
        json_content = json.load(json_file)
        for module in json_content['module']:
            modules_list.append(module)
  
for module_info in pkgutil.iter_modules(["modules"]):
    json_path = f"./modules/{module_info.name}/module.json"
    if not os.path.exists(json_path):
        continue
    with open(json_path, "r") as json_file:
        json_content = json.load(json_file)
        for module in json_content['module']:
            modules_list.append(module)
    
Ariadne.config(inject_bypass_listener=True)
saya = create(Saya)
app = Ariadne(
    connection=config(
        config_json['bot_account'],
        config_json['mirai_verify_key'],
        HttpClientConfig(host=config_json['mirai_host']),
        WebsocketClientConfig(host=config_json['mirai_host']),
    ),
)

bcc = app.broadcast

sche = app.create(GraiaScheduler)

con = Console(
    broadcast=app.broadcast,
    prompt=HTML("<python>  </python><split_0></split_0><betago>  BetaGo </betago><split_1></split_1> "),
    style=Style(
        [
            ("python", "bg:#ffffff fg:#61afef"),
            ("split_0", "bg:#61afef fg:#ffffff"),
            ("betago", "bg:#61afef fg:#betago"),
            ("split_1", "fg:#61afef"),
        ]
    ),
    replace_logger=False,
)
saya.install_behaviours(ConsoleBehaviour(con))

sql = SQL(config_json['sql_host'], config_json['sql_port'],
          config_json['sql_database_name'], config_json['sql_database_user'], config_json['sql_database_passwd'])

if(config_json['first_run']):
    param = ("id char(20) primary key",
             "eone_id char(9)", "eone_passwd char(20)")
    loop = asyncio.get_event_loop()
    if loop.is_running():
        loop.create_task(sql.create("eone_neu",param))
    else:
        loop.run_until_complete(sql.create("eone_neu",param))
    param = ("id char(20) primary key","tag int")
    if loop.is_running():
        loop.create_task(sql.create("jkdk_subscribe",param))
    else:
        loop.run_until_complete(sql.create("jkdk_subscribe",param))
    config_json['first_run'] = False
    with open("./config.json", "w") as config_file:
        config_json = json.dump(config_file)
        
channel_list = {}