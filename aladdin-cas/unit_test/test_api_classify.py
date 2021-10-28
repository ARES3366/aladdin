#!/usr/bin/env python
# -*- coding: utf-8 -*-
import os,sys
import json
from requests import session
import unittest
import numpy as np
import asyncio
from aiohttp import ClientSession
import time
import random
content = ("深蓝的天空中挂着一轮金黄的圆月，下面是海边的沙地，都种着一望无际的碧绿的西瓜。其间有一个十一二岁的少年，"
                   "项带银圈，手捏一柄钢叉，向一匹猹尽力地刺去。那猹却将身一扭，反从他的胯下逃走了。  这少年便是闰土。"
                   "我认识他时，也不过十多岁，离现在将有三十年了；那时我的父亲还在世，家景也好，我正是一个少爷。那一年，"
                   "我家是一件大祭祀的值年。这祭祀，说是三十多年才能轮到一回，所以很郑重。正月里供像，供品很多，祭器很讲究，"
                   "拜的人也很多，祭器也很要防偷去。我家只有一个忙月（我们这里给人做 工的分三种：整年给一定人家做工的叫长工；"
                   "按日给人做工的叫短工自己也种地只在过年过节以及收租时候来给一定的人家做工的称忙月），忙不过来，"
                   "他便对父亲说，可以叫他的儿子闰土来管祭器的。  我的父亲允许了；我也很高兴，因为我早听到闰土这名字，"
                   "而且知道他和我仿佛年纪，闰月生的，五行缺土，所以他的父亲叫他闰土。他是能装弶捉小鸟雀的。  "
                   "我于是日日盼望新 年，新年到，闰土也就到了。好容易到了年末，有一日，母亲告诉我，闰土来了，我便飞跑地去看。"
                   "他正在厨房里，紫色的圆脸，头戴一顶小毡帽，颈上套一个明晃晃的银项圈，这可见他的父亲十分爱他，怕他死去，"
                   "所以在神佛面前许下愿心，用圈子将他套住了。他见人很怕羞，只是不怕我，没有旁人的时候，便和我说话，"
                   "于是不到半日，我们便熟识了。    我们那时候不知道谈些什么，只记得闰土很高兴，说是上城之后，见了许多没有"
                   "见过的东西。  第二日，我便要他捕鸟。他说：“这不能。须大雪下了才好，我们沙地上，下了雪，我扫出一块空地来，"
                   "用短棒支起一个大竹匾，撒下秕谷，看鸟雀来吃时，我远远地将缚在棒上的绳子只一拉，那鸟雀就罩在竹匾下了。"
                   "什么都有：稻鸡，角鸡，鹁鸪，蓝背……”  我于是又很盼望下雪。  闰土又对我说：“现在太冷，"
                   "你夏天到我们这里来。我们日里到海边捡贝壳去，红的绿的都有，鬼见怕也有，观音手也有。晚上我和爹管西瓜去，"
                   "你也去。”  “管贼吗？”  “不是。走路的人口渴了摘一个瓜吃，我们这里是不算偷的。要管的是獾猪，刺猬，猹。"
                   "月亮地下，你听，啦啦地响了，猹在咬瓜了。你便捏了胡叉，轻轻地走去……”  我那时并不知道这所谓猹的是怎么一"
                   "件东西——便是现在也不知道——只是无端地觉得状如小狗而很凶猛。  “它不咬人吗？”  “有胡叉呢。走到了，"
                   "看见猹了，你便刺。这畜生很伶俐，倒向你奔来，反从胯下窜了 。它的皮毛是油一般的滑……”  我素不知道天下"
                   "有这许多新鲜事：海边有如许五色的贝壳；西瓜有这样危险的经历，我先前单知道它在水果店里出卖罢了。  “我们"
                   "沙地里，潮汛要来的时候，就有许多跳鱼儿只是跳，都有青蛙似的两个脚……”    啊！闰土的心里有无穷无尽的稀奇"
                   "的事，都是我往常的一朋友所不知道的。闰土在海边时，他们都和我一样，只看见院子里高墙上的四角的天空。  "
                   "可惜正月过去了，闰土须回家里去。我急得大哭，他也躲到厨房里，哭着不肯出门，但终于被他父亲带走了。"
                   "他后来还托他的父亲带给我一包贝壳和几支很好看的鸟毛，我也曾送他56一两次东西，但从此没有64再见面。  "
                   "我在朦abcde胧中，眼前又展开一片海边碧绿的沙12456地来，上面深蓝的天空中挂着一轮金黄的圆！@##月。")

url = "http://127.0.0.1:9528/api/fast-text-analysis/v1/illegality"

class TestApiClassify(unittest.TestCase):
    def test_classify_2(self):
        '''
	参数：
		content为合法内容
	请求并发数:
		1000
	结果：
		误判率要求小于1%
        '''
        global url
        dir_list = ['normal','zzfd','seqing','other']
        exp_cls_id = 0
        exp_cls_name = dir_list[exp_cls_id]
        cur_dir = os.path.dirname(os.path.realpath(__file__))
        data_dir = '%s/testdata/%s'%(cur_dir, exp_cls_name)
        classify_error_list = []
        async def task(fn):
            with open('%s/%s'%(data_dir, fn), 'r') as fp:
                params = {
                    "content": fp.read()
                }
            async with ClientSession() as sess:
                async with sess.post(url,json=params) as resp:
                    body = await resp.text()
                    json_data = json.loads(body)
                    class_id_dict = {'legal':0, 'sexy':2, 'political':1, 'other_illegal':3}
                    class_id = class_id_dict[json_data['class_name']]
                    if class_id != exp_cls_id:
                        #cmd = 'mv %s/%s %s/notnormal'%(data_dir,fn,cur_dir)
                        #os.system(cmd)
                        classify_error_list.append(dict(fn=fn, class_id=class_id))

        loop=asyncio.get_event_loop()
        tasks=[task(fn) for fn in random.sample(os.listdir(data_dir),1000)]
        loop.run_until_complete(asyncio.wait(tasks))
        self.assertTrue(len(classify_error_list) < 10)

    def test_classify_3(self):
        '''
	参数：
		content为色情内容
	请求并发数:
		1000
	结果：
		误判率要求小于10%
        '''
        global url
        dir_list = ['normal','zzfd','seqing','other']
        exp_cls_id = 2
        exp_cls_name = dir_list[exp_cls_id]
        cur_dir = os.path.dirname(os.path.realpath(__file__))
        data_dir = '%s/testdata/%s'%(cur_dir, exp_cls_name)
        classify_error_list = []
        async def task(fn):
            with open('%s/%s'%(data_dir, fn), 'r') as fp:
                params = {
                    "content": fp.read()
                }
            async with ClientSession() as sess:
                async with sess.post(url,json=params) as resp:
                    body = await resp.text()
                    json_data = json.loads(body)
                    class_id_dict = {'legal':0, 'sexy':2, 'political':1, 'other_illegal':3}
                    class_id = class_id_dict[json_data['class_name']]
                    if class_id != exp_cls_id:
                        classify_error_list.append(dict(fn=fn, class_id=class_id))

        loop=asyncio.get_event_loop()
        request_count=1000
        tasks=[task(fn) for fn in random.sample(os.listdir(data_dir),100)]
        loop.run_until_complete(asyncio.wait(tasks))
        print(len(classify_error_list))
        self.assertTrue(len(classify_error_list) < 10)

    def test_classify_4(self):
        '''
	参数：
		content为政治反动内容
	请求并发数:
		1000
	结果：
		误判率要求小于10%
        '''
        global url
        dir_list = ['normal','zzfd','seqing','other']
        exp_cls_id = 1
        exp_cls_name = dir_list[exp_cls_id]
        cur_dir = os.path.dirname(os.path.realpath(__file__))
        data_dir = '%s/testdata/%s'%(cur_dir, exp_cls_name)
        classify_error_list = []
        async def task(fn):
            with open('%s/%s'%(data_dir, fn), 'r') as fp:
                params = {
                    "content": fp.read()
                }
            async with ClientSession() as sess:
                async with sess.post(url,json=params) as resp:
                    body = await resp.text()
                    json_data = json.loads(body)
                    class_id_dict = {'legal':0, 'sexy':2, 'political':1, 'other_illegal':3}
                    class_id = class_id_dict[json_data['class_name']]
                    if class_id != exp_cls_id:
                        #cmd = 'mv %s/%s %s/notzzfd'%(data_dir,fn,cur_dir)
                        #os.system(cmd)
                        classify_error_list.append(dict(fn=fn, class_id=class_id))

        loop=asyncio.get_event_loop()
        request_count=1000
        tasks=[task(fn) for fn in random.sample(os.listdir(data_dir),100)]
        loop.run_until_complete(asyncio.wait(tasks))
        self.assertTrue(len(classify_error_list) < 10)

    def test_classify_5(self):
        '''
	参数：
		content为赌博内容
	请求并发数:
		1000
	结果：
		误判率要求小于20%
        '''
        global url
        dir_list = ['normal','zzfd','seqing','other']
        exp_cls_id = 3
        exp_cls_name = dir_list[exp_cls_id]
        cur_dir = os.path.dirname(os.path.realpath(__file__))
        data_dir = '%s/testdata/%s'%(cur_dir, exp_cls_name)
        classify_error_list = []
        async def task(fn):
            with open('%s/%s'%(data_dir, fn), 'r') as fp:
                params = {
                    "content": fp.read()
                }
            async with ClientSession() as sess:
                async with sess.post(url,json=params) as resp:
                    body = await resp.text()
                    json_data = json.loads(body)
                    class_id_dict = {'legal':0, 'sexy':2, 'political':1, 'other_illegal':3}
                    class_id = class_id_dict[json_data['class_name']]
                    if class_id != exp_cls_id:
                        classify_error_list.append(dict(fn=fn, class_id=class_id))

        loop=asyncio.get_event_loop()
        request_count=1000
        tasks=[task(fn) for fn in random.sample(os.listdir(data_dir),100)]
        loop.run_until_complete(asyncio.wait(tasks))
        self.assertTrue(len(classify_error_list) < 20)

    def test_classify_6(self):
        '''
	参数：
		content为非字符串类型: int 123456789
	结果：
		返回错误信息
        '''
        global content, content_english, content_fanti, url
        sess = session()
        params = {
            "content": 123456789
        }
        s_get = sess.post(url, json=params)
        json_data = json.loads(s_get.content.decode('utf8'))
        print(json_data)
        status = json_data['status']
        self.assertEqual(status, 1)
        self.assertIn('message', json_data)
        message = json_data['message']
        self.assertTrue(isinstance(message, str))
        sess.close()

    def test_classify_7(self):
        '''
	参数：
		content为非字符串类型: list ["非法"，"内容"]
	结果：
		返回错误信息
        '''
        global content, content_english, content_fanti, url
        sess = session()
        params = {
            "content": ["非法","内容"]
        }
        s_get = sess.post(url, json=params)
        json_data = json.loads(s_get.content.decode('utf8'))
        print(json_data)
        status = json_data['status']
        self.assertEqual(status, 1)
        self.assertIn('message', json_data)
        message = json_data['message']
        self.assertTrue(isinstance(message, str))
        sess.close()

    def test_classify_8(self):
        '''
	参数：
		content为非字符串类型: dict
	结果：
		返回错误信息
        '''
        global content, content_english, content_fanti, url
        sess = session()
        params = {
            "content": {'key':'value'}
        }
        s_get = sess.post(url, json=params)
        json_data = json.loads(s_get.content.decode('utf8'))
        print(json_data)
        status = json_data['status']
        self.assertEqual(status, 1)
        self.assertIn('message', json_data)
        message = json_data['message']
        self.assertTrue(isinstance(message, str))
        sess.close()

    def test_classify_9(self):
        '''
	参数：
		content为非字符串类型: None
	结果：
		返回错误信息
        '''
        global content, content_english, content_fanti, url
        sess = session()
        params = {
            "content": None
        }
        s_get = sess.post(url, json=params)
        json_data = json.loads(s_get.content.decode('utf8'))
        print(json_data)
        status = json_data['status']
        self.assertEqual(status, 1)
        self.assertIn('message', json_data)
        message = json_data['message']
        self.assertTrue(isinstance(message, str))
        sess.close()

    def test_classify_10(self):
        '''
	参数：
		content为英文内容
	请求并发数:
		1000
	结果：
		要求被分类为正常文本，误判率要求小于1%
        '''
        global url
        exp_cls_id = 0
        exp_cls_name = 'english'
        cur_dir = os.path.dirname(os.path.realpath(__file__))
        data_dir = '%s/testdata/%s'%(cur_dir, exp_cls_name)
        classify_error_list = []
        async def task(fn):
            with open('%s/%s'%(data_dir, fn), 'r') as fp:
                params = {
                    "content": fp.read()
                }
            async with ClientSession() as sess:
                async with sess.post(url,json=params) as resp:
                    body = await resp.text()
                    json_data = json.loads(body)
                    class_id_dict = {'legal':0, 'sexy':2, 'political':1, 'other_illegal':3}
                    class_id = class_id_dict[json_data['class_name']]
                    if class_id != exp_cls_id:
                        classify_error_list.append(dict(fn=fn, class_id=class_id))

        loop=asyncio.get_event_loop()
        tasks=[task(fn) for fn in random.sample(os.listdir(data_dir),1000)]
        loop.run_until_complete(asyncio.wait(tasks))
        print('\n---classify_error_list: ',len(classify_error_list))
        self.assertTrue(len(classify_error_list) < 10)

    def test_classify_11(self):
        '''
	参数：
		content为繁体内容
	请求并发数:
		1000
	结果：
		要求被分类为正常文本，误判率要求小于1%
        '''
        global url
        exp_cls_id = 0
        exp_cls_name = 'fanti'
        cur_dir = os.path.dirname(os.path.realpath(__file__))
        data_dir = '%s/testdata/%s'%(cur_dir, exp_cls_name)
        classify_error_list = []
        async def task(fn):
            with open('%s/%s'%(data_dir, fn), 'r') as fp:
                params = {
                    "content": fp.read()
                }
            async with ClientSession() as sess:
                async with sess.post(url,json=params) as resp:
                    body = await resp.text()
                    json_data = json.loads(body)
                    class_id_dict = {'legal':0, 'sexy':2, 'political':1, 'other_illegal':3}
                    class_id = class_id_dict[json_data['class_name']]
                    if class_id != exp_cls_id:
                        classify_error_list.append(dict(fn=fn, class_id=class_id))

        loop=asyncio.get_event_loop()
        tasks=[task(fn) for fn in random.sample(os.listdir(data_dir), 1000)]
        loop.run_until_complete(asyncio.wait(tasks))
        self.assertTrue(len(classify_error_list) < 10)
