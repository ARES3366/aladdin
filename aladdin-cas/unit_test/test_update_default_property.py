import os.path
import unittest
import json
import time
from privacy_information_identity.identify_privacy_information import identity
from privacy_information_identity.update_default import update_default_property,update,load


_get_module_path = lambda path: os.path.normpath(os.path.join(os.getcwd(),
                                                 os.path.dirname(__file__), path))

class TestIdentify(unittest.TestCase):

    '''
    测试修改default.json
    '''
    def test_update_default(self):
        defaule_classes = {}
        defaule_classes["cn_id"] = "true"
        defaule_classes["cn_bank"] = "true"
        defaule_classes["cn_email"] = "true"
        defaule_classes["cn_date"] = "false"
        defaule_classes["cn_telephone"] = "true"
        defaule_classes["cn_passport"] = "false"
    
        param={}
        param['recognize_class']='default'
        param['update_propertiy']=defaule_classes
        param['rate_grade']="高"

        list_class=update_default_property(param)
        print(list_class)
        time.sleep(2)
        
        defaule_classes = {}
        defaule_classes["cn_id"] = "true"
        defaule_classes["cn_bank"] = "true"
        defaule_classes["cn_email"] = "true"
        defaule_classes["cn_date"] = "true"
        defaule_classes["cn_telephone"] = "true"
        defaule_classes["cn_passport"] = "true"
        param={}
        param['recognize_class']='update'
        param['update_propertiy']=defaule_classes
        param['rate_grade']="高"        
        list_class2=update_default_property(param)
        print(list_class2)


        defaule_classes = {}
        defaule_classes["cn_id"] = "true"
        defaule_classes["cn_bank"] = "true"
        defaule_classes["cn_email"] = "true"
        defaule_classes["cn_date"] = "true"
        defaule_classes["cn_telephone"] = "true"
        defaule_classes["cn_passport"] = "true"
        param={}
        param['recognize_class']='check'
        param['update_propertiy']=defaule_classes
        param['rate_grade']="高"
        list_class3=update_default_property(param)
        print(list_class3)

        num = 900
        update(defaule_classes,num,"高")
        after_update =load()
        self.assertEqual(6,len(after_update))





if __name__ == "__main__":
    unittest.main()

