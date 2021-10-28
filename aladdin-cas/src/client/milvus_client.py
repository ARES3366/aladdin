from milvus import Milvus
from read_config import milvus_config
from collections import defaultdict
from queue import Queue
import asyncio
import numpy as np
import traceback
from utils import singleton, newsingleton
class MilvusResult():
    def __init__(self, code=0, message='OK', **results):
        self.code = code
        self.message = message
        self.__results = results

    def __str__(self):
        return str(self.__dict__)

    def __getattr__(self, name):
        if name in self.__results: return self.__results[name]
        else: return None

class AioMilvusBase():
    def __init__(self, collection_name, client, loop):
        self.collection_name = collection_name
        self.client = client
        self.request_queue = Queue(maxsize=1000)
        self.__loop = loop
    async def async_request(self, **item):
        q = self.request_queue
        while q.full(): await asyncio.sleep(1e-3)
        q.put(item)
        while True:
            await asyncio.sleep(1e-3)
            if 'status' in item:
                return self._process_response(item)

    def _process_response(self,item):
        status = item['status']
        return MilvusResult(code=status.code, message=status.message)

    async def _batch_request(self,item_list):
        pass

    def __get_all_items_from_queue(self):
        item_list=[]
        q = self.request_queue
        while not q.empty():
            item = q.get(False)
            item_list.append(item)
        return item_list

    async def main_loop(self):
        while True:
            try:
                await asyncio.sleep(1e-1)
                item_list=self.__get_all_items_from_queue()
                await self._batch_request(item_list)
            except Exception as e:
                import traceback
                s = traceback.format_exc()
                print('--------------------------------------',s)
                print('----------------Exception is : ', e)

# 根据向量id查询向量
class AioMilvusQuery(AioMilvusBase):
    def _process_response(self, item):
        '''
        item example:{
          'vid':150000000000,
          'status': status,   #请求成功后存在
          'res': res,         #网络出错时不存在
        }
        '''
        status = item['status']
        vec = item['vec']
        return MilvusResult(code=status.code, message=status.message, vec=vec)

    async def _batch_request(self,item_list):
        if len(item_list) == 0: return
        ids = [item['vid'] for item in item_list]
        N = len(ids)
        status, vector_list = self.client.get_entity_by_id(collection_name=self.collection_name, ids=ids)
        for i in range(N):
            item = item_list[i]
            item['status'] = status
            if status.code==0:
                item['vec'] = vector_list[i]
        # print(item_list)



@newsingleton
class AioMilvus():
    def __init__(self,collection_name, loop):
        self.milvus = Milvus(**milvus_config)
        self.__loop = loop
        self.collection_name = collection_name
        self.aio_milvus_query = AioMilvusQuery(collection_name=collection_name,client=self.milvus, loop=self.__loop)
        asyncio.run_coroutine_threadsafe(self.aio_milvus_query.main_loop(), loop=self.__loop)
        
        
    async def get_vector_by_id(self, vid):
        return await self.aio_milvus_query.async_request(vid=vid[0])

    async def search(self, top_k, partition_list, vec):
        feature = self.milvus.search(collection_name=self.collection_name, partition_tags=partition_list, query_records=vec, top_k=top_k, params={'nprobe': 20}, _async=True, timeout=3000)
        if not feature._done is True: await asyncio.sleep(0.5)
        status, result = feature.result()
        if status.OK():
            return dict(status=0, message=result)
        else:
            return dict(status=1, message=status.message, details=traceback.format_exc()) # 001
            
    def sync_get_vector_by_id(self, vid):
        result = self.milvus.get_entity_by_id(self.collection_name, vid)

    async def get_entity_by_id(self, vid):
        status, vector_list = self.milvus.get_entity_by_id(self.collection_name, [int(vid)])
        if status.OK():
            return dict(status=0, message=vector_list[0])
        else:
            return dict(status=1, message=status.message, details=traceback.format_exc()) # 001
            
    def insert(self, vectors, partition_tag):
        status, ok = self.milvus.has_collection(self.collection_name)
        if ok:
            status, ids = self.milvus.insert(
                collection_name=self.collection_name, records=vectors, partition_tag=partition_tag)
            if not status.OK():
                return dict(status=1, message=status.message, details=traceback.format_exc()) # 001
            else:
                return dict(status=0, message=ids)
        else:
            return dict(status=1, message="collection has not been created", details=traceback.format_exc()) # 001
    
    def flush(self):
        status = self.milvus.flush([self.collection_name])
        if status.OK():
            return dict(status=0, message="flush success")
        else:
            return dict(status=1, message="flush failed", details=traceback.format_exc()) # 001
    def list_partition(self):
        status, partition_list = self.milvus.list_partitions(
            self.collection_name)
        if status.OK():
            return dict(status=0, message=partition_list)
        else:
            return dict(status=1, message=status.message, details=traceback.format_exc())
    def has_collection(self):
        return self.milvus.has_collection(self.collection_name)

    def list_id_in_segment(self, segment_name):
        return self.milvus.list_id_in_segment(collection_name=self.collection_name, segment_name=segment_name)

    def get_collection_stats(self):
        status, collection_stats = self.milvus.get_collection_stats(
            self.collection_name)
        if status.OK():
            return dict(status=0, message=collection_stats)
        else:
            return dict(status=1, message=status.message, details=traceback.format_exc()) # 001
    def delete_entity_by_id(self, milvus_id_list):
        if len(milvus_id_list) == 0:
            return dict(status=1, message="no milvus_id belong to this url") # 001
        status = self.milvus.delete_entity_by_id(
            self.collection_name, milvus_id_list, timeout=10)
        if status.OK():
            return dict(status=0, message="success delete")
        else:
            return dict(status=1, message=status.message, details=traceback.format_exc()) # 001

    def count_entities(self):
        _, result = self.milvus.count_entities(self.collection_name)
        print(f"有向量 {result} 条")
