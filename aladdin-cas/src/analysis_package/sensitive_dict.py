import os,math,random
from acam_dict import WordTree
from wordlist import WordList, Pattern
from utils import singleton

@singleton
class SensitiveDict():
    def __init__(self):
        work_path = os.path.dirname(os.path.dirname(__file__))
        sensitive_dict_file = os.path.abspath('%s/model/illegal.txt'%work_path)
        sensitive_word_set = set()
        with open(sensitive_dict_file, 'r', encoding='utf-8') as fp:
            for line in fp:
                word, flag, weight = line.split()
                sensitive_word_set.add(word)

        self.wt = WordTree({'#','@','$'})
        self.wt.build(list(sensitive_word_set))

    def has_sensitive_word(self, s):
        result, _ = self.wt.search_multi(s)
        return len(result) > 0

