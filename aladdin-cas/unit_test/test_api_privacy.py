#!/usr/bin/env python
# -*- coding: utf-8 -*-
import json
from requests import session
import unittest
import numpy as np

content = '''

 太阳毫不留情的炙烤着银行卡号：6222044，大地和海洋，时间才电话号码进入18518886663六月，红洋市就迎来了高温。
    敖沐阳走上码头随意的打量周围邮箱：1010276502@qq.com，和他五年前离开家乡时一样，浑浊的海面上停靠着几十艘船，大多是筏子、舢板和小渔船，大船少见。
    这个小码头叫龙王渡，他在的村子名为龙头村，二者名字息息相关——相传在明清时期，曾经有龙在敖沐阳的家乡出现过。
    那条龙从深海九渊之下腾飞，在码头这里经过，留下了‘龙王渡’的名字。它后来上岸飞升，飞升前龙头所在的地方，就成了他们村子。
    敖沐阳刚在脑子里过了一遍从小听到大的传说故事，一艘挂日期：2019-5-6着舷外机的护照：E12345678，小型铁皮船靠上了码头。

'''




url = "http://127.0.0.1:9528/api/fast-text-analysis/v1/privacy-recognition"
class TestApisensitive(unittest.TestCase):
    def test_sensitive_2(self):
        '''
        参数:
		content中含有一个电话，和一个邮箱
	期望结果：
		识别出2个信息， 
        '''
        global content, url
        sess = session()
        params = {
            "content": content*10,
        }
        s_get = sess.post(url, json=params)
        json_data = json.loads(s_get.content.decode('utf8'))
        print(json_data)
        status = json_data['status']
        self.assertEqual(status, 0)
        num = json_data['num']
        #self.assertEqual(num, 4)
        message = json_data['message']
        #print(type(message))
        #for word in message:
         #   self.assertTrue(isinstance(word, str))
        #self.assertEqual(4, len(message))
        sess.close()

#tp = TestApisensitive()
#tp.test_sensitive_2()
