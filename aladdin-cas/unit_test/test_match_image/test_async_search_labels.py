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
from match_image.do_handler import MatchImageIndexPost, MatchImageIndexDelete
from match_image import search_labels
from match_image import utils
from PIL import Image
from unittest import mock

def SetSearchResultLabel(label_type=None):
    # ===============================================================
    # 设置被搜索到的标签
    if label_type == 1:
        label = "'`~!@#$%^&*( )-_=+,<.>/?\|\t\n"
    elif label_type == 2:
        label = "·~！@#￥%……&*（）-=——+【｛｝】：“；‘’”，。、《 》？"
    else:
        label = "Test://image/label.jpg"
    return label 

def SetSearchRequestImage(image_path=None):
    # ===============================================================
    # 设置用于搜索的图片
    if image_path:
        img = Image.open(image_path)
        img = img.convert('RGB')
        img = utils.Normal(img, 2)
        img_rgb_array = np.array(img)[:, :, :3]
    else:
        image_path = sys.path[0] + "/image000.jpg"
        img_rgb_array = SetSearchRequestImage(image_path=image_path)
    return img_rgb_array

async def CheckSearchResult(image):
    # ===============================================================
    # 检查搜索结果是否符合预期
    try:
        result = await search_labels.SearchImageLabels(image)
        ifconfi_1 = isinstance(result, list)
        ifconfi_2 = SetSearchResultLabel() in result
        ifconfi_3 = SetSearchResultLabel(1) in result
        ifconfi_4 = SetSearchResultLabel(2) in result
        if ifconfi_1 and ifconfi_2 and ifconfi_3 and ifconfi_4:
            return True
        else:
            return False
    except BaseException as err:
        return False

async def CatchESConnectError(image):
    # ===============================================================
    # 捕获ES服务连接失败的异常
    try:
        result = await search_labels.SearchImageLabels(image)
        return False
    except BaseException as err:
        ifcondi_1 = bool(err.code[:3] == "500")
        ifcondi_2 = bool(err.cause == "Failed to connect to ElasticSearch.")
        if ifcondi_1 and ifcondi_2:
            return True
        else:
            return False

async def CatchDLConnectError(image):
    # ===============================================================
    # 捕获DL服务连接失败的异常
    try:
        result = await search_labels.SearchImageLabels(image)
        return False
    except BaseException as err:
        ifcondi_1 = bool(err.code[:3] == "500")
        ifcondi_2 = bool(err.cause == "Failed to connect to DL-Inference-Serving.")
        if ifcondi_1 and ifcondi_2:
            return True
        else:
            return False

async def CatchESInitError(image):
    # ===============================================================
    # 捕获ES服务未初始化的异常
    try:
        result = await search_labels.SearchImageLabels(image)
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
        # UT测试开始，创建测试数据
        try:
            tasks = []
            cls.loop = asyncio.get_event_loop()
            image_path = sys.path[0] + "/image000.jpg"
            with open(image_path, "rb") as f:
                image = f.read()
            image = str(base64.b64encode(image), encoding="utf-8")
            for i in range(3):
                params = dict(
                    image=image,
                    label=SetSearchResultLabel(i),
                )
                tasks.append(asyncio.ensure_future(
                    MatchImageIndexPost(params)))
            cls.loop.run_until_complete(asyncio.wait(tasks))
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
                labels=[SetSearchResultLabel(i) for i in range(3)],
            )
            cls.loop.run_until_complete(MatchImageIndexDelete(params))
            time.sleep(3)
        except BaseException as err:
            print(err)
            raise(err)

    async def test_SearchImageLabels_1(self):
        # ===============================================================
        # 原图搜索，不通过特征提取器，单一指纹匹配
        image = SetSearchRequestImage()
        result = await CheckSearchResult(image)
        self.assertTrue(result)
        # ===============================================================
        # 截图搜索，通过特征提取器，进行图片匹配
        image_list = [
            sys.path[0] + "/image_sub_1.png",
            sys.path[0] + "/image_sub_2.png",
            sys.path[0] + "/image_sub_3.png",
            sys.path[0] + "/image_sub_4.png",
        ]
        result = []
        for i in image_list:
            image = SetSearchRequestImage(i)
            res = await CheckSearchResult(image)
            result.append(res)
        self.assertIn(True, result)
    
    async def test_SearchImageLabels_2(self):
        # ===============================================================
        # 搜索时ES连接错误
        image = SetSearchRequestImage()
        elasticsearch_path = mock.Mock(return_value="http://127.0.0.1:8080")
        with mock.patch('match_image.search_labels.ELASTICSEARCH_PATH', elasticsearch_path):
            result = await CatchESConnectError(image)
        self.assertTrue(result)

    async def test_SearchImageLabels_3(self):
        # ===============================================================
        # 搜索时dl连接错误
        image = SetSearchRequestImage()
        dl_inference_server_excep = mock.Mock(return_value=Exception)
        with mock.patch('match_image.search_labels.GetVisualLabels', dl_inference_server_excep):
            ahash_result = mock.Mock(return_value="error_hash_code")
            with mock.patch('match_image.search_labels.AverageHash', ahash_result):
                result = await CatchDLConnectError(image)
        self.assertTrue(result)
    
    async def test_SearchImageLabels_4(self):
        # ===============================================================
        # 搜索时ES连接正常，但未初始化
        image = SetSearchRequestImage()
        aliases = mock.Mock(return_value="error_aliases")
        with mock.patch('match_image.search_labels.ALIASES', aliases):
            result = await CatchESInitError(image)
        self.assertTrue(result)

if __name__ == "__main__":
    unittest.main()
