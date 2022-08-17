<div align="center">
<img src=".github/betago.jpg"/>

# BetaGo

QQ Robot based on Mirai and Ariadne

> 适用于大学生活的应用场景, 适配了东北大学的部分功能

<a href="https://github.com/Yastruhank/BetaGo/blob/main/LICENSE"><img alt="License" src="https://img.shields.io/badge/license-APGL--3.0-green"></a>
</div>

## 注意

**本项目尚不成熟,可能会有潜在的问题**

遇到问题欢迎提出issue或直接联系作者

也欢迎直接参与项目开发

--------

## 安装与依赖

* 依赖参见项目路径下[`requirements.txt`](requirements.txt)
若需要启用聊天功能还需要[`requirements_chat.txt`](requirements_chat.txt)
下依赖，且需要安装顺序为先安装[`requirements.txt`](requirements.txt)后安装[`requirements_chat.txt`](requirements_chat.txt)</br>
</br>

* 若需启动本地聊天模型,请自行下载模型文件并放置在modules/chat/module文件夹下,下载链接:
[百度网盘(提取码:aisq)](https://pan.baidu.com/share/init?surl=1KZ3hU2_a2MtI_StXBUKYw), 模型来自开源项目[dialogbot](https://github.com/shibing624/dialogbot),该项目采用[The Apache License 2.0](https://github.com/shibing624/dialogbot/blob/master/LICENSE)开源协议
</br>
</br>

* 若需启动语音聊天模块,请自行下载模型文件并放置在modules/voice_chat/module文件夹下,下载链接:</br>
Download [Config File](https://sjtueducn-my.sharepoint.com/:u:/g/personal/cjang_cjengh_sjtu_edu_cn/Ed7PXqaBdllAki0TPpeZorgBFdnxirbX_AYGUIiIcWAYNg?e=avxkWs)</br>
Download [Model](https://sjtueducn-my.sharepoint.com/:u:/g/personal/cjang_cjengh_sjtu_edu_cn/EXTQrTj-UJpItH3BmgIUvhgBNZk88P1tT_7GPNr4yegNyw?e=93bbpR)</br>
模型来自开源项目[MoeGoe](https://github.com/CjangCjengh/MoeGoe)</br>
对于Linux系统, 还需要额外安装libsndfile与ffmpeg, 例如在Ubuntu下, 可使用以下指令安装

```shell
sudo apt-get install libsndfile1 ffmpeg
```

--------

## 配置文件解读

| 配置名称 | 解读 |
| --- | --- |
mirai_host | mirai核心程序的地址,格式为<http://ip:端口>
mirai_verify_key | mirai_api_http插件中设置的密码
bot_account | 机器人的QQ账号
Turing_Api-Key | 图灵机器人的api(若不使用可留空)
Molly_Api-Key | 茉莉机器人的api(若不使用可留空)
Molly_Api-Secret | 茉莉机器人api的secret_key(若不使用可留空)
chat_type | 使用的聊天机器人类型,0为本地模型,1为图灵机器人,2为茉莉机器人
tentcloud_api_key | 腾讯云的api(共使用`文本翻译`与`一句话识别`两项服务)(若不使用可留空)
tentcloud_api_Secret | 腾讯云api的secret_key(若不使用可留空)
sql_host | MySQL数据库的ip地址
sql_port | MySQL数据库的端口
sql_database_name | MySQL数据库的库名称
sql_database_user | MySQL数据库的用户名
sql_database_passwd | MySQL数据库的密码
proxy_open | 是否在部分需要使用外网的功能下使用代理
proxy | 代理信息(若不使用可留空)

-------

## 协议

本项目以 [`GNU AGPL-3.0`](https://choosealicense.com/licenses/agpl-3.0/) 作为开源协议, 这意味着你需要遵守相应的规则.
