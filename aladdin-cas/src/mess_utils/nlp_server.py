#coding=utf8
import os
import uuid
import asyncio
from client.tfs_client import BaseClient
from protos.tensorflow.core.framework import types_pb2
import numpy as np
from .fc_model import Sampler
from utils import singleton
 
@singleton
class NlpServer():
    def __init__(self):
        self.sampler = Sampler(factor=100000)
        cur_path = os.path.dirname(__file__)
        src_path = os.path.dirname(cur_path)
        model_path = os.path.abspath('%s/model'%src_path)
        self.datas = {}
        self.labels = {}
        self.datas_busy = False
        
        #从self.datas中采样
    def sample(self):
        try:
            self.datas_busy=True
            uid_list=[]
            data_list=[]
            for i in range(100):
                uid, data = self.datas.popitem()
                uid_list.append(uid)
                data_list.append( data[np.newaxis,:] )
        except:
            pass
        finally:
            self.datas_busy = False
        return uid_list, data_list

        #异步预测
    async def async_predict(self, s, factor=1):
        """
        1、将数据提交到self.dict中
        2、异步获取模型处理的结果
        """
        if factor > 1:
            factor = 1
        if factor < 0:
            factor = 0
        data  = self.sampler.str2vec(s)
        data *= factor
        tfs_client = BaseClient()
        input_data ={
            "text":{
                "data": data[np.newaxis,:],
                "dtype": types_pb2.DT_FLOAT
            }
        }
        output_list = ["probs"]
        result = await tfs_client.inference("mingan", "serving_default", input_data, output_list)
        val = result["probs"]["value"]
        return np.array(val, np.float32)
