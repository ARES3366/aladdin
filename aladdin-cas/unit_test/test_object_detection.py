
print("============================== 以图搜图UT测试 ====================================")

import time
from object_detection.image_search_handler import image_meta_data_post, image_meta_data_get, image_meta_data_delete, similar_image_search_post, image_meta_data_put
import os
import unittest
import aiounittest
import base64
import asyncio
from exception_handler import ParamsException, InternalErrorException
from client.milvus_client import AioMilvus
from db_adapter.mongo_adapter import MongoDBClient
from object_detection.delete_meta_info import delete_meta_data_by_vid, delete_meta_data_by_url
from object_detection.search_similar_images import *
_get_module_path = lambda path: os.path.normpath(os.path.join(os.path.dirname(__file__),"testcase_data","image_search_test_case", path))
milvus_client_for_sub = AioMilvus("object_detection", asyncio.get_event_loop())
milvus_client_for_face = AioMilvus("face_recognition",asyncio.get_event_loop())
db_client = MongoDBClient()

def test_await_method(fun, *args):
    loop = asyncio.get_event_loop()
    loop.run_in_executor(fun, *args)
class TestImageSearch(aiounittest.AsyncTestCase):

    def get_event_loop(self):
        return asyncio.get_event_loop()

    async def test_1(self):
        print("=======================上传元数据============================")
        url = _get_module_path("0.png")
        url1 = _get_module_path("3.jpg")
        with open(url, "rb") as image:
            base64_data = base64.b64encode(image.read())
        with open(url, "rb") as image:
            base64_data1 = base64.b64encode(image.read())
        b64 = str(base64_data, encoding="utf-8")
        b641 = str(base64_data1, encoding="utf-8")
        time.sleep(2)
        print("---base64 缺失") 
        params = dict(url=url)
        try:
            res = await image_meta_data_post(params)
        except Exception as err:
            self.assertEqual(type(err), ParamsException)
            self.assertEqual(err.code, "400001000")

        print("---base64 非法")
        params = dict(url=url, image=b64[:-2])
        try:
            res = await image_meta_data_post(params)
        except Exception as err:
            self.assertEqual(type(err), ParamsException)
            self.assertEqual(err.code, "400001000")

        print("---base64 不是字符串类型")
        params = dict(url=url, image=0)
        try:
            res = await image_meta_data_post(params)
        except Exception as err:
            self.assertEqual(type(err), ParamsException)
            self.assertEqual(err.code, "400001000")

        params = dict(url=url, image="")
        try:
            res = await image_meta_data_post(params)
        except Exception as err:
            self.assertEqual(type(err), ParamsException)
            self.assertEqual(err.code, "400001000")

        print("---url 为空")
        params = dict(url="", image=b64)
        try:
            res = await image_meta_data_post(params)
        except Exception as err:
            self.assertEqual(type(err), ParamsException)
            self.assertEqual(err.code, "400001000")

        print("---url 缺失")
        params = dict(image=b64)
        try:
            res = await image_meta_data_post(params)
        except Exception as err:
            self.assertEqual(type(err), ParamsException)
            self.assertEqual(err.code, "400001000")
        
        print("---url 不是字符串")
        params = dict(url=0, image=b64)
        try:
            res = await image_meta_data_post(params)
        except Exception as err:
            self.assertEqual(type(err), ParamsException)
            self.assertEqual(err.code, "400001000")

        print("--- 输入正确")
        url = _get_module_path("0.png")
        params = dict(url=url, image=b64)
        res = await image_meta_data_post(params)
        print(f"res: {res}")
        self.assertEqual(res.get("code"), 200)
        print("--- 输入正确")

        params1 = dict(url=url1, image=b641)
        res = await image_meta_data_post(params1)
        print(f"res: {res}")
        self.assertEqual(res.get("code"), 200)
        print("=======================获取元数据============================")
        print("---url 不存在")
        url = _get_module_path("gerge.png")
        params = dict(url=url)
        try:
            res = await image_meta_data_get(params)
        except Exception as err:
            self.assertEqual(type(err), InternalErrorException)
            self.assertEqual(err.code, "500001001") # 上传不存在的url返回空列表
            self.assertEqual(err.code, "500001001")

        print("---url 为空")
        params = dict(url="")
        try:
            res = await image_meta_data_get(params)
        except Exception as err:
            self.assertEqual(type(err), ParamsException)
            self.assertEqual(err.code, "400001000")
        print("---url 不是字符串")
        params = dict(url=0)
        try:
            res = await image_meta_data_get(params)
        except Exception as err:
            self.assertEqual(type(err), ParamsException)
            self.assertEqual(err.code, "400001000")

        print("---url 缺失")
        params = dict()
        try:
            res = await image_meta_data_get(params)
        except Exception as err:
            self.assertEqual(type(err), ParamsException)
            self.assertEqual(err.code, "400001000")

        print("---输入正确")
        params = dict(url=_get_module_path("0.png"))
        res = await image_meta_data_get(params)
        print(f"res: {res}")
        self.assertEqual(res.get("code"), 200)   

        # print("=======================搜索相似图片============================")
        # url = _get_module_path("3.jpg")
        # with open(url, "rb") as image:
        #     base64_data = base64.b64encode(image.read())
        # b64 = str(base64_data, encoding="utf-8")
        # res = await image_meta_data_get(params)
        # print(f"------res: {res}")
        # vid = res["image_meta_data_list"][0]["vid"]
        # vid = str(vid)
        # time.sleep(2)
        # print(f"---输入正确 1 :{url}")
        # params = dict(url=url, top_k=10)
        # print(params)
        # res = await similar_image_search_post(params)
        # print(f"res: {res}")
        # self.assertEqual(res.get("code"), 200)

        # print("---输入正确 2")
        # params = dict(vid=vid, top_k=10)
        # res = await similar_image_search_post(params)
        # print(f"res: {res}")
        # self.assertEqual(res.get("code"), 200)

        # print("---输入正确 3")
        # params = dict(image=b64, top_k=10)
        # res = await similar_image_search_post(params)
        # print(f"res: {res}")
        # self.assertEqual(res.get("code"), 200)

        # url = _get_module_path("0.png")
        # with open(url, "rb") as image:
        #     base64_data = base64.b64encode(image.read())
        # b64 = str(base64_data, encoding="utf-8")
        # print(f"-----------: {res}")
        # params = dict(url=_get_module_path("0.png"))
        # res = await image_meta_data_get(params)
        # vid = res["image_meta_data_list"][0]["vid"]
        # vid = str(vid)
        # time.sleep(2)
        # print("---输入正确 1")
        # params = dict(url=url, top_k=10)
        # print(params)
        # res = await similar_image_search_post(params)
        # print(f"res: {res}")
        # self.assertEqual(res.get("code"), 200)

        # print("---输入正确 2")
        # params = dict(vid=vid, top_k=10)
        # res = await similar_image_search_post(params)
        # print(f"res: {res}")
        # self.assertEqual(res.get("code"), 200)

        # print("---输入正确 3")
        # params = dict(image=b64, top_k=10)
        
        # res = await similar_image_search_post(params)
        # print(f"res: {res}")
        # self.assertEqual(res.get("code"), 200)

        # print("---url 不存在1")
        # url = _get_module_path("gerge.png")
        # print(f"url:{url}")
        # params = dict(url=url, top_k=10)
        # try:
        #     res = await similar_image_search_post(params)
        # except Exception as err:
        #     print(err.generate_response())
        #     self.assertEqual(type(err), InternalErrorException)
        #     self.assertEqual(err.code, "500001001")

        # print("---topk <=0 url 不存在4")
        # url = _get_module_path("gerge.png")
        # params = dict(url=url, top_k=-1)
        # try:
        #     res = await similar_image_search_post(params)
        # except Exception as err:
        #     self.assertEqual(type(err), ParamsException)
        #     self.assertEqual(err.code, "400001000")

        # print("---topk > 100 url 不存在5")
        # url = _get_module_path("gerge.png")
        # params = dict(url=url, top_k=101)
        # try:
        #     res = await similar_image_search_post(params)
        # except Exception as err:
        #     self.assertEqual(type(err), ParamsException)
        #     self.assertEqual(err.code, "400001000")

        # print("---url 为空1")
        # params = dict(url="", top_k=10)
        # try:
        #     res = await similar_image_search_post(params)
        # except Exception as err:
        #     self.assertEqual(type(err), ParamsException)
        #     self.assertEqual(err.code, "400001000")

        # print("---url 不是字符串1")
        # params = dict(url=0, top_k=10)
        # try:
        #     res = await similar_image_search_post(params)
        # except Exception as err:
        #     self.assertEqual(type(err), ParamsException)
        #     self.assertEqual(err.code, "400001000")
        
        # print("---vid 不存在1")
        # params = dict(vid="12342345125112", top_k=10)
        # try:
        #     res = await similar_image_search_post(params)
        # except Exception as err:
        #     self.assertEqual(type(err), InternalErrorException)
        #     self.assertEqual(err.code, "500001001")
        # print("---vid 为空")
        # params = dict(vid="", top_k=10)
        # try:
        #     res = await similar_image_search_post(params)
        # except Exception as err:
        #     self.assertEqual(type(err), ParamsException)
        #     self.assertEqual(err.code, "400001000")

        # print("---vid 不是字符串1")
        # params = dict(vid=1589879800197584000, top_k=10)
        # try:
        #     res = await similar_image_search_post(params)
        # except Exception as err:
        #     self.assertEqual(type(err), ParamsException)
        #     self.assertEqual(err.code, "400001000")

        # print("---base64 不完整")
        # params = dict(image=b64[:2], top_k=10)
        # try:
        #     res = await similar_image_search_post(params)
        # except Exception as err:
        #     self.assertEqual(type(err), ParamsException)
        #     self.assertEqual(err.code, "400001000")

        # print("---base64 非法")
        # params = dict(image="gwergewge", top_k=10)
        # try:
        #     res = await similar_image_search_post(params)
        # except Exception as err:
        #     self.assertEqual(type(err), ParamsException)
        #     self.assertEqual(err.code, "400001000")

        # print("---base64 不是字符串类型")
        # params = dict(image=64, top_k=10)
        # try:
        #     res = await similar_image_search_post(params)
        # except Exception as err:
        #     self.assertEqual(type(err), ParamsException)
        #     self.assertEqual(err.code, "400001000")

        # print("---base64 为空")
        # params = dict(image="", top_k=10)
        # try:
        #     res = await similar_image_search_post(params)
        # except Exception as err:
        #     self.assertEqual(type(err), ParamsException)
        #     self.assertEqual(err.code, "400001000")

        # print("---参数不正确")
        # url = _get_module_path("0.png")
        # params = dict(url=url, image=b64, vid=vid, top_k=10)
        # try:
        #     res = await similar_image_search_post(params)
        # except Exception as err:
        #     self.assertEqual(type(err), ParamsException)
        #     self.assertEqual(err.code, "400001000")

        # url = _get_module_path("0.png")
        # params = dict(url=url, image=b64, top_k=10)
        # try:
        #     res = await similar_image_search_post(params)
        # except Exception as err:
        #     self.assertEqual(type(err), ParamsException)
        #     self.assertEqual(err.code, "400001000")

        # url = _get_module_path("0.png")
        # params = dict(url=url, vid=vid, top_k=10)
        # try:
        #     res = await similar_image_search_post(params)
        # except Exception as err:
        #     self.assertEqual(type(err), ParamsException)
        #     self.assertEqual(err.code, "400001000")

        # url = _get_module_path("0.png")
        # params = dict(vid=url, image=b64, top_k=10)
        # try:
        #     res = await similar_image_search_post(params)
        # except Exception as err:
        #     self.assertEqual(type(err), ParamsException)
        #     self.assertEqual(err.code, "400001000")

        # params = dict(top_k=10)
        # try:
        #     res = await similar_image_search_post(params)
        # except Exception as err:
        #     self.assertEqual(type(err), ParamsException)
        #     self.assertEqual(err.code, "400001000")
        

        print("=======================删除元数据============================")
        print("---url 不存在")
        url = _get_module_path("gerge.png")
        params = ["ffef"]
        res=await image_meta_data_delete(params, "url")
        print(f"res: {res}")
        self.assertEqual(res.get("code"), 200)

        print("---url 为空")
        params = [""]
        try:
            res = await image_meta_data_delete(params, "url")
        except Exception as err:
            self.assertEqual(type(err), ParamsException)
            self.assertEqual(err.code, "400001000")

        print("---url 不是字符串")
        params = [112,33]
        try:
            res = await image_meta_data_delete(params,"url")
        except Exception as err:
            self.assertEqual(type(err), ParamsException)
            self.assertEqual(err.code, "400001000")

        print("---url 缺失")
        params = []
        try:
            res = await image_meta_data_delete(params, "url")
        except Exception as err:
            self.assertEqual(type(err), ParamsException)
            self.assertEqual(err.code, "400001000")
        
        print("---vid 不存在")
        params = ["fewqgjweggewgjqwigqwe"]
        try:
            res = await image_meta_data_delete(params,"vid")
        except Exception as err:
            self.assertEqual(type(err), ParamsException)
            self.assertEqual(err.code, "400001000")
        print(f"res: {res}")
        self.assertEqual(res.get("code"), 200)

        print("---vid 为空")
        params = [""]
        try:
            res = await image_meta_data_delete(params,"vid")
        except Exception as err:
            self.assertEqual(type(err), ParamsException)
            self.assertEqual(err.code, "400001000")

        print("---vid 不是字符串")
        params = [1]
        try:
            res = await image_meta_data_delete(params,"vid")
        except Exception as err:
            self.assertEqual(type(err), ParamsException)
            self.assertEqual(err.code, "400001000")

        print("---vid 缺失")
        params = []
        try:
            res = await image_meta_data_delete(params,"vid")
        except Exception as err:
            self.assertEqual(type(err), ParamsException)
            self.assertEqual(err.code, "400001000")

        # print("---参数设置不正确")
        # params = dict(url=url, vid=vid)
        # try:
        #     res = await image_meta_data_delete(params)
        # except Exception as err:
        #     self.assertEqual(type(err), ParamsException)
        #     self.assertEqual(err.code, "400001000")

        print("---输入正确使用url删除")
        params = [_get_module_path("0.png")]
        res = await image_meta_data_delete(params,"url")
        print(f"res: {res}")
        self.assertEqual(res.get("code"), 200)


        url = _get_module_path("0.png")
        params = dict(url=url, image=b64)
        res = await image_meta_data_post(params)
        params = dict(url=url)
        res = await image_meta_data_get(params)
        print(res["image_meta_data_list"])
        vid = str(res["image_meta_data_list"][0]["vid"])
        params = [vid]
        res = await image_meta_data_delete(params,"vid")
        print(f"res: {res}")
        self.assertEqual(res.get("code"), 200)


        print(f"---输入正确使用vid列表: {vid}删除")
        url = _get_module_path("0.png")
        params = dict(url=url, image=b64)
        res = await image_meta_data_post(params)
        params = dict(url=url)
        res = await image_meta_data_get(params)
        print(res["image_meta_data_list"])
        vid_list = []
        for item in res["image_meta_data_list"]:
            vid_list.append(str(item["vid"]))
        res = await image_meta_data_delete(vid_list,"vid")
        print(f"res: {res}")
        self.assertEqual(res.get("code"), 200)

        print(f"---输入正确使用vid和不存在的vid列表: {vid}删除")
        url = _get_module_path("0.png")
        params = dict(url=url, image=b64)
        res = await image_meta_data_post(params)
        params = dict(url=url)
        res = await image_meta_data_get(params)
        print(res["image_meta_data_list"])
        vid_list = []
        for item in res["image_meta_data_list"]:
            vid_list.append(str(item["vid"]))
        vid_list.append("ererewwfjwifjeiw")
        vid_list.append("1231453212141")
        
        try:
            res = await image_meta_data_delete(vid_list,"vid")
        except Exception as err:
            self.assertEqual(type(err), ParamsException)
            self.assertEqual(err.code, "500001001")
        

        print("=======================修改元数据============================")
        print("---输入正确")
        url = _get_module_path("0.png")
        params = dict(url=url, image=b64)
        res = await image_meta_data_post(params)
        params = dict(url=url)
        res = await image_meta_data_get(params)
        vid = str(res["image_meta_data_list"][0]["vid"])
        params = [dict(vid=vid, label="aaaa")]
        res1 = await image_meta_data_put(params)
        params = [vid]
        res = await image_meta_data_delete(params, "vid")
        print(f"res: {res1}")
        self.assertEqual(res1.get("code"), 200)

        print("---缺少vid")
        url = _get_module_path("0.png")
        params = dict(url=url, image=b64)
        res = await image_meta_data_post(params)
        time.sleep(1)
        params = dict(url=url)
        res = await image_meta_data_get(params)
        vid = str(res["image_meta_data_list"][0]["vid"])
        params = [dict(label="aaaa")]
        try:
            res = await image_meta_data_put(params)
        except Exception as err:
            self.assertEqual(type(err), ParamsException)
            self.assertEqual(err.code, "400001000")
        params = [vid]
        res = await image_meta_data_delete(params,"vid")


        print("---缺少label")
        url = _get_module_path("0.png")
        params = dict(url=url, image=b64)
        res = await image_meta_data_post(params)
        time.sleep(1)
        params = dict(url=url)
        res = await image_meta_data_get(params)
        print(res)
        vid = str(res["image_meta_data_list"][0]["vid"])
        params = [dict(vid=vid)]
        try:
            res = await image_meta_data_put(params)
        except Exception as err:
            self.assertEqual(type(err), ParamsException)
            self.assertEqual(err.code, "400001000")
        params = dict(url=url)
        res = await image_meta_data_get(params)
        print(res)
        params = ["vid"]
        res = await image_meta_data_delete(params,"vid")

        print("---缺少vid和label")
        url = _get_module_path("0.png")
        params = dict(url=url, image=b64)
        res = await image_meta_data_post(params)
        time.sleep(1)
        params = dict(url=url)
        res = await image_meta_data_get(params)
        print(res)
        vid = str(res["image_meta_data_list"][0]["vid"])
        params = [dict()]
        try:
            res = await image_meta_data_put(params)
        except Exception as err:
            self.assertEqual(type(err), ParamsException)
            self.assertEqual(err.code, "400001000")
        params = dict(url=url)
        res = await image_meta_data_get(params)
        print(res)
        params = [vid]
        res = await image_meta_data_delete(params, "vid")

        print("---vid 不存在")
        url = _get_module_path("0.png")
        params = dict(url=url, image=b64)
        print(f"post")
        res = await image_meta_data_post(params)
        time.sleep(1)
        params = dict(url=url)
        print("get")
        res = await image_meta_data_get(params)
        print(f"get res:{res}")
        vid = str(res["image_meta_data_list"][0]["vid"])
        print(f"vid: {vid}")
        params = [dict(vid="1597202475446139000", label="aaaa")]
        print("put")
        try:
            res = await image_meta_data_put(params)
        except Exception as err:
            self.assertEqual(type(err), InternalErrorException)
            self.assertEqual(err.code, "500001001")
        params = dict(url=url)
        print(f"get")
        res = await image_meta_data_get(params)
        print(f"get res:{res}")
        params = [vid]
        res = await image_meta_data_delete(params,"vid")

        print("---vid 非法")
        url = _get_module_path("0.png")
        params = dict(url=url, image=b64)
        res = await image_meta_data_post(params)
        time.sleep(1)
        params = dict(url=url)
        res = await image_meta_data_get(params)
        print(res)
        vid = str(res["image_meta_data_list"][0]["vid"])
        params = [dict(vid="fwefwqgwqegwg", label="aaaa")]
        try:
            res = await image_meta_data_put(params)
        except Exception as err:
            self.assertEqual(type(err), InternalErrorException)
            self.assertEqual(err.code, "500001001")
        params = dict(url=url)
        res = await image_meta_data_get(params)
        print(res)
        params = [vid]
        res = await image_meta_data_delete(params,"vid")

        print("---vid 为空")
        url = _get_module_path("0.png")
        params = dict(url=url, image=b64)
        res = await image_meta_data_post(params)
        time.sleep(1)
        params = dict(url=url)
        res = await image_meta_data_get(params)
        print(res)
        vid = str(res["image_meta_data_list"][0]["vid"])
        params = [dict(vid="", label="aaaa")]
        try:
            res = await image_meta_data_put(params)
        except Exception as err:
            self.assertEqual(type(err), ParamsException)
            self.assertEqual(err.code, "400001000")
        params = dict(url=url)
        res = await image_meta_data_get(params)
        print(res)
        params = [vid]
        res = await image_meta_data_delete(params,"vid")

        print("---vid 非字符串")
        url = _get_module_path("0.png")
        params = dict(url=url, image=b64)
        res = await image_meta_data_post(params)
        time.sleep(1)
        params = dict(url=url)
        res = await image_meta_data_get(params)
        print(res)
        vid = res["image_meta_data_list"][0]["vid"]
        vid = int(vid)
        params = [dict(vid=vid, label="aaaa")]
        try:
            res = await image_meta_data_put(params)
        except Exception as err:
            self.assertEqual(type(err), ParamsException)
            self.assertEqual(err.code, "400001000")
        params = dict(url=url)
        res = await image_meta_data_get(params)
        print(res)
        params = [str(vid)]
        res = await image_meta_data_delete(params,"vid")

        print("---label 非字符串")
        url = _get_module_path("0.png")
        params = dict(url=url, image=b64)
        res = await image_meta_data_post(params)
        time.sleep(1)
        params = dict(url=url)
        res = await image_meta_data_get(params)
        print(res)
        vid = str(res["image_meta_data_list"][0]["vid"])
        params = [dict(vid=vid, label=123)]
        try:
            res = await image_meta_data_put(params)
        except Exception as err:
            self.assertEqual(type(err), ParamsException)
            self.assertEqual(err.code, "400001000")
        params = dict(url=url)
        res = await image_meta_data_get(params)
        print(res)
        params = [vid]
        res = await image_meta_data_delete(params,"vid") 
        print("-----------其他方法测试")
        print("---测试删除方法 delete_meta_data_by_vid")
        print("测试'failed to search data from mongodb by vid' 方法1")
        vid_list = []
        result = await delete_meta_data_by_vid(vid_list, milvus_client_for_sub, milvus_client_for_face, db_client)
        self.assertEqual(result.get("status"), 0)
            
        print("测试'failed to search data from mongodb by vid' 方法2")
        id_list = ""
        try:
            result = await delete_meta_data_by_vid(vid_list, milvus_client_for_sub, milvus_client_for_face, db_client)
        except Exception as err:
            self.assertEqual(type(err), ParamsException)
            self.assertEqual(err.code, "500001000")
        print("测试'failed to search data from mongodb by vid' 方法3 删除时 mongodb 不存在数据")
        vid_list = []
        url = _get_module_path("0.png")
        with open(url, "rb") as image:
            base64_data = base64.b64encode(image.read())
        b64 = str(base64_data, encoding="utf-8")
        params = dict(url=url, image=b64)
        res = await image_meta_data_post(params)
        select_result = await db_client.select({})
        vid_list = [item["vid"] for item in select_result]

        selected_vid_list_face = []
        selected_vid_list_sub = []
        selected_vid_list = []
        for item in select_result:
            if item["is_face"] is True:
                selected_vid_list_face.append(int(item["vid"]))
            else:
                selected_vid_list_sub.append(int(item["vid"]))
            selected_vid_list.append(item["vid"])
        await db_client.delete_many({"vid":{"$in": vid_list}})
        print(f"vid_list: {vid_list}")
        result = await delete_meta_data_by_vid(vid_list, milvus_client_for_sub, milvus_client_for_face, db_client)
        self.assertEqual(result.get("status"), 0)
        print("测试'failed to search data from mongodb by vid' 方法3 删除时 milvus 不存在数据")
        vid_list = []
        url = _get_module_path("0.png")
        with open(url, "rb") as image:
            base64_data = base64.b64encode(image.read())
        b64 = str(base64_data, encoding="utf-8")
        params = dict(url=url, image=b64)
        res = await image_meta_data_post(params)
        select_result = await db_client.select({})
        vid_list = [item["vid"] for item in select_result]

        selected_vid_list_face = []
        selected_vid_list_sub = []
        selected_vid_list = []
        for item in select_result:
            if item["is_face"] is True:
                selected_vid_list_face.append(int(item["vid"]))
            else:
                selected_vid_list_sub.append(int(item["vid"]))
            selected_vid_list.append(item["vid"])
        delete_sub_result = milvus_client_for_sub.delete_entity_by_id(selected_vid_list_sub)
        delete_face_result = milvus_client_for_face.delete_entity_by_id(selected_vid_list_face)
        print(f"vid_list: {vid_list}")
        result = await delete_meta_data_by_vid(vid_list, milvus_client_for_sub, milvus_client_for_face, db_client)
        self.assertEqual(result.get("status"), 0)


