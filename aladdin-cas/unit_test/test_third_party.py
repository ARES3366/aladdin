#!/usr/bin/env python
# -*- coding: utf-8 -*-
import os,re,time
import unittest


class TestExtractMethod(unittest.TestCase):
    def test_seg(self):
        s = '[#@$]'
        partten = re.compile(s)
        text = '你#好@我$是@小##明'*200000
        print(len(text))
        t0 = time.time()
        text = partten.sub('',text)
        print(len(text))
        t1 = time.time()
        print('-----------use time: %s'%(t1-t0))
        

if __name__ == "__main__":
    unittest.main()
