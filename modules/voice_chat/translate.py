import json
import asyncio
import time

from loguru import logger
import numpy as np
from tencentcloud.common import credential
from tencentcloud.common.profile.client_profile import ClientProfile
from tencentcloud.common.profile.http_profile import HttpProfile
from tencentcloud.common.exception.tencent_cloud_sdk_exception import TencentCloudSDKException
from tencentcloud.tmt.v20180321 import tmt_client, models

class TencentTranslater:
    def __init__(self, api_key, api_passwd):
        self.api_key = api_key
        self.api_passwd = api_passwd
        cred = credential.Credential(api_key, api_passwd)
        httpProfile = HttpProfile()
        httpProfile.endpoint = "tmt.tencentcloudapi.com"
        clientProfile = ClientProfile()
        clientProfile.httpProfile = httpProfile
        try:
            self.client = tmt_client.TmtClient(cred, "ap-beijing", clientProfile)
            self.init_done = True
        except:
            logger.error('Init tencent cloud client fail.')
        
            
    def translate(self, input_str):
        if not self.init_done:
            logger.error('Tencent cloud client was not loaded correctly.')
            return
        req = models.TextTranslateRequest()
        __json = {'Action': 'TextTranslate',
                  'Version': '2018-03-21',
                  'SourceText': input_str,
                  'Source': 'auto',
                  'Target': 'ja',
                  'ProjectId': 0,
                  'Timestamp': int(time.time()),
                  }
        req.from_json_string(json.dumps(__json))
        resp = self.client.TextTranslate(req)
        return json.loads(resp.to_json_string())['TargetText']


from core.load_param import config_json
tencent_translater = TencentTranslater(config_json['tentcloud_api_key'], config_json['tentcloud_api_Secret'])
