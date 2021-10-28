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
from match_image.do_handler import MatchImageIndexPost, MatchImageSearchPost
from match_image import delete_index
from match_image import utils
from PIL import Image
from unittest import mock

def SetRemoveLabel(label_type=None):
    # ===============================================================
    # 设置用于删除索引的标签
    if label_type == 1:
        label = "D'`~!@#$%^&*( )-_=+,<.>/?\|\t\n"
    elif label_type == 2:
        label = "D·~！@#￥%……&*（）-=——+【｛｝】：“；‘’”，。、《 》？"
    else:
        label = "DTest://image/label.jpg"
    return label 

def SetRemoveImage(image_path=None):
    # ===============================================================
    # 设置用于删除索引的图片
    if image_path:
        with open(image_path, "rb") as f:
            image = f.read()
    else:
        image_path = sys.path[0] + "/image001.jpg"
        image = SetRemoveImage(image_path=image_path)
    return str(base64.b64encode(image), encoding="utf-8")

def SetDeleteData(image_path, labels):
    # ===============================================================
    # 设置用于删除索引的图片以及标签
    try:
        tasks = []
        loop = asyncio.get_event_loop()
        for i in labels:
            params = dict(
                image=SetRemoveImage(image_path),
                label=i,
            )
            tasks.append(asyncio.ensure_future(
                MatchImageIndexPost(params)))
        loop.run_until_complete(asyncio.wait(tasks))
        for i in range(30):
            params = dict(
                image=SetRemoveImage(image_path),
            )
            result = loop.run_until_complete(MatchImageSearchPost(params))
            if False not in [(x in result['labels']) for x in labels]:
                set_state = True
                break
            else:
                set_state = False
                time.sleep(1)
        if not set_state:
            raise Exception
    except:
        raise Exception

async def CheckRemoveImageLabelsResult(labels, image_path):
    # ===============================================================
    # 检查索引删除结果是否符合预期
    try:
        result_1, _ = await delete_index.RemoveImageLabels(labels)
        ifconfi_1 = result_1
        params = dict(
            image=SetRemoveImage(image_path),
        )
        for i in range(30):
            time.sleep(10)
            result_3 = await MatchImageSearchPost(params)
            if True not in [(x in result_3['labels']) for x in labels]:
                ifconfi_2 = True
                break
            else:
                ifconfi_2 = False
        if ifconfi_1 and ifconfi_2:
            return True
        else:
            return False
    except BaseException as err:
        return False

async def CatchESConnectError(labels):
    # ===============================================================
    # 捕获ES服务连接失败的异常
    try:
        result = await delete_index.RemoveImageLabels(labels)
        return False
    except BaseException as err:
        ifcondi_1 = bool(err.code[:3] == "500")
        ifcondi_2 = bool(err.cause == "Failed to connect to ElasticSearch.")
        if ifcondi_1 and ifcondi_2:
            return True
        else:
            return False

async def CatchESInitError(labels):
    # ===============================================================
    # 捕获ES服务未初始化的异常
    try:
        result = await delete_index.RemoveImageLabels(labels)
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
        # UT测试开始，创建待删除的数据
        try:
            image_path = sys.path[0] + "/image000.jpg"
            labels = [SetRemoveLabel(i) for i in range(3)]
            SetDeleteData(image_path, labels)
            image_path = sys.path[0] + "/image001.jpg"
            labels = [SetRemoveLabel(i) for i in range(3)]
            SetDeleteData(image_path, labels)
        except BaseException as err:
            print(err)
            raise(err)
    
    @classmethod
    def tearDownClass(cls):
        pass

    async def test_RemoveImageLabels_1(self):
        # ===============================================================
        # 不删除标签
        labels = []
        image_path = sys.path[0] + "/image001.jpg"
        result = await CheckRemoveImageLabelsResult(labels, image_path)
        self.assertTrue(result)
        # ===============================================================
        # 成功删除部分标签
        labels = [SetRemoveLabel(1), SetRemoveLabel(2)]
        image_path = sys.path[0] + "/image001.jpg"
        result = await CheckRemoveImageLabelsResult(labels, image_path)
        self.assertTrue(result)
        # ===============================================================
        # 成功删除所有标签
        labels = [SetRemoveLabel(i) for i in range(3)]
        image_path = sys.path[0] + "/image000.jpg"
        result = await CheckRemoveImageLabelsResult(labels, image_path)
        self.assertTrue(result)
    
    async def test_RemoveImageLabels_2(self):
        # ===============================================================
        # 删除标签时ES连接错误
        labels = [SetRemoveLabel(), SetRemoveLabel(1), SetRemoveLabel(2)]
        elasticsearch_path = mock.Mock(return_value="http://127.0.0.1:8080")
        with mock.patch('match_image.delete_index.ELASTICSEARCH_PATH', elasticsearch_path):
            result = await CatchESConnectError(labels)
        self.assertTrue(result)
    
    async def test_RemoveImageLabels_3(self):
        # ===============================================================
        # 删除标签时ES连接正常，但未初始化
        labels = [SetRemoveLabel(), SetRemoveLabel(1), SetRemoveLabel(2)]
        aliases = mock.Mock(return_value="error_aliases")
        with mock.patch('match_image.delete_index.ALIASES', aliases):
            result = await CatchESInitError(labels)
        self.assertTrue(result)

if __name__ == "__main__":
    unittest.main()