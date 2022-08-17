import json
import asyncio
import time
import base64

from loguru import logger
import numpy as np
from tencentcloud.common import credential
from tencentcloud.common.profile.client_profile import ClientProfile
from tencentcloud.common.profile.http_profile import HttpProfile
from tencentcloud.common.exception.tencent_cloud_sdk_exception import TencentCloudSDKException
from tencentcloud.asr.v20190614 import asr_client, models


class TencentVoiceRecognition:
    def __init__(self, api_key, api_passwd):
        self.api_key = api_key
        self.api_passwd = api_passwd
        cred = credential.Credential(api_key, api_passwd)
        httpProfile = HttpProfile()
        httpProfile.endpoint = "asr.tencentcloudapi.com"
        clientProfile = ClientProfile()
        clientProfile.httpProfile = httpProfile
        try:
            self.client = asr_client.AsrClient(cred, "", clientProfile)
            self.init_done = True
        except:
            logger.error('Init tencent cloud client fail.')
        
            
    def recognize(self, input_voice_url, sender_id):
        if not self.init_done:
            logger.error('Tencent cloud client was not loaded correctly.')
            return
        req = models.SentenceRecognitionRequest()
        __json = {"ProjectId": 0,
                "SubServiceType": 2,
                "EngSerViceType": "16k_zh",
                "SourceType": 0,
                "VoiceFormat": "silk",
                "UsrAudioKey": str(sender_id),
                "Url": input_voice_url
                }
        req.from_json_string(json.dumps(__json))
        resp = self.client.SentenceRecognition(req)
        return json.loads(resp.to_json_string())['Result']
    
from core.load_param import config_json
tencent_voice_recognition = TencentVoiceRecognition(config_json['tentcloud_api_key'], config_json['tentcloud_api_Secret'])
