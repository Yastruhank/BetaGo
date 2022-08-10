from dialogbot import Bot
from loguru import logger

class DialogBot:
    def __init__(self, gpt_model_dir):
        logger.info('Loading gpt model in chat module ... ')
        self.bot = Bot(gpt_model_dir='./modules/chat/module/')
        logger.info('Gpt model loaded.')
    
    async def contact(self, input_str, type, id, name, group=0, group_name=''):
        reply = self.bot.answer(input_str, use_gen=True,use_search=False)
        return reply.get('gen_response')

dialogbot = DialogBot(gpt_model_dir='./modules/chat/module/')