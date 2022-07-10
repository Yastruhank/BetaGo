import pickle

import asyncio
from graia.ariadne.app import Ariadne
from graia.ariadne.event.message import GroupMessage, MessageEvent, FriendMessage, TempMessage, StrangerMessage
from graia.ariadne.message.element import Plain, At, AtAll, Face, Image
from graia.ariadne.message.chain import MessageChain, Source
from graia.ariadne.connection.config import HttpClientConfig,WebsocketClientConfig,config
from graia.ariadne.model import Group, Stranger, Friend, Member, Client, Union, MemberPerm

async def SendMessage(app: Ariadne, message: MessageChain, id: Union[Friend, Member, Client, Stranger], type: str, source: Source = None,no_group_mention: int = 0,force_quote: int = 0):
    if(type != 'GroupMessage'):
        if(force_quote):
            await app.sendMessage(id, MessageChain(message), quote=source)
        else:
            await app.sendMessage(id, MessageChain(message))
    else:
        if(no_group_mention):
            await app.sendMessage(id.group, MessageChain(message))
        elif(source == None):
            await app.sendMessage(id.group, MessageChain(At(id.id), "\n", message))
        else:
            await app.sendMessage(id.group, message, quote=source)

def addtwodimdict(thedict, key_a, key_b, val):
    if key_a in thedict:
        thedict[key_a].update({key_b: val})
    else:
        thedict.update({key_a: {key_b: val}})


def save_variable(v, filename):
    f = open(filename, 'wb')
    pickle.dump(v, f)
    f.close()
    return filename


def load_variavle(filename):
    f = open(filename, 'rb')
    r = pickle.load(f)
    f.close()
    return r
