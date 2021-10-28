from zhtools.langconv import *
import os,sys
import time
import unittest

class TestZhtools(unittest.TestCase):

    def test_chs2cht(self):
        s_cht = '把中文字符串進行繁體和簡體中文的轉換'
        s_chs = '把中文字符串进行繁体和简体中文的转换'
        s = Converter('zh-hant').convert(s_chs)
        self.assertEqual(s, s_cht)

    def test_cht2chs(self):
        s_cht = '把中文字符串進行繁體和簡體中文的轉換'
        s_chs = '把中文字符串进行繁体和简体中文的转换'
        s = Converter('zh-hans').convert(s_cht)
        self.assertEqual(s, s_chs)

    #每秒转换50K字，速度极慢。
    def test_cht2chs_speed(self):
        s_cht = '把中文字符串進行繁體和簡體中文的轉換'*(2**10)*10
        s_chs = '把中文字符串进行繁体和简体中文的转换'*(2**10)*10
        t0 = time.time()
        s = Converter('zh-hans').convert(s_cht)
        t1=time.time()
        print('=====cht2chs,  s_cht.length=%s  use_time=%s'%(len(s_cht), t1-t0))
        self.assertEqual(s, s_chs)
