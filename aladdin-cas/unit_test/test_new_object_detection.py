import os
import sys
import time
import io
import asyncio
import unittest
from unittest import mock
from object_detection.search_similar_images import *
from object_detection.image_search_handler import *
import base64
import asyncio
from client.milvus_client import AioMilvus
from db_adapter.mongo_adapter import MongoDBClient
import read_config
from exception_handler import *
from object_detection.util import *
_get_module_path = lambda path: os.path.normpath(os.path.join(os.path.dirname(__file__), path))

# read_config.milvus_config = {
#     "host": "10.2.180.212",
#     "port": "32003"
# }



def process_base64_data(image_base64):
    processed_params = dict()
    image_data = base64.b64decode(image_base64)
    image = io.BytesIO(image_data)
    image = Image.open(image)
    image = image.convert("RGB")
    cols, rows = image.size
    new_image = resize_image(image, rows, cols, detection_resize_map["D1"])
    channel_last_rgb_array = np.array(image)
    channel_last_rgb_array_resize = np.array(new_image)
    processed_params['image'] = channel_last_rgb_array
    processed_params["rgb_array_channel_last"] = channel_last_rgb_array
    processed_params["rgb_array_channel_last_resize"] = channel_last_rgb_array_resize
    processed_params["rows"] = rows
    processed_params["cols"] = cols
    processed_params["flag"] = 1
    return processed_params

def prepare_search_by_url_params(image_path):
    return dict(offset=0, limit=20, url=_get_module_path(image_path))
    

def prepare_search_by_b64_params(image_path):
    with open(_get_module_path(image_path),'rb') as image:
        b64 = str(base64.b64encode(image.read()), encoding="utf-8")
    params = process_base64_data(b64)
    params["offset"] = 0
    params["limit"] = 20
    return params

# def prepare_search_by_vid_params(vid):    
#     return dict(offset=0, limit=20, vid=str(vid))


def prepare_search_by_vid_params(vid):
    return dict(offset=20, limit=20, vid=str(vid))


def prepare_insert_data(image_path):
    with open(_get_module_path(image_path),'rb') as image:
        b64 = str(base64.b64encode(image.read()), encoding="utf-8")
    return dict(url=_get_module_path(image_path), image=b64)

def prepar_check_search_params_query_params_1():
    # offset 与 limit 都缺失
    return dict()

def prepar_check_search_params_query_params_2():
    # offset 缺失
    return dict(limit="20")
def prepar_check_search_params_query_params_3():
    #limit 缺失
    return dict(offset="0")

def prepar_check_search_params_query_params_4():
    # 参数数量不对
    return dict(offset="0", limit="20", aaa="12")
def prepar_check_search_params_query_params_5():
    # 两个参数不全
    return dict(offset="0", aaa="20")

def prepar_check_search_params_query_params_6():
    # offset 格式不对1
    return dict(offset="1.3", limit="20")

def prepar_check_search_params_query_params_7():
    # offset 格式不对2
    return dict(offset="-1",limit="20")


def prepar_check_search_params_query_params_10():
    # offset 格式不对3
    return dict(offset="零", limit="20")

def prepar_check_search_params_query_params_8():
    # limit 格式不对1
    return dict(offset="0", limit="-20")

def prepar_check_search_params_query_params_9():
    # limit 格式不对2
    return dict(offset="0", limit="20.1")

def prepar_check_search_params_query_params_11():
    # limit 格式不对3
    return dict(offset="0", limit="ershi")

def prepar_check_search_params_query_params_12():
    # limit 格式不对4
    return dict(offset="0", limit="200")

def prepar_check_search_params_query_params_13():
    # 输入正确
    return dict(offset="0", limit="20")

def prepar_check_search_params_body_params_1():
    # url 
    insert_data_dir = _get_module_path(os.path.join("image_search_test_case","insert_data"))
    image_list = os.listdir(insert_data_dir)
    image_path = os.path.join(insert_data_dir, image_list[0])
    return dict(url=image_path)

def prepar_check_search_params_body_params_2():
    # vid
    search_data_dir = _get_module_path(os.path.join("image_search_test_case", "insert_data"))
    search_image_list = os.listdir(search_data_dir)
    try:
        loop = asyncio.get_event_loop()
        print("res")
        res = loop.run_until_complete(image_meta_data_get(dict(url=os.path.join(search_data_dir,search_image_list[1]))))
        
        print(res)

        vid = str(res["image_meta_data_list"][0]["vid"])  
        return dict(vid=vid)
    except Exception as e:
        print(e)
        print(e.generate_response())



def prepar_check_search_params_body_params_3():
    # image
    search_data_dir = _get_module_path(os.path.join("image_search_test_case", "search_data"))
    search_image_list = os.listdir(search_data_dir)
    search_image_path = os.path.join(search_data_dir, search_image_list[0])
    with open(search_image_path, "rb") as image:
        b64 = str(base64.b64encode(image.read()), encoding="utf-8")
    return dict(image=b64)

def prepar_check_search_params_body_params_4():
    # 未知参数
    return dict(aaa="aaaaaaaa")

def prepar_check_search_params_body_params_5():
    # 未知参数
    return dict(url="affefewfwefewf")

def prepar_check_search_params_body_params_6():
    # url 格式不正确
    
    return dict(url=1)
def prepar_check_search_params_body_params_7():
    # vid 格式不正确
    return dict(vid=None)

def prepar_check_search_params_body_params_8():
    # image 格式不正确
    return dict(image=1.1)

def prepar_check_search_params_body_params_9():
    # body param 缺失
    return dict()

def prepar_check_search_params_body_params_10():
    # image 不正确
    return dict(image="fjoewfjowqefjoweiqjfiofjieqwjfoqewjfieqwjfo")


def prepar_check_search_params_body_params_11():
    # body param 传入超过一个互斥条件
    return dict(url="fiewfjiowqjfoiwjf",vid="fewiofjowqjfoiwj")


class TestObjectDetection(unittest.TestCase):
    def setUp(self):
        # read_config.milvus_config["host"] = "127.0.0.1"
        # read_config.mongo_config["host"] = "127.0.0.1"
        # read_config.mongo_config["db"] = "object_detection"

        self.sub_milvus = AioMilvus("object_detection", asyncio.get_event_loop())
        self.face_milvus = AioMilvus("face_recognition",asyncio.get_event_loop())
        self.db_client = MongoDBClient()
        self.loop = asyncio.get_event_loop()

    def setDown(self):
        del self.sub_milvus
        del self.face_milvus
        del self.db_client
        del self.loop
   
    @classmethod
    def setUpClass(cls):
        print ("object_detection start UT")

    @classmethod
    def tearDownClass(cls):
        print ("object_detection end UT")
    
    def test_image_meta_data_post(self):
        insert_data_dir = _get_module_path(os.path.join("image_search_test_case","insert_data"))
        image_list = os.listdir(insert_data_dir)
        for image_path in image_list:

            post_data = prepare_insert_data(os.path.join(insert_data_dir, image_path))
            try:
                result = self.loop.run_until_complete(image_meta_data_post(post_data))
                print(image_path, result)
            except Exception as e:
                print(image_path, e.generate_response())


    def test_search_by_url(self):
        insert_data_dir = _get_module_path(os.path.join("image_search_test_case", "insert_data"))
        search_image_list = os.listdir(insert_data_dir)
        for search_image_path in search_image_list:
            params = prepare_search_by_url_params(os.path.join(insert_data_dir, search_image_path))
            
            print(params)
            try:
                result = self.loop.run_until_complete(search_by_url(params, self.sub_milvus, self.face_milvus, self.db_client))
                print(result)
            except InternalErrorException as e:
                print(e.generate_response())
        
        
    def test_search_by_base64(self):
        search_data_dir = _get_module_path(os.path.join("image_search_test_case", "search_data"))
        search_image_list = os.listdir(search_data_dir)
        for search_image_path in search_image_list:
            params = prepare_search_by_b64_params(os.path.join(search_data_dir, search_image_path))
            print("search: ", params)
            try:
                result = self.loop.run_until_complete(search_by_b64(params, self.sub_milvus, self.face_milvus, self.db_client)) 
                print("result: ", result)
            except InternalErrorException as e:
                print(e.generate_response())

    def test_search_by_vid(self):
        search_data_dir = _get_module_path(os.path.join("image_search_test_case", "insert_data"))
        search_image_list = os.listdir(search_data_dir)
        for search_image_path in search_image_list:
            try:
                res = self.loop.run_until_complete(image_meta_data_get(dict(url=os.path.join(search_data_dir,search_image_path))))
            except Exception as e:
                print(e.generate_response())
            if res is None:
                continue
            vid = str(res["image_meta_data_list"][0]["vid"])
            params = prepare_search_by_vid_params(vid)
            try:
                result = self.loop.run_until_complete(search_by_vid(params, self.sub_milvus, self.face_milvus, self.db_client))
                print("result: ", result)
            except Exception as e: 
                print(e.generate_response())

    def test_z_check_search_params(self):
        query_params = prepar_check_search_params_query_params_1()
        body_params = prepar_check_search_params_body_params_1()
        try:
            res = check_search_params(query_params, body_params)
        except Exception as err:
            self.assertEqual(type(err), MissingParamsException)
        # ======================================================
        query_params = prepar_check_search_params_query_params_1()
        body_params = prepar_check_search_params_body_params_2()
        try:
            res = check_search_params(query_params, body_params)
        except Exception as err:
            self.assertEqual(type(err), MissingParamsException)
            
        # ======================================================
        query_params = prepar_check_search_params_query_params_1()
        body_params = prepar_check_search_params_body_params_3()
        try:
            res = check_search_params(query_params, body_params)
        except Exception as err:
            self.assertEqual(type(err), MissingParamsException)
            
        # ======================================================
        query_params = prepar_check_search_params_query_params_1()
        body_params = prepar_check_search_params_body_params_4()
        try:
            res = check_search_params(query_params, body_params)
        except Exception as err:
            self.assertEqual(type(err), MissingParamsException)
            
        # ======================================================
        query_params = prepar_check_search_params_query_params_1()
        body_params = prepar_check_search_params_body_params_5()
        try:
            res = check_search_params(query_params, body_params)
        except Exception as err:
            self.assertEqual(type(err), MissingParamsException)
            
        # ======================================================
        query_params = prepar_check_search_params_query_params_1()
        body_params = prepar_check_search_params_body_params_6()
        try:
            res = check_search_params(query_params, body_params)
        except Exception as err:
            self.assertEqual(type(err), ParamsWrongTypeException)
            
        # ======================================================
        query_params = prepar_check_search_params_query_params_1()
        body_params = prepar_check_search_params_body_params_7()
        try:
            res = check_search_params(query_params, body_params)
        except Exception as err:
            self.assertEqual(type(err), ParamsWrongTypeException)
            
        # ======================================================
        query_params = prepar_check_search_params_query_params_1()
        body_params = prepar_check_search_params_body_params_8()
        try:
            res = check_search_params(query_params, body_params)
        except Exception as err:
            self.assertEqual(type(err), ParamsWrongTypeException)
            
        # ======================================================
        query_params = prepar_check_search_params_query_params_1()
        body_params = prepar_check_search_params_body_params_9()
        try:
            res = check_search_params(query_params, body_params)
        except Exception as err:
            self.assertEqual(type(err), MissingParamsException)
            
        # ======================================================


        query_params = prepar_check_search_params_query_params_2()
        body_params = prepar_check_search_params_body_params_1()

        res = check_search_params(query_params, body_params)

        # ======================================================
        query_params = prepar_check_search_params_query_params_2()
        body_params = prepar_check_search_params_body_params_2()

        res = check_search_params(query_params, body_params)


        # ======================================================
        query_params = prepar_check_search_params_query_params_2()
        body_params = prepar_check_search_params_body_params_3()

        res = check_search_params(query_params, body_params)

            
        # ======================================================
        query_params = prepar_check_search_params_query_params_2()
        body_params = prepar_check_search_params_body_params_4()
        try:
            res = check_search_params(query_params, body_params)
        except Exception as err:
            self.assertEqual(type(err), MissingParamsException)
            
        # ======================================================
        query_params = prepar_check_search_params_query_params_2()
        body_params = prepar_check_search_params_body_params_5()
        try:
            res = check_search_params(query_params, body_params)
        except Exception as err:
            self.assertEqual(type(err), MissingParamsException)
            
        # ======================================================
        query_params = prepar_check_search_params_query_params_2()
        body_params = prepar_check_search_params_body_params_6()
        try:
            res = check_search_params(query_params, body_params)
        except Exception as err:
            self.assertEqual(type(err), ParamsWrongTypeException)
            
        # ======================================================
        query_params = prepar_check_search_params_query_params_2()
        body_params = prepar_check_search_params_body_params_7()
        try:
            res = check_search_params(query_params, body_params)
        except Exception as err:
            self.assertEqual(type(err), ParamsWrongTypeException)
            
        # ======================================================
        query_params = prepar_check_search_params_query_params_2()
        body_params = prepar_check_search_params_body_params_8()
        try:
            res = check_search_params(query_params, body_params)
        except Exception as err:
            self.assertEqual(type(err), ParamsWrongTypeException)
            
        # ======================================================
        query_params = prepar_check_search_params_query_params_2()
        body_params = prepar_check_search_params_body_params_9()
        try:
            res = check_search_params(query_params, body_params)
        except Exception as err:
            self.assertEqual(type(err), MissingParamsException)
            
        # ======================================================
        

        query_params = prepar_check_search_params_query_params_3()
        body_params = prepar_check_search_params_body_params_1()

        res = check_search_params(query_params, body_params)

            
        # ======================================================
        query_params = prepar_check_search_params_query_params_3()
        body_params = prepar_check_search_params_body_params_2()
        res = check_search_params(query_params, body_params)
            
        # ======================================================
        query_params = prepar_check_search_params_query_params_3()
        body_params = prepar_check_search_params_body_params_3()
        res = check_search_params(query_params, body_params)
            
        # ======================================================
        query_params = prepar_check_search_params_query_params_3()
        body_params = prepar_check_search_params_body_params_4()
        try:
            res = check_search_params(query_params, body_params)
        except Exception as err:
            self.assertEqual(type(err), MissingParamsException)
            
        # ======================================================
        query_params = prepar_check_search_params_query_params_3()
        body_params = prepar_check_search_params_body_params_5()
        try:
            res = check_search_params(query_params, body_params)
        except Exception as err:
            self.assertEqual(type(err), MissingParamsException)
            
        # ======================================================
        query_params = prepar_check_search_params_query_params_3()
        body_params = prepar_check_search_params_body_params_6()
        try:
            res = check_search_params(query_params, body_params)
        except Exception as err:
            self.assertEqual(type(err), ParamsWrongTypeException)
            
        # ======================================================
        query_params = prepar_check_search_params_query_params_3()
        body_params = prepar_check_search_params_body_params_7()
        try:
            res = check_search_params(query_params, body_params)
        except Exception as err:
            self.assertEqual(type(err), ParamsWrongTypeException)
            
        # ======================================================
        query_params = prepar_check_search_params_query_params_3()
        body_params = prepar_check_search_params_body_params_8()
        try:
            res = check_search_params(query_params, body_params)
        except Exception as err:
            self.assertEqual(type(err), ParamsWrongTypeException)
            
        # ======================================================
        query_params = prepar_check_search_params_query_params_3()
        body_params = prepar_check_search_params_body_params_9()
        try:
            res = check_search_params(query_params, body_params)
        except Exception as err:
            self.assertEqual(type(err), MissingParamsException)
            
        # ======================================================


        query_params = prepar_check_search_params_query_params_4()
        body_params = prepar_check_search_params_body_params_1()
        res = check_search_params(query_params, body_params)
            
        # ======================================================
        query_params = prepar_check_search_params_query_params_4()
        body_params = prepar_check_search_params_body_params_2()
        res = check_search_params(query_params, body_params)
            
        # ======================================================
        query_params = prepar_check_search_params_query_params_4()
        body_params = prepar_check_search_params_body_params_3()
        res = check_search_params(query_params, body_params)
            
        # ======================================================
        query_params = prepar_check_search_params_query_params_4()
        body_params = prepar_check_search_params_body_params_4()
        try:
            res = check_search_params(query_params, body_params)
        except Exception as err:
            self.assertEqual(type(err), MissingParamsException)
            
        # ======================================================
        query_params = prepar_check_search_params_query_params_4()
        body_params = prepar_check_search_params_body_params_5()
        try:
            res = check_search_params(query_params, body_params)
        except Exception as err:
            self.assertEqual(type(err), MissingParamsException)
            
        # ======================================================
        query_params = prepar_check_search_params_query_params_4()
        body_params = prepar_check_search_params_body_params_6()
        try:
            res = check_search_params(query_params, body_params)
        except Exception as err:
            self.assertEqual(type(err), ParamsWrongTypeException)
            
        # ======================================================
        query_params = prepar_check_search_params_query_params_4()
        body_params = prepar_check_search_params_body_params_7()
        try:
            res = check_search_params(query_params, body_params)
        except Exception as err:
            self.assertEqual(type(err), ParamsWrongTypeException)
            
        # ======================================================
        query_params = prepar_check_search_params_query_params_4()
        body_params = prepar_check_search_params_body_params_8()
        try:
            res = check_search_params(query_params, body_params)
        except Exception as err:
            self.assertEqual(type(err), ParamsWrongTypeException)
            
        # ======================================================
        query_params = prepar_check_search_params_query_params_4()
        body_params = prepar_check_search_params_body_params_9()
        try:
            res = check_search_params(query_params, body_params)
        except Exception as err:
            self.assertEqual(type(err), MissingParamsException)
            
        # ======================================================


        query_params = prepar_check_search_params_query_params_5()
        body_params = prepar_check_search_params_body_params_1()
        res = check_search_params(query_params, body_params)
            
        # ======================================================
        query_params = prepar_check_search_params_query_params_5()
        body_params = prepar_check_search_params_body_params_2()
        res = check_search_params(query_params, body_params)
            
        # ======================================================
        query_params = prepar_check_search_params_query_params_5()
        body_params = prepar_check_search_params_body_params_3()
        res = check_search_params(query_params, body_params)
            
        # ======================================================
        query_params = prepar_check_search_params_query_params_5()
        body_params = prepar_check_search_params_body_params_4()
        try:
            res = check_search_params(query_params, body_params)
        except Exception as err:
            self.assertEqual(type(err), MissingParamsException)
            
        # ======================================================
        query_params = prepar_check_search_params_query_params_5()
        body_params = prepar_check_search_params_body_params_5()
        try:
            res = check_search_params(query_params, body_params)
        except Exception as err:
            self.assertEqual(type(err), MissingParamsException)
            
        # ======================================================
        query_params = prepar_check_search_params_query_params_5()
        body_params = prepar_check_search_params_body_params_6()
        try:
            res = check_search_params(query_params, body_params)
        except Exception as err:
            self.assertEqual(type(err), ParamsWrongTypeException)
            
        # ======================================================
        query_params = prepar_check_search_params_query_params_5()
        body_params = prepar_check_search_params_body_params_7()
        try:
            res = check_search_params(query_params, body_params)
        except Exception as err:
            self.assertEqual(type(err), ParamsWrongTypeException)
            
        # ======================================================
        query_params = prepar_check_search_params_query_params_5()
        body_params = prepar_check_search_params_body_params_8()
        try:
            res = check_search_params(query_params, body_params)
        except Exception as err:
            self.assertEqual(type(err), ParamsWrongTypeException)
            
        # ======================================================
        query_params = prepar_check_search_params_query_params_5()
        body_params = prepar_check_search_params_body_params_9()
        try:
            res = check_search_params(query_params, body_params)
        except Exception as err:
            self.assertEqual(type(err), MissingParamsException)
            
        # ======================================================


        query_params = prepar_check_search_params_query_params_6()
        body_params = prepar_check_search_params_body_params_1()
        try:
            res = check_search_params(query_params, body_params)
        except Exception as err:
            print(err)
            self.assertEqual(type(err), InvalidParamsException)
            
        # ======================================================
        query_params = prepar_check_search_params_query_params_6()
        body_params = prepar_check_search_params_body_params_2()
        try:
            res = check_search_params(query_params, body_params)
        except Exception as err:
            self.assertEqual(type(err), InvalidParamsException)
            
        # ======================================================
        query_params = prepar_check_search_params_query_params_6()
        body_params = prepar_check_search_params_body_params_3()

        try:
            res = check_search_params(query_params, body_params)
        except Exception as err:
            self.assertEqual(type(err), InvalidParamsException)
            
        # ======================================================
        query_params = prepar_check_search_params_query_params_6()
        body_params = prepar_check_search_params_body_params_4()
        try:
            res = check_search_params(query_params, body_params)
        except Exception as err:
            self.assertEqual(type(err), MissingParamsException)
            
        # ======================================================
        query_params = prepar_check_search_params_query_params_6()
        body_params = prepar_check_search_params_body_params_5()
        try:
            res = check_search_params(query_params, body_params)
        except Exception as err:
            self.assertEqual(type(err), InvalidParamsException)
            
        # ======================================================
        query_params = prepar_check_search_params_query_params_6()
        body_params = prepar_check_search_params_body_params_6()
        try:
            res = check_search_params(query_params, body_params)
        except Exception as err:
            self.assertEqual(type(err), ParamsWrongTypeException)
            
        # ======================================================
        query_params = prepar_check_search_params_query_params_6()
        body_params = prepar_check_search_params_body_params_7()
        try:
            res = check_search_params(query_params, body_params)
        except Exception as err:
            self.assertEqual(type(err), ParamsWrongTypeException)
            
        # ======================================================
        query_params = prepar_check_search_params_query_params_6()
        body_params = prepar_check_search_params_body_params_8()
        try:
            res = check_search_params(query_params, body_params)
        except Exception as err:
            self.assertEqual(type(err), ParamsWrongTypeException)
            
        # ======================================================
        query_params = prepar_check_search_params_query_params_6()
        body_params = prepar_check_search_params_body_params_9()
        try:
            res = check_search_params(query_params, body_params)
        except Exception as err:
            self.assertEqual(type(err), MissingParamsException)
            
        # ======================================================
    
        query_params = prepar_check_search_params_query_params_7()
        body_params = prepar_check_search_params_body_params_1()
        try:
            res = check_search_params(query_params, body_params)
        except Exception as err:
            print(err)
            self.assertEqual(type(err), InvalidParamsException)
            
        # ======================================================
        query_params = prepar_check_search_params_query_params_7()
        body_params = prepar_check_search_params_body_params_2()
        try:
            res = check_search_params(query_params, body_params)
        except Exception as err:
            self.assertEqual(type(err), InvalidParamsException)
            
        # ======================================================
        query_params = prepar_check_search_params_query_params_7()
        body_params = prepar_check_search_params_body_params_3()

        try:
            res = check_search_params(query_params, body_params)
        except Exception as err:
            self.assertEqual(type(err), InvalidParamsException)
            
        # ======================================================
        query_params = prepar_check_search_params_query_params_7()
        body_params = prepar_check_search_params_body_params_4()
        try:
            res = check_search_params(query_params, body_params)
        except Exception as err:
            self.assertEqual(type(err), MissingParamsException)
            
        # ======================================================
        query_params = prepar_check_search_params_query_params_7()
        body_params = prepar_check_search_params_body_params_5()
        try:
            res = check_search_params(query_params, body_params)
        except Exception as err:
            self.assertEqual(type(err), InvalidParamsException)
            
        # ======================================================
        query_params = prepar_check_search_params_query_params_7()
        body_params = prepar_check_search_params_body_params_6()
        try:
            res = check_search_params(query_params, body_params)
        except Exception as err:
            self.assertEqual(type(err), ParamsWrongTypeException)
            
        # ======================================================
        query_params = prepar_check_search_params_query_params_7()
        body_params = prepar_check_search_params_body_params_7()
        try:
            res = check_search_params(query_params, body_params)
        except Exception as err:
            self.assertEqual(type(err), ParamsWrongTypeException)
            
        # ======================================================
        query_params = prepar_check_search_params_query_params_7()
        body_params = prepar_check_search_params_body_params_8()
        try:
            res = check_search_params(query_params, body_params)
        except Exception as err:
            self.assertEqual(type(err), ParamsWrongTypeException)
            
        # ======================================================
        query_params = prepar_check_search_params_query_params_7()
        body_params = prepar_check_search_params_body_params_9()
        try:
            res = check_search_params(query_params, body_params)
        except Exception as err:
            self.assertEqual(type(err), MissingParamsException)
            
        # ======================================================


        query_params = prepar_check_search_params_query_params_8()
        body_params = prepar_check_search_params_body_params_1()
        try:
            res = check_search_params(query_params, body_params)
        except Exception as err:
            print(err)
            self.assertEqual(type(err), InvalidParamsException)
            
        # ======================================================
        query_params = prepar_check_search_params_query_params_8()
        body_params = prepar_check_search_params_body_params_2()
        try:
            res = check_search_params(query_params, body_params)
        except Exception as err:
            self.assertEqual(type(err), InvalidParamsException)
            
        # ======================================================
        query_params = prepar_check_search_params_query_params_8()
        body_params = prepar_check_search_params_body_params_3()

        try:
            res = check_search_params(query_params, body_params)
        except Exception as err:
            self.assertEqual(type(err), InvalidParamsException)
            
        # ======================================================
        query_params = prepar_check_search_params_query_params_8()
        body_params = prepar_check_search_params_body_params_4()
        try:
            res = check_search_params(query_params, body_params)
        except Exception as err:
            self.assertEqual(type(err), MissingParamsException)
            
        # ======================================================
        query_params = prepar_check_search_params_query_params_8()
        body_params = prepar_check_search_params_body_params_5()
        try:
            res = check_search_params(query_params, body_params)
        except Exception as err:
            self.assertEqual(type(err), InvalidParamsException)
            
        # ======================================================
        query_params = prepar_check_search_params_query_params_8()
        body_params = prepar_check_search_params_body_params_6()
        try:
            res = check_search_params(query_params, body_params)
        except Exception as err:
            self.assertEqual(type(err), ParamsWrongTypeException)
            
        # ======================================================
        query_params = prepar_check_search_params_query_params_8()
        body_params = prepar_check_search_params_body_params_7()
        try:
            res = check_search_params(query_params, body_params)
        except Exception as err:
            self.assertEqual(type(err), ParamsWrongTypeException)
            
        # ======================================================
        query_params = prepar_check_search_params_query_params_8()
        body_params = prepar_check_search_params_body_params_8()
        try:
            res = check_search_params(query_params, body_params)
        except Exception as err:
            self.assertEqual(type(err), ParamsWrongTypeException)
            
        # ======================================================
        query_params = prepar_check_search_params_query_params_8()
        body_params = prepar_check_search_params_body_params_9()
        try:
            res = check_search_params(query_params, body_params)
        except Exception as err:
            self.assertEqual(type(err), MissingParamsException)
            
        # ======================================================


        query_params = prepar_check_search_params_query_params_9()
        body_params = prepar_check_search_params_body_params_1()
        try:
            res = check_search_params(query_params, body_params)
        except Exception as err:
            print(err)
            self.assertEqual(type(err), InvalidParamsException)
            
        # ======================================================
        query_params = prepar_check_search_params_query_params_9()
        body_params = prepar_check_search_params_body_params_2()
        try:
            res = check_search_params(query_params, body_params)
        except Exception as err:
            self.assertEqual(type(err), InvalidParamsException)
            
        # ======================================================
        query_params = prepar_check_search_params_query_params_9()
        body_params = prepar_check_search_params_body_params_3()

        try:
            res = check_search_params(query_params, body_params)
        except Exception as err:
            self.assertEqual(type(err), InvalidParamsException)
            
        # ======================================================
        query_params = prepar_check_search_params_query_params_9()
        body_params = prepar_check_search_params_body_params_4()
        try:
            res = check_search_params(query_params, body_params)
        except Exception as err:
            self.assertEqual(type(err), MissingParamsException)
            
        # ======================================================
        query_params = prepar_check_search_params_query_params_9()
        body_params = prepar_check_search_params_body_params_5()
        try:
            res = check_search_params(query_params, body_params)
        except Exception as err:
            self.assertEqual(type(err), InvalidParamsException)
            
        # ======================================================
        query_params = prepar_check_search_params_query_params_9()
        body_params = prepar_check_search_params_body_params_6()
        try:
            res = check_search_params(query_params, body_params)
        except Exception as err:
            self.assertEqual(type(err), ParamsWrongTypeException)
            
        # ======================================================
        query_params = prepar_check_search_params_query_params_9()
        body_params = prepar_check_search_params_body_params_7()
        try:
            res = check_search_params(query_params, body_params)
        except Exception as err:
            self.assertEqual(type(err), ParamsWrongTypeException)
            
        # ======================================================
        query_params = prepar_check_search_params_query_params_9()
        body_params = prepar_check_search_params_body_params_8()
        try:
            res = check_search_params(query_params, body_params)
        except Exception as err:
            self.assertEqual(type(err), ParamsWrongTypeException)
            
        # ======================================================
        query_params = prepar_check_search_params_query_params_9()
        body_params = prepar_check_search_params_body_params_9()
        try:
            res = check_search_params(query_params, body_params)
        except Exception as err:
            self.assertEqual(type(err), MissingParamsException)
            
        # ======================================================



        query_params = prepar_check_search_params_query_params_10()
        body_params = prepar_check_search_params_body_params_1()
        try:
            res = check_search_params(query_params, body_params)
        except Exception as err:
            print(err)
            self.assertEqual(type(err), InvalidParamsException)
            
        # ======================================================
        query_params = prepar_check_search_params_query_params_10()
        body_params = prepar_check_search_params_body_params_2()
        try:
            res = check_search_params(query_params, body_params)
        except Exception as err:
            self.assertEqual(type(err), InvalidParamsException)
            
        # ======================================================
        query_params = prepar_check_search_params_query_params_10()
        body_params = prepar_check_search_params_body_params_3()

        try:
            res = check_search_params(query_params, body_params)
        except Exception as err:
            self.assertEqual(type(err), InvalidParamsException)
            
        # ======================================================
        query_params = prepar_check_search_params_query_params_10()
        body_params = prepar_check_search_params_body_params_4()
        try:
            res = check_search_params(query_params, body_params)
        except Exception as err:
            self.assertEqual(type(err), MissingParamsException)
            
        # ======================================================
        query_params = prepar_check_search_params_query_params_10()
        body_params = prepar_check_search_params_body_params_5()
        try:
            res = check_search_params(query_params, body_params)
        except Exception as err:
            self.assertEqual(type(err), InvalidParamsException)
            
        # ======================================================
        query_params = prepar_check_search_params_query_params_10()
        body_params = prepar_check_search_params_body_params_6()
        try:
            res = check_search_params(query_params, body_params)
        except Exception as err:
            self.assertEqual(type(err), ParamsWrongTypeException)
            
        # ======================================================
        query_params = prepar_check_search_params_query_params_10()
        body_params = prepar_check_search_params_body_params_7()
        try:
            res = check_search_params(query_params, body_params)
        except Exception as err:
            self.assertEqual(type(err), ParamsWrongTypeException)
            
        # ======================================================
        query_params = prepar_check_search_params_query_params_10()
        body_params = prepar_check_search_params_body_params_8()
        try:
            res = check_search_params(query_params, body_params)
        except Exception as err:
            self.assertEqual(type(err), ParamsWrongTypeException)
            
        # ======================================================
        query_params = prepar_check_search_params_query_params_10()
        body_params = prepar_check_search_params_body_params_9()
        try:
            res = check_search_params(query_params, body_params)
        except Exception as err:
            self.assertEqual(type(err), MissingParamsException)
            
        # ======================================================




        query_params = prepar_check_search_params_query_params_11()
        body_params = prepar_check_search_params_body_params_1()
        try:
            res = check_search_params(query_params, body_params)
        except Exception as err:
            print(err)
            self.assertEqual(type(err), InvalidParamsException)
            
        # ======================================================
        query_params = prepar_check_search_params_query_params_11()
        body_params = prepar_check_search_params_body_params_2()
        try:
            res = check_search_params(query_params, body_params)
        except Exception as err:
            self.assertEqual(type(err), InvalidParamsException)
            
        # ======================================================
        query_params = prepar_check_search_params_query_params_11()
        body_params = prepar_check_search_params_body_params_3()

        try:
            res = check_search_params(query_params, body_params)
        except Exception as err:
            self.assertEqual(type(err), InvalidParamsException)
            
        # ======================================================
        query_params = prepar_check_search_params_query_params_11()
        body_params = prepar_check_search_params_body_params_4()
        try:
            res = check_search_params(query_params, body_params)
        except Exception as err:
            self.assertEqual(type(err), MissingParamsException)
            
        # ======================================================
        query_params = prepar_check_search_params_query_params_11()
        body_params = prepar_check_search_params_body_params_5()
        try:
            res = check_search_params(query_params, body_params)
        except Exception as err:
            self.assertEqual(type(err), InvalidParamsException)
            
        # ======================================================
        query_params = prepar_check_search_params_query_params_11()
        body_params = prepar_check_search_params_body_params_6()
        try:
            res = check_search_params(query_params, body_params)
        except Exception as err:
            self.assertEqual(type(err), ParamsWrongTypeException)
            
        # ======================================================
        query_params = prepar_check_search_params_query_params_11()
        body_params = prepar_check_search_params_body_params_7()
        try:
            res = check_search_params(query_params, body_params)
        except Exception as err:
            self.assertEqual(type(err), ParamsWrongTypeException)
            
        # ======================================================
        query_params = prepar_check_search_params_query_params_11()
        body_params = prepar_check_search_params_body_params_8()
        try:
            res = check_search_params(query_params, body_params)
        except Exception as err:
            self.assertEqual(type(err), ParamsWrongTypeException)
            
        # ======================================================
        query_params = prepar_check_search_params_query_params_11()
        body_params = prepar_check_search_params_body_params_9()
        try:
            res = check_search_params(query_params, body_params)
        except Exception as err:
            self.assertEqual(type(err), MissingParamsException)
            
        # ======================================================


        query_params = prepar_check_search_params_query_params_12()
        body_params = prepar_check_search_params_body_params_1()
        try:
            res = check_search_params(query_params, body_params)
        except Exception as err:
            print(err)
            self.assertEqual(type(err), InvalidParamsException)
            
        # ======================================================
        query_params = prepar_check_search_params_query_params_12()
        body_params = prepar_check_search_params_body_params_2()
        try:
            res = check_search_params(query_params, body_params)
        except Exception as err:
            self.assertEqual(type(err), InvalidParamsException)
            
        # ======================================================
        query_params = prepar_check_search_params_query_params_12()
        body_params = prepar_check_search_params_body_params_3()

        try:
            res = check_search_params(query_params, body_params)
        except Exception as err:
            self.assertEqual(type(err), InvalidParamsException)
            
        # ======================================================
        query_params = prepar_check_search_params_query_params_12()
        body_params = prepar_check_search_params_body_params_4()
        try:
            res = check_search_params(query_params, body_params)
        except Exception as err:
            self.assertEqual(type(err), MissingParamsException)
            
        # ======================================================
        query_params = prepar_check_search_params_query_params_12()
        body_params = prepar_check_search_params_body_params_5()
        try:
            res = check_search_params(query_params, body_params)
        except Exception as err:
            self.assertEqual(type(err), InvalidParamsException)
            
        # ======================================================
        query_params = prepar_check_search_params_query_params_12()
        body_params = prepar_check_search_params_body_params_6()
        try:
            res = check_search_params(query_params, body_params)
        except Exception as err:
            self.assertEqual(type(err), ParamsWrongTypeException)
            
        # ======================================================
        query_params = prepar_check_search_params_query_params_12()
        body_params = prepar_check_search_params_body_params_7()
        try:
            res = check_search_params(query_params, body_params)
        except Exception as err:
            self.assertEqual(type(err), ParamsWrongTypeException)
            
        # ======================================================
        query_params = prepar_check_search_params_query_params_12()
        body_params = prepar_check_search_params_body_params_8()
        try:
            res = check_search_params(query_params, body_params)
        except Exception as err:
            self.assertEqual(type(err), ParamsWrongTypeException)
            
        # ======================================================
        query_params = prepar_check_search_params_query_params_12()
        body_params = prepar_check_search_params_body_params_9()
        try:
            res = check_search_params(query_params, body_params)
        except Exception as err:
            self.assertEqual(type(err), MissingParamsException)
            
        # ======================================================

        query_params = prepar_check_search_params_query_params_13()
        body_params = prepar_check_search_params_body_params_1()
        res = check_search_params(query_params, body_params)

        # ======================================================
        query_params = prepar_check_search_params_query_params_13()
        body_params = prepar_check_search_params_body_params_2()
        res = check_search_params(query_params, body_params)
        
        # ======================================================
        query_params = prepar_check_search_params_query_params_13()
        body_params = prepar_check_search_params_body_params_3()
        res = check_search_params(query_params, body_params)

        # ======================================================
        query_params = prepar_check_search_params_query_params_13()
        body_params = prepar_check_search_params_body_params_4()
        try:
            res = check_search_params(query_params, body_params)
        except Exception as err:
            self.assertEqual(type(err), MissingParamsException)
            
        # ======================================================
        query_params = prepar_check_search_params_query_params_13()
        body_params = prepar_check_search_params_body_params_5()
        try:
            res = check_search_params(query_params, body_params)
        except Exception as err:
            self.assertEqual(type(err), MissingParamsException)
            
        # ======================================================
        query_params = prepar_check_search_params_query_params_13()
        body_params = prepar_check_search_params_body_params_6()
        try:
            res = check_search_params(query_params, body_params)
        except Exception as err:
            self.assertEqual(type(err), ParamsWrongTypeException)
            
        # ======================================================
        query_params = prepar_check_search_params_query_params_13()
        body_params = prepar_check_search_params_body_params_7()
        try:
            res = check_search_params(query_params, body_params)
        except Exception as err:
            self.assertEqual(type(err), ParamsWrongTypeException)
            
        # ======================================================
        query_params = prepar_check_search_params_query_params_13()
        body_params = prepar_check_search_params_body_params_8()
        try:
            res = check_search_params(query_params, body_params)
        except Exception as err:
            self.assertEqual(type(err), ParamsWrongTypeException)
            
        # ======================================================
        query_params = prepar_check_search_params_query_params_13()
        body_params = prepar_check_search_params_body_params_9()
        try:
            res = check_search_params(query_params, body_params)
        except Exception as err:
            self.assertEqual(type(err), MissingParamsException)
            
        # ======================================================

        query_params = prepar_check_search_params_query_params_13()
        body_params = prepar_check_search_params_body_params_11()
        try:
            res = check_search_params(query_params, body_params)
        except Exception as err:
            self.assertEqual(type(err), InvalidParamsException)