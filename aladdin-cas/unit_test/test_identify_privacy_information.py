import os.path
import unittest
import aiounittest
import json
import re
from privacy_information_identity import ac_search
from privacy_information_identity.identify_privacy_information import identity
import asyncio
#import pytest
_get_module_path = lambda path: os.path.normpath(os.path.join(os.getcwd(),
                                                 os.path.dirname(__file__), path))
text="太阳毫不留情的炙烤着银行卡号：6222031001007499044，大地和海洋，时间才电话号码进入18518886663六月，红洋市就来了高温敖>沐阳走上>码头随意的打量周围邮箱：1010276502@qq.com，和他五年前离开家乡时一样，浑浊的海面上停靠着几十艘船，大多是筏子、舢板>和小渔船，大船>少见。这个小码头叫龙王渡，他在的村子名为龙头村，二者名字息息相关——相传在明清时期，曾经有龙在敖沐阳的家乡出现过。那条龙从深海九渊之下腾飞>，在码头这里经过，留下了‘龙王渡’的名字。它后来上岸飞升，飞升前龙头所在的地方，就成了他们村子。 敖沐阳刚在脑子说"
text1="太阳毫不留情的炙烤着银行卡号：6222031001007499044，大地和海洋，时间才电话号码进入18518886663六月哈哈哈哈哈哈红洋市就来了高温敖沐阳走哈哈哈哈哈哈哈哈上码头随意的打量周围邮箱：1010276502@qq.com，和他五年前离开家乡时一样，浑浊的海面上停靠着几十艘船，大多是筏子、舢板>和小渔船，大船少见。这个小码头叫龙王渡，他在的村子名为龙头村，二者名字息息相关——相传在明清时期，曾经有龙在敖沐阳的家乡出现过。342221198810055636那条龙从深海九渊之下腾飞，在码头这里经过，留下了‘龙王渡’的名字。它后来上岸飞升，飞升前龙头所在的地方，就成了他们村子。 敖沐阳刚在脑子说"
text2="1234567890zbcdefghijklmnopqrstuvwxyz"
text3="太阳毫不留情的炙烤着银行卡红洋市就迎来了高温。敖沐阳走上码头随意的打量周围邮箱和他五年前离开家乡时一样，浑浊的海面上停靠着几十艘船大多是筏子、舢板和小渔船，大船少见。这个小码头叫龙王渡，他在的村子名为龙头村，二者名字息息相关——相传在明清时期曾有龙在敖沐阳的家乡出现过那条龙从深海九渊之下腾飞在码头这里经过，留下了‘龙王渡’的名字。342221198810055636它后来上岸飞升升前龙头所在的地方，就成了他们村子。敖沐阳刚在了一遍从小听到大的传说故事，一艘挂日期：6着舷外机的护照：，小型铁皮船靠上了码头"
class TestIdentify(unittest.TestCase):

    def test_get_rate_grade(self):
        grade="高"
        ra = identity.get_rate_grade(grade)
        print("get_rate_grade(高)：",ra)
        self.assertEqual(ra,0.001)
     
        grade="中"
        ra = identity.get_rate_grade(grade)
        print("get_rate_grade(中)：",ra)
        self.assertEqual(ra,0.005)
       
          
        grade="低"
        ra = identity.get_rate_grade(grade)
        print("get_rate_grade低)：",ra)
        self.assertEqual(ra,0.01)
       
       
        grade="汉"
        ra = identity.get_rate_grade(grade)
        self.assertEqual(ra,0.005)
        print(ra)

    def test_get_dic1(self):
        global text1
        global text3
        p = re.compile(
             r"((D|E|S|P)\d{8})")
        dic = []
        path='dic/passport.txt'
        model = identity.get_model(path)
        text1 = text1
        identity.get_dic1(p,text1,300,dic,model)
        print("测试get_model,测试get_dic1:")
        print(dic)
        dic=[]
        text3=text3
        identity.get_dic1(p,text3,300,dic,model)
        print(dic)
    def test_get_substring(self):
        global text2
        text = text2
        i=6
        j=15
        limit=4
        sub_str = identity.get_substring(i,j,text,limit)
        self.assertTrue(isinstance(sub_str,str))
        print("sub_str=====",sub_str)
        i=4
        j=15
        limit=5
        print(identity.get_substring(i,j,text,limit))
        i=4
        j=33
        limit=5
        print(identity.get_substring(i,j,text,limit))

        i=6
        j=33
        limit=5
        print(identity.get_substring(i,j,text,limit))


    def test_get_onecontent(self):
        list_sentes=['a','b','c','d','e','f','g','h','i','j','k','l']
        i=1
        sumnum=12
        one=5
        print(identity.get_onecontent(i,sumnum,one,list_sentes))
        i=3
        sumnum=12
        one=5
        print(identity.get_onecontent(i,sumnum,one,list_sentes))
    def test_luhn_check(self):
        num=6222031001007499044
        print(identity.luhn_check(num))
        num=6222031001007488888
        print(identity.luhn_check(num))
    def test_get_dic2(self):
        global text1
        global text3
        p = re.compile(r"(((3|4|5|6)\d{18})|((3|4|5|6)\d{15}))")
        dic = []
        path='dic/bank.txt'
        model =identity.get_model(path)
        te = text1
        identity.get_dic2(p,te,50,dic,model)
        print(dic)
        dic=[]
        te3 = text3
        identity.get_dic2(p,te3,50,dic,model)
        print(dic)

    def test_checkID(self):
        id_num="342221198810055636"
        result=identity.check_id(id_num)
        print("check_id : ",result)
        self.assertEqual(result,1)
        id_num="342221198810055688"
        result=identity.check_id(id_num)
        print("check_id : ",result)
        self.assertEqual(result,0)

    def test_get_dic3(self):
        global text1
        global text3
        p = re.compile(r"[1-9]\d{5}(18|19|20)\d{2}((0[1-9])|(10|11|12))(([0-2][1-9])|10|20|30|31)\d{3}[0-9Xx]")
        dic = []
        path='dic/id.txt'
        model =identity.get_model(path)
        te = text1
        identity.get_dic3(p,te,50,dic,model)
        print(dic)
        dic=[]
        te3=text3
        identity.get_dic3(p,te3,50,dic,model)
        print(dic)


class TestIdentifyAsync(aiounittest.AsyncTestCase):
    '''
    小于30k文本，测试id信息
    '''
    def get_event_loop(self):
        loop = asyncio.get_event_loop()
        return loop
        
    async def test_get_id_information1(self):
        text_id="太阳毫不留情的炙烤着银行卡红洋市就迎来了高温。敖沐阳走上码头随意的打量周围邮箱和他五年前离开家乡时一样，浑浊的海面上停靠着几十艘船大多是筏子、>舢板和>小渔船342221198810055636，大船少见。这个小码头叫龙王渡，他在的村子名为龙头村，二者名字息息相关——相传在明清时期曾有龙在敖沐阳的家乡出现过那条龙从深海>九渊之下腾飞在码头这里经过，留下了‘龙王渡’的名字。它后来上岸飞升升前龙头所在的地方，就成了他们村子。敖沐阳刚在了一遍从小听到大的传说故事，一艘挂日期：6着舷外机的护照：，小型铁皮船靠>上了码头" 
        limit = 200
        rate_n=0.005
        id_list=await identity.get_id_information(text_id,limit,rate_n)
        print("id_information:----",id_list)
        self.assertTrue(isinstance(id_list,list))
    
    '''
    大于30k文本，测试id信息
    '''
    async def test_get_id_information2(self):
        text_id="太阳毫不留情的炙烤着银行卡红洋市就迎来了高温。敖沐阳走上码头随意的打量周围邮箱和他五年前离开家乡时一样，浑浊的海面上停靠着几十艘船大多是筏>子、>舢板和>小渔船342221198810055636，大船少见。这个小码头叫龙王渡，他在的村子名为龙头村，二者名字息息相关——相传在明清时期曾有龙在敖沐阳的家乡出现过那条龙深海九渊之下腾飞在码头这里经过，留下了‘龙王渡’的名字。它后来上岸飞升升前龙头所在的地方，就成了他们村子。敖沐阳刚在了一遍从小听到大的传说故事，一艘挂日期：6着舷外机的护照：，小型铁皮船靠>上了码头"
        text_ids = text_id*600
        limit = 100
        rate_n=0.005
        id_list=await identity.get_id_information(text_ids,limit,rate_n)
        print("id_information:----",id_list)
        self.assertTrue(isinstance(id_list,list))
    '''
    小于30k，测试date信息
    '''
    async def test_get_date_information1(self):
        text_date="太阳毫不留情的炙烤着银行卡红洋市就迎来了高温。2010年10月5日敖沐阳走上码头随意的打量周围邮箱和他五年前离开家乡时一样，浑浊的海面上停靠着几十艘船大多是筏>子、>舢板和>小渔船342221198810055636，大船少见。这个小码头叫龙王渡，他在的村子名为龙头村，二者名字息息相关——相传在明清时期曾有龙在敖沐阳的家乡出现过那条龙从深海>九渊之下腾飞在码头这里经过，留下了‘龙王渡’的名字。它后来上岸飞升升前龙头所在的地方，就成了他们村子。敖沐阳刚在了一遍从小听到大的传说故事，一艘挂日期：6着舷外机的护照：，小型铁皮船靠>上了码头" 
        limit=50
        rate_n = 0.001
        date_list=await identity.get_date_information(text_date,limit,rate_n)
        print("date_information:----",date_list)
        self.assertTrue(isinstance(date_list,list))

    '''
    大于30k，测试date信息
    '''
    async def test_get_date_information2(self):
        text_date="太阳毫不留情的炙烤着银行卡红洋市就迎来了高温。2010年10月5日敖沐阳走上码头随意的打量周围邮箱和他五年前离开家乡时一样，浑浊的海面上停靠着十艘船大多是筏>子、>舢板和>小渔船342221198810055636，大船少见。这个小码头叫龙王渡，他在的村子名为龙头村，二者名字息息相关——相传在明清时期曾有龙在敖沐阳的家>乡出现过那条龙从深海>九渊之下腾飞在码头这里经过，留下了‘龙王渡’的名字。它后来上岸飞升升前龙头所在的地方，就成了他们村子。敖沐阳刚在了一遍从小听到大的传说故>事，一艘挂日期：6着舷外机的护照：，小型铁皮船靠>上了码头" *600
        limit=50
        rate_n = 0.001
        date_list=await identity.get_date_information(text_date,limit,rate_n)
        print("date_information:----",date_list)
        self.assertTrue(isinstance(date_list,list))
    
    
    '''
    小于30k，测试telephone信息
    '''
    async def test_get_telephone_information1(self):
        text_tele="太阳毫不留情的炙烤着银行卡红洋市就迎来了高温。2010年10月5日敖沐阳走上码头随意的打量周围邮箱和他五年前离开家乡时一样，浑浊的海面上停靠着几十艘船大多是筏>子、>舢板和>小渔船18516363383，大船少见。这个小码头叫龙王渡，他在的村子名为龙头村，二者名字息息相关——相传在明清时期曾有龙在敖沐阳的家>乡出现过那条龙从深海>九渊之下腾飞在码头这里经过，留下了‘龙王渡’的名字。它后来上岸飞升升前龙头所在的地方，就成了他们村子。敖沐阳刚在了一遍从小听到大的传说故>事，一艘挂日期：6着舷外机的护照：，小型铁皮船靠>上了码头" 
        limit=50
        rate_n = 0.001
        infor_list=await identity.get_telephone_information(text_tele,limit,rate_n)
        print("telephone_information1====",infor_list)
        self.assertTrue(isinstance(infor_list,list))

    '''
    大于30k，测试telephone信息
    '''
    async def test_get_telephone_information2(self):
        text_date="太阳毫不留情的炙烤着银行卡红洋市就迎来了高温。2010年10月5日敖沐阳走上码头随意的打量周围邮箱和他五年前离开家乡时一样，浑浊的海面上停靠着几十艘船大多是筏>子、>舢板和>小渔船18516363388，大船少见。这个小码头叫龙王渡，他在的村子名为龙头村，二者名字息息相关——相传在明清时期曾有龙在敖沐阳的家>乡出现过那条龙从深海>九渊之下腾飞在码头这里经过，留下了‘龙王渡’的名字。它后来上岸飞升升前龙头所在的地方，就成了他们村子。敖沐阳刚在了一遍从小听到大的传说故>事，一艘挂日期：6着舷外机的护照：，小型铁皮船靠>上了码头" *600
        limit=50
        rate_n = 0.001
        infor_list=await identity.get_telephone_information(text_date,limit,rate_n)
        print("telephone_information2====",infor_list)
        self.assertTrue(isinstance(infor_list,list))

    '''
    小于30k文本，测试bank信息
    '''
    async def test_get_bank_information1(self):
        text="太阳毫不留情的炙烤着银行卡号：6222031001007499044，大地和海洋，时间才电话号码进入18518886663六月，红洋市就来了高温敖>沐阳走上>码头随意的打量周围邮箱：1010276502@qq.com，和他五年前离开家乡时一样，浑浊的海面上停靠着几十艘船，大多是筏子、舢板>和小渔船，大船>少见。这个小码头叫龙王渡，他在的村子名为龙头村，二>者名字息息相关——相传在明清时期，曾经有龙在敖沐阳的家乡出现过。那条龙从深海九渊之下腾飞>，在码头这里经过，留下了‘龙王渡’的名字。它后来上岸飞升，飞升前龙头所>在的地方，就成了他们村子。 敖沐阳刚在脑子说"
        limit=50
        rate_n=0.005
        infor_list=await identity.get_bank_information(text,limit,rate_n)
        print("bank information ---",infor_list)
        self.assertTrue(isinstance(infor_list,list))


    '''
    大于30k文本，测试bank信息
    '''
    async def test_get_bank_information2(self):
        text="太阳毫不留情的炙烤着银行卡号：6222031001007499044，大地和海洋，时间才电话号码进入18518886663六月，红洋市就来了高温敖>沐阳走上>码头随意的打量周围邮箱：1010276502@qq.com，和他五年前离开家乡时一样，浑浊的海面上停靠着几十艘船，大多是筏子、舢板>和小渔船，大船>少见。这个小码头叫龙王渡，他在的村子名为龙头村，二>者名字息息相关——相传在明清时期，曾经有龙在敖沐阳的家乡出现过。那条龙从深海九渊之下腾飞>，在码头这里经过，留下了‘龙王渡’的名字。它后来上岸飞升，飞升前龙头所>在的地方，就成了他们村子。 敖沐阳刚在脑子说"*600
        limit=50
        rate_n=0.005
        infor_list=await identity.get_bank_information(text,limit,rate_n)
        print("bank information ---",infor_list)
        self.assertTrue(isinstance(infor_list,list))



    '''
    小于30k文本，测试email信息
    '''
    async def test_get_email_information1(self):
        text="太阳毫不留情的炙烤着银行卡号：6222031001007499044，大地和海洋，时间才电话号码进入18518886663六月，红洋市就来了高温敖>沐阳走上>码头随意的打量周围邮箱：1010276502@qq.com，和他五年前离开家乡时一样，浑浊的海面上停靠着几十艘船，大多是筏子、舢板>和小渔船，大船>少见。这个小码头叫龙王渡，他在的村子名为龙头村，二>者名字息息相关——相传在明清时期，曾经有龙在敖沐阳的家乡出现过。那条龙从深海九渊之下腾飞>，在码头这里经过，留下了‘龙王渡’的名字。它后来上岸飞升，飞升前龙头所>在的地方，就成了他们村子。 敖沐阳刚在脑子说"
        limit=50
        rate_n=0.005
        infor_list=await identity.get_email_information(text,limit,rate_n)
        print("email_information:----",infor_list)
        self.assertTrue(isinstance(infor_list,list))


    '''
    大于30k文本，测试email信息
    '''
    async def test_get_email_information2(self):
        text="太阳毫不留情的炙烤着银行卡号：6222031001007499044，大地和海洋，时间才电话号码进入18518886663六月，红洋市就来了高温敖>沐阳走上>码头随意的打量周围邮箱：1010276502@qq.com，和他五年前离开家乡时一样，浑浊的海面上停靠着几十艘船，大多是筏子、舢板>和小渔船，大船>少见。这个小码头叫龙王渡，他在的村子名为龙>头村，二>者名字息息相关——相传在明清时期，曾经有龙在敖沐阳的家乡出现过。那条龙从深海九渊之下腾飞>，在码头这里经过，留下了‘龙王渡’的名字。它后来上岸飞升，飞升前龙头所>在的地方，就成了他们村子。 敖沐阳刚在脑子说"*600
        limit=50
        rate_n=0.005
        infor_list=await identity.get_email_information(text,limit,rate_n)
        print("email_information:----",infor_list)
        self.assertTrue(isinstance(infor_list,list))



    '''
    小于30k文本，测试passport信息
    '''
    async def test_get_passport_information1(self):
        text="太阳毫不留情的炙烤着银行卡号：6222031001007499044，大地和海洋，时间才电话号码进入18518886663六月，红洋市就来了高温敖>沐阳走上>码头随意的打量周围邮箱：1010276502@qq.com，和他五年前离开家乡时一样，浑浊的海面上停靠着几十艘船，S66668888大多是筏子、舢板>和小渔船，大船>少见。这个小码头叫龙王渡，他在的村子名为龙头村，二>者名字息息相关——相传在明清时期，曾经有龙在敖沐阳的家乡出现过。那条龙从深海九渊之下腾飞>，在码头这里经过，留下了‘龙王渡’的名字。它后来上岸飞升，飞升前龙头所>在的地方，就成了他们村子。 敖沐阳刚在脑子说"
        limit=50
        rate_n=0.005
        infor_list=await identity.get_passport_information(text,limit,rate_n)
        print("passport_information:----",infor_list)
        self.assertTrue(isinstance(infor_list,list))


    '''
    大于30k文本，测试passport信息
    '''
    async def test_get_passport_information2(self):
        text="太阳毫不留情的炙烤着银行卡号：6222031001007499044，大地和海洋，时间才电话号码进入18518886663六月，红洋市就来了高温敖>沐阳走上>码头随意的打量围邮箱：1010276502@qq.com，和他五年前离开家乡时一样，E66668888浑浊的海面上停靠着几十艘船，大多是筏子、舢板>和小渔船，大船>少见。这个小码头叫龙王渡，他在的村子名为龙>头村，二>者名字息息相关——相传在明清时期，曾经有龙在敖沐阳的家乡出现过。那条龙从深海九渊之下腾飞>，在码头这里经过，留下了‘龙王渡’的名字。它后来上岸飞升，飞升前龙头所>在的地方，就成了他们村子。 敖沐阳刚在脑子说"*600
        limit=50
        rate_n=0.005
        infor_list=await identity.get_passport_information(text,limit,rate_n)
        print("passport_information:----",infor_list)
        self.assertTrue(isinstance(infor_list,list))    
   
    #@pytest.mark.asyncio 
    async def test_get_properties_information2(self):
        text="太阳毫不留情的炙烤着银行卡号：6222031001007499044，大地和海洋，时间才电话号码进入18518886663六月，红洋市就来了高温敖>沐阳走上>码头随意的打量围邮箱：1010276502@qq.com，和他五年前离开家乡时一样，E66668888浑浊的海面上停靠着几十艘船，大多是筏子、舢板>和小渔船，大船>少见。这个小码头叫龙王渡，他在的村子名为龙>头村，二>者名字息息相关——相传在明清时期，曾经有龙在敖沐阳的家乡出现过。那条龙从深海九渊之下腾飞>，在码头这里经过，留下了‘龙王渡’的名字。它后来上岸>飞升，飞升前龙头所>在的地方，就成了他们村子。 敖沐阳刚在脑子说"*600
        infor_list=await identity.get_properties(text)
        print("passport_information:----",infor_list)
        self.assertTrue(isinstance(infor_list,dict))


if __name__ == "__main__":
    unittest.main()

