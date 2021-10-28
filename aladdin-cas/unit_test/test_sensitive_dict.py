#!/usr/bin/env python
# -*- coding: utf-8 -*-
import sys,os,time
import unittest
from analysis_package.sensitive_dict import SensitiveDict

class TestAnalysisContent(unittest.TestCase):
    def test_sensitive_dict(self):
        sd = SensitiveDict()
        self.assertFalse(sd.has_sensitive_word('你好'))
        self.assertTrue(sd.has_sensitive_word('文化大革命'))
        self.assertTrue(sd.has_sensitive_word('胡锦涛'))
        
