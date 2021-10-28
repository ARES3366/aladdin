# -*- coding: utf-8 -*-
import re
import math
from privacy_information_identity import ac_search
#from pirvacy_information_identity.Util import Properties
import json
# from datetime import datetime
import os.path
import asyncio
#from tornado import gen 
_get_module_path = lambda path: os.path.normpath(os.path.join(os.getcwd(),
                                                 os.path.dirname(__file__), path))
class identity():
    message = {}
    '''
        匹配查找身份证号
    ''' 
    @staticmethod
    async def get_id_information(text, limit,rate_n):
        p = re.compile(r"[1-9]\d{5}(18|19|20)\d{2}((0[1-9])|(10|11|12))(([0-2][1-9])|10|20|30|31)\d{3}[0-9Xx]")
        dic = []
        path='dic/id.txt'
        model =identity.get_model(path)
        #prob = 0.0
        sumlen = len(text)
        if sumlen<=30000:
            identity.get_dic3(p,text,limit,dic,model)
        else:
            d=math.ceil(sumlen/30000)
            list_sentes=re.split(r'[。？?!.]+',text)
            sumnum = len(list_sentes)
            one = math.ceil(sumnum/d)
            for i in range(1,d+1):
                te = identity.get_onecontent(i,sumnum,one,list_sentes)
                identity.get_dic3(p,te,limit,dic,model)
                await asyncio.sleep(rate_n)
        return dic

    @staticmethod
    def get_dic3(p,text,limit,dic,model):
        prob = 0.0  
        for m in p.finditer(text):
            prob = 0.6
            i = m.start()
            j = m.end()
            space = [i, j] #位置信息
            if identity.check_id(m.group())==1:
                prob = 0.75
                content = identity.get_substring(i, j, text, int(limit))
                if len(model.search(content)) > 0:
                    prob = 0.9
                dateone = {'match_con': m.group(), 'pos': space, 'prob': prob}
                dic.append(dateone)
            else:
                prob = 0.0
   
    # 身份证号校验
    @staticmethod
    def check_id(ID):
        ID_check = ID[17]
        W = [7, 9, 10, 5, 8, 4, 2, 1, 6, 3, 7, 9, 10, 5, 8, 4, 2]
        #ID_num = [18, 17, 16, 15, 14, 13, 12, 11, 10, 9, 8, 7, 6, 5, 4, 3, 2]
        ID_CHECK = ['1', '0', 'X', '9', '8', '7', '6', '5', '4', '3', '2']
        ID_aXw = 0
        for i in range(len(W)):
            ID_aXw = ID_aXw + int(ID[i]) * W[i]
        ID_Check = ID_aXw % 11
        if ID_check != ID_CHECK[ID_Check]:
            return 0
        else:
            return 1
    
    #匹配查找日期
    @staticmethod
    async def get_date_information(text,limit,rate_n):
        p = re.compile( r"(((\d{4}|\d{2})年((0[1-9])|[1-9]|(10|11|12))月([1-9]|(0[1-9])|(([1-2][1-9])|10|20|30|31))日)|((\d{4}|\d{2})(\/|\-|\.|\*)((0[1-9])|[1-9]|(10|11|12))(\/|\-|\.|\*)(([1-2][1-9])|10|20|30|31|[1-9]|(0[1-9]))))")
        dic = []
        path='dic/date.txt'
        model =identity.get_model(path)
        #prob = 0.0
        sumlen = len(text)
        if sumlen<=30000:
            identity.get_dic1(p,text,limit,dic,model)
        else:
            d=math.ceil(sumlen/30000)
            list_sentes=re.split(r'[。？?!.]+',text)
            sumnum = len(list_sentes)
            one = math.ceil(sumnum/d)
            for i in range(1,d+1):
                te = identity.get_onecontent(i,sumnum,one,list_sentes)
                identity.get_dic1(p,te,limit,dic,model)
                await asyncio.sleep(rate_n)
        return  dic
   
    #匹配查找电话号码信息
    @staticmethod
    async def get_telephone_information(text,limit,rate_n):
        p = re.compile(r"(130|131|132|145|155|156|199|175|176|185|186|166|146|134|135|136|137|138|139|147|150|151|152|157|158|159|178|182|183|184|187|188|133|153|149|173|177|180|181|189)\d{8}")
        dic = []
        path='dic/telephone.txt'
        model =identity.get_model(path)
        #prob = 0.0
        sumlen = len(text)
        if sumlen<=30000:
            identity.get_dic1(p,text,limit,dic,model)
        else:
            d=math.ceil(sumlen/30000)
            list_sentes=re.split(r'[。？?!.]+',text)
            sumnum = len(list_sentes)
            one = math.ceil(sumnum/d)
            for i in range(1,d+1):
                te = identity.get_onecontent(i,sumnum,one,list_sentes)
                identity.get_dic1(p,te,limit,dic,model)
                await asyncio.sleep(rate_n)
        return  dic

    # 匹配查找银行卡号
    @staticmethod
    async def get_bank_information(text, limit,rate_n):
        p = re.compile(r"(((3|4|5|6)\d{18})|((3|4|5|6)\d{15}))")
        dic = []
        path='dic/bank.txt'
        model =identity.get_model(path)
        #prob = 0.0
        sumlen = len(text)
        if sumlen<=30000:
            identity.get_dic2(p,text,limit,dic,model)
        else:
            d=math.ceil(sumlen/30000)
            list_sentes=re.split(r'[。？?!.]+',text)
            sumnum = len(list_sentes)
            one = math.ceil(sumnum/d)
            for i in range(1,d+1):
                te = identity.get_onecontent(i,sumnum,one,list_sentes)
                identity.get_dic2(p,te,limit,dic,model)
                await asyncio.sleep(rate_n)
        return dic
    @staticmethod
    def get_dic2(p,te,limit,dic,model):
        for m in p.finditer(te):
            prob = 0.6
            i = m.start()
            j = m.end()
            space = [i, j]  # 位置信息
            if identity.luhn_check(m.group()):
                prob = 0.75
                content = identity.get_substring(i, j, te, limit)
                if len(model.search(content)) > 0:
                    prob = 0.9
                dateone = {'match_con': m.group(), 'pos': space, 'prob': prob}
                dic.append(dateone)
            else:
                prob = 0.0

    #验证银行卡号校验
    @staticmethod
    def luhn_check(num):
        # Number - List of reversed digits 
        digits = [int(x) for x in reversed(str(num))]
        check_sum = sum(digits[::2]) + sum((dig//10 + dig%10) for dig in [2*el for el in digits[1::2]])
        return check_sum%10 == 0
    
    # 匹配查找邮箱信息
    @staticmethod
    async def get_email_information(text, limit,rate_n):
        p = re.compile(r"([A-Za-z0-9_]+([-_\.]?[A-Za-z0-9_]+)@[A-Za-z0-9_]+([\.-_]?[A-Za-z0-9_]+)*(\.(com|COM|cn|CN|org|net|NET|edu|(com\.cn)|(com\.com)))+)")
        dic = []
        path='dic/email.txt'
        model =identity.get_model(path)
        #prob = 0.0
        sumlen = len(text)
        if sumlen<=30000:
            identity.get_dic1(p,text,limit,dic,model)
        else:
            d=math.ceil(sumlen/30000)
            list_sentes=re.split(r'[。？?!.]+',text)
            sumnum = len(list_sentes)
            one = math.ceil(sumnum/d)
            for i in range(1,d+1):
                te = identity.get_onecontent(i,sumnum,one,list_sentes)
                identity.get_dic1(p,te,limit,dic,model)
                await asyncio.sleep(rate_n)
        return dic
    
    #   匹配查找护照信息
    @staticmethod
    async def get_passport_information(text, limit,rate_n):
        p = re.compile(
            r"((D|E|S|P)\d{8})")
        dic = []
        path='dic/passport.txt'
        model = identity.get_model(path)
        sumlen = len(text)
        if sumlen<=30000:
            identity.get_dic1(p,text,limit,dic,model)
        else:
            d=math.ceil(sumlen/30000)
            list_sentes=re.split(r'[。？?!.]+',text)
            sumnum = len(list_sentes)
            one = math.ceil(sumnum/d)
            for i in range(1,d+1):
                te = identity.get_onecontent(i,sumnum,one,list_sentes)

                identity.get_dic1(p,te,limit,dic,model)    
                await asyncio.sleep(rate_n)
        return dic

    @staticmethod
    def get_model(path):
        with open(_get_module_path(path), 'r', encoding='utf-8') as f:
            lin = f.read().replace('\n', ',')
        model = ac_search.Trie(lin.split(','))
        f.close()
        return model

    @staticmethod
    def get_dic1(p,text,limit,dic,model):
        prob = 0.0
        for m in p.finditer(text):
            prob = 0.6
            i = m.start()
            j = m.end()
            space = [i, j]
            content = identity.get_substring(i, j, text, limit)
            if len(model.search(content)) > 0:
                prob = 0.75
            dateone = {'match_con': m.group(), 'pos': space, 'prob': prob}
            dic.append(dateone)

    @staticmethod
    def get_onecontent(i,sumnum,one,list_sentes):
        if one*i <sumnum:
            c=list_sentes[(i-1)*one:i*one]
        else:
            c=list_sentes[(i-1)*one:sumnum]
        te="。".join(c)
        return te

    @staticmethod
    def get_substring(i,j,text,limit):
        limit = int(limit)
        if i-limit >= 0 and j+limit <= len(text):
            content = text[i-limit:i] + text[j:j+limit]
        if i-limit < 0 and j+limit <= len(text):
            content = text[0:i]+text[j:j+limit]
        if i-limit < 0 and j+limit > len(text):
            content = text[0:i]+text[j:len(text)]
        if i-limit >= 0 and j+limit > len(text):
            content = text[i-limit:i] + text[j:len(text)]
        return content

    @staticmethod
    def get_rate_grade(grade):
        if grade =="高":
            return 0.001
        if grade =="中":
            return 0.005
        if grade =="低":
            return 0.01
        else:
            return 0.005

    @staticmethod
    async def get_properties(text):
        num=0
        result = {}
        message = {}
        with open(_get_module_path("property/default.json"), 'r') as load_f:
            load_dict = json.load(load_f)
        limit = load_dict['default']['limit']
        rate_grade = load_dict['default']['rate_grade']
        rate_n =identity.get_rate_grade(rate_grade)
        default_class = load_dict['default']['default_classes']
        if default_class['cn_date'] == 'true':
            num += 1
            date_mes = await identity.get_date_information(text,limit/3,rate_n)
            message["cn_date"]=date_mes       
        if default_class['cn_telephone'] == 'true':
            num += 1
            date_mes =await identity.get_telephone_information(text, limit/3,rate_n)
            message["cn_telephone"]= date_mes
        if default_class['cn_id'] == 'true':
            num += 1
            date_mes =await identity.get_id_information(text, limit/3,rate_n)
            message["cn_id"]= date_mes
        if default_class['cn_bank'] == 'true':
            num += 1
            date_mes =await identity.get_bank_information(text, limit / 3,rate_n)
            message["cn_bank"]= date_mes
        if default_class['cn_passport'] == 'true':
            num += 1
            date_mes =await identity.get_passport_information(text, limit/3,rate_n)
            message["cn_passport"]= date_mes
        if default_class['cn_email'] == 'true':
            num += 1
            date_mes =await identity.get_email_information(text, limit / 3,rate_n)
            message["cn_email"]= date_mes
        result["num"]= num
        result["message"]= message
        return result
