#!/usr/bin/env python
# -*- coding: utf-8 -*-
from fta.fast_text_analysis import content2wordlist,wordlist2keywords,wordlist2abstract,keyword2keyphrase,keywords2fingerprint,wordlist2commonclass

def fastTextAnalysis(params):
    content=params['content']
    action=params['action']
    data={}
    cut_result=content2wordlist(content)
    def get_kwds(keywords,sentence_phrase_list):
        top_num = action['keywords']['top_num']
        top_keywords = [i[0] for i in keywords[:top_num]]
        keyphrase = action['keywords']['keyphrase']
        if keyphrase:
            top_keywords=keyword2keyphrase(sentence_phrase_list,top_keywords)
        return top_keywords
    if "fingerprint" in action.keys() and action["fingerprint"] :
        keywords,sentence_phrase_list=wordlist2keywords(cut_result['wordlist'])
        fp=keywords2fingerprint(keywords[:30])
        data['fingerprint']=fp
        if 'keywords' in action.keys():
            data['keywords']=get_kwds(keywords,sentence_phrase_list)
    if 'keywords' in action.keys() and 'keywords' not in data.keys() :
        keywords,sentence_phrase_list=wordlist2keywords(cut_result['wordlist'])
        data['keywords']=get_kwds(keywords,sentence_phrase_list)
    if "abstract" in action.keys() and action["abstract"]:
        abstract=wordlist2abstract(cut_result)
        data['abstract']=abstract
    if "common_class" in action.keys() and action["common_class"] :
        common_class=wordlist2commonclass(cut_result['wordlist'])
        data['common_class']=common_class

    return data
def fta_keywords(params):
    content=params['content']
    cut_result=content2wordlist(content)
    keywords,sentence_phrase_list=wordlist2keywords(cut_result['wordlist'])
    return keywords[:30]








