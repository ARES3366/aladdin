import base64
import sys
import os, io
import json
import time
import aiounittest
import asyncio
import unittest
import aiohttp
import numpy as np
from match_image.do_handler import MatchImageIndexDelete
from match_image.search_labels import SearchImageLabels
from match_image import create_index
from match_image import utils
from PIL import Image
from unittest import mock

def SetAddLabel(label_type=None):
    # ===============================================================
    # 设置用于创建索引的标签
    if label_type == 1:
        label = "C'`~!@#$%^&*( )-_=+,<.>/?\|\t\n"
    elif label_type == 2:
        label = "C·~！@#￥%……&*（）-=——+【｛｝】：“；‘’”，。、《 》？"
    else:
        label = "CTest://image/label.jpg"
    return label 

def SetAddImage():
    # ===============================================================
    # 设置用于创建索引的图片
    image_path = sys.path[0] + "/image001.jpg"
    img = Image.open(image_path)
    img = img.convert('RGB')
    img = utils.Normal(img, 3)
    img_rgb_array = np.array(img)[:, :, :3]
    return img_rgb_array

async def CheckAddImageLabelResult(image, label):
    # ===============================================================
    # 检查索引创建结果是否符合预期
    try:
        result_1 = await SearchImageLabels(image)
        ifconfi_1 = label not in result_1
        result_2 = await create_index.AddImageLabel(image, label)
        ifconfi_2 = result_2
        for i in range(30):
            result_3 = await SearchImageLabels(image)
            if label in result_3:
                ifconfi_3 = True
                break
            else:
                ifconfi_3 = False
                time.sleep(1)
        if ifconfi_1 and ifconfi_2 and ifconfi_3:
            return True
        else:
            return False
    except BaseException as err:
        return False

async def CatchESConnectError(image, label):
    # ===============================================================
    # 捕获ES服务连接失败的异常
    try:
        result = await create_index.AddImageLabel(image, label)
        return False
    except BaseException as err:
        ifcondi_1 = bool(err.code[:3] == "500")
        ifcondi_2 = bool(err.cause == "Failed to connect to ElasticSearch.")
        if ifcondi_1 and ifcondi_2:
            return True
        else:
            return False

async def CatchDLConnectError(image, label):
    # ===============================================================
    # 捕获DL服务连接失败的异常
    try:
        result = await create_index.AddImageLabel(image, label)
        return False
    except BaseException as err:
        ifcondi_1 = bool(err.code[:3] == "500")
        ifcondi_2 = bool(err.cause == "Failed to connect to DL-Inference-Serving.")
        if ifcondi_1 and ifcondi_2:
            return True
        else:
            return False

async def CatchESInitError(image, label):
    # ===============================================================
    # 捕获ES服务未初始化的异常
    try:
        result = await create_index.AddImageLabel(image, label)
        return False
    except BaseException as err:
        ifcondi_1 = bool(err.code[:3] == "500")
        ifcondi_2 = bool(err.cause == "Service is not initialized.")
        if ifcondi_1 and ifcondi_2:
            return True
        else:
            return False


class TestSearch(aiounittest.AsyncTestCase):

    def get_event_loop(self):
        self.loop = asyncio.get_event_loop()
        return self.loop

    @classmethod
    def setUpClass(cls):
        # ===============================================================
        # UT测试开始，清空数据环境
        try:
            cls.loop = asyncio.get_event_loop()
            params = dict(
                labels=[SetAddLabel(i) for i in range(3)],
            )
            cls.loop.run_until_complete(MatchImageIndexDelete(params))
            time.sleep(10)
        except BaseException as err:
            print(err)
            raise(err)
    
    @classmethod
    def tearDownClass(cls):
        # ===============================================================
        # UT测试完成，删除测试数据
        try:
            cls.loop = asyncio.get_event_loop()
            params = dict(
                labels=[SetAddLabel(i) for i in range(3)],
            )
            cls.loop.run_until_complete(MatchImageIndexDelete(params))
            time.sleep(3)
        except BaseException as err:
            print(err)
            raise(err)

    async def test_AddImageLabel_1(self):
        # ===============================================================
        # 为一张图片首次创建索引
        image = SetAddImage()
        label = SetAddLabel(1)
        result = await CheckAddImageLabelResult(image, label)
        self.assertTrue(result)
        # ===============================================================
        # 为一张图片追加标签更新索引
        image = SetAddImage()
        label = SetAddLabel(2)
        result = await CheckAddImageLabelResult(image, label)
        self.assertTrue(result)
    
    async def test_AddImageLabel_2(self):
        # ===============================================================
        # 创建图片标签索引时ES连接错误
        image = SetAddImage()
        label = SetAddLabel()
        elasticsearch_path = mock.Mock(return_value="http://127.0.0.1:8080")
        with mock.patch('match_image.create_index.ELASTICSEARCH_PATH', elasticsearch_path):
            result = await CatchESConnectError(image, label)
        self.assertTrue(result)

    async def test_AddImageLabel_3(self):
        # ===============================================================
        # 创建图片标签索引时dl连接错误
        image = SetAddImage()
        label = SetAddLabel()
        dl_inference_server_excep = mock.Mock(return_value=Exception)
        with mock.patch('match_image.create_index.GetVisualLabels', dl_inference_server_excep):
            ahash_result = mock.Mock(return_value="error_hash_code")
            with mock.patch('match_image.create_index.AverageHash', ahash_result):
                result = await CatchDLConnectError(image, label)
        self.assertTrue(result)
    
    async def test_AddImageLabel_4(self):
        # ===============================================================
        # 创建图片标签索引时ES连接正常，但未初始化
        image = SetAddImage()
        label = SetAddLabel()
        aliases = mock.Mock(return_value="error_aliases")
        with mock.patch('match_image.create_index.ALIASES', aliases):
            result = await CatchESInitError(image, label)
        self.assertTrue(result)

if __name__ == "__main__":
    unittest.main()