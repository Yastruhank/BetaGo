import sys
import os

from torch import no_grad, LongTensor

import modules.voice_chat.MoeGoe.commons
import modules.voice_chat.MoeGoe.utils
from modules.voice_chat.MoeGoe.models import SynthesizerTrn
from modules.voice_chat.MoeGoe.text import text_to_sequence
from modules.voice_chat.MoeGoe.mel_processing import spectrogram_torch
from modules.voice_chat.MoeGoe.MoeGoe import get_text

from scipy.io.wavfile import write
from loguru import logger



class MoeGoe:
    def __init__(self, model_path, config_path):
        try:
            self.hps_ms = utils.get_hparams_from_file(config_path)
            self.net_g_ms = SynthesizerTrn(
                len(self.hps_ms.symbols),
                self.hps_ms.data.filter_length // 2 + 1,
                self.hps_ms.train.segment_size // self.hps_ms.data.hop_length,
                n_speakers=self.hps_ms.data.n_speakers,
                **self.hps_ms.model)
            _ = self.net_g_ms.eval()
            _ = utils.load_checkpoint(model_path, self.net_g_ms, None)
            
            self.index = 0
            self.init_done = True
        except:
            logger.error('Failed to load!')
            self.init_done = False
            
    async def text_to_voice(self, text, speaker_id):
        if not self.init_done:
            logger.error('TTS model was not loaded.')
            return
        try:
            stn_tst = get_text(text, self.hps_ms)
        except:
            logger.error('Invalid text!')
            return
        
        try:
            with no_grad():
                x_tst = stn_tst.unsqueeze(0)
                x_tst_lengths = LongTensor([stn_tst.size(0)])
                sid = LongTensor([speaker_id])
                audio = self.net_g_ms.infer(x_tst, x_tst_lengths, sid=sid, noise_scale=.667, noise_scale_w=0.8, length_scale=1)[0][0,0].data.cpu().float().numpy()
            while os.path.exists(str(self.index) + '.wav'):
                self.index += 1
            path_name = str(self.index) + '.wav'
            write(path_name, self.hps_ms.data.sampling_rate, audio)
            self.index += 1
            return path_name
            
        except:
            logger.error('Failed to generate!')
            return
        
    def get_speakers(self):
        ret_str = ''
        num = 0
        for id, name in enumerate(self.hps_ms.speakers):
            ret_str += str(id) + '\t' + name + '\n'
            num += 1
        return ret_str,num
        
            