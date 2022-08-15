from dialogbot import Bot
from loguru import logger

class DialogBot:
    def __init__(self, gpt_model_dir):
        logger.info('Loading gpt model in chat module ... ')
        try:
            self.bot = Bot(gpt_model_dir='./modules/chat/module/')
            logger.info('Gpt model loaded.')
            self.init_done = True
        except:
            self.init_done = False
            logger.warning('Gpt model was not loaded.')
        
    
    async def contact(self, input_str, type, id, name, group=0, group_name=''):
        if not self.init_done:
            logger.error('Gpt model was not loaded.')
        reply = self.bot.answer(input_str, use_gen=True,use_search=False)
        return reply.get('gen_response')

dialogbot = DialogBot(gpt_model_dir='./modules/chat/module/')