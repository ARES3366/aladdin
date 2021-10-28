#!/usr/bin/env python
# -*- coding: utf-8 -*-
import sys,os

import unittest
from wordlist import WordList, Pattern


class TestWordList(unittest.TestCase):

    def test_check_worddic(self):
        cur_dir = os.path.dirname(os.path.realpath(__file__))
        word_list = WordList("%s/test_dic"%cur_dir, Pattern(1, '\t', True))
        self.assertEqual(len(word_list), 52)

        
