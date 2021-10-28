#!/usr/bin/env python
# -*- coding: utf-8 -*-
import sys,os,time
import unittest
from analysis_package.analysis_content import match_keywords

class TestAnalysisContent(unittest.TestCase):
    def test_match_keywords(self):
        content='hello world'*1024
        word_loc=match_keywords(content,['hello', 'world'])
        self.assertTrue(isinstance(word_loc,dict))
        self.assertIn('hello',word_loc)
        self.assertIn('world',word_loc)
