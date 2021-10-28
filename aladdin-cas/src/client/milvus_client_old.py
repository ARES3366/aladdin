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
    def __init__(self, client, loop, collection_list):
        self.client = client
        self.request_queue = Queue(maxsize=1000)
        self.collection_list = collection_list
        self.colletion_count = len(self.collection_list)
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
        collection_name = item["collection_name"]
        return MilvusResult(code=status.code, message=status.message, vec=vec, collection_name=collection_name)

    async def _batch_request(self,item_list):
        def arrange_item_list(collection_name, item_list):
            ids = []
            index_list = []
            for item_index in range(len(item_list)):
                item = item_list[item_index]
                if item["collection_name"] == collection_name:
                    ids.append(item)
                    index_list.append(item)
            return ids, index_list
        if len(item_list) == 0: return
        for collection_name in self.collection_list:
            ids, index_list = arrange_item_list(item_list, collection_name)
            N = len(ids)
            status, vector_list = self.client.get_entity_by_id(collection_name=collection_name, ids=ids)
            for i in range(N):
                index = index_list[i]
                item = item_list[index]
                item['status'] = status
                if status.code==0:
                    item['vec'] = vector_list[i]
        # print(item_list)

#根据向量查询相似向量
# class AioMilvusSearch(AioMilvusBase):
#     def _process_response(self, item):
#         statu0= item['status']
#         id_list = item['id_list']
#         dis_list = item['dis_list']
#         collecton_name = item["collection_name"]
#         return MilvusResult(code=status.code, message=status.message, id_list=id_list,dis_list=dis_list)

#     async def _batch_request(self,all_item_list):
#         def arrange_item_list(collection_name, item_list):
#             part_item_list = []
#             index_list = []
#             for item_index in range(len(item_list)):
#                 item = item_list[item_index]
#                 if item["collection_name"] == collection_name:
#                     part_item_list.append(item)
#                     index_list.append(item_index)
#             return part_item_list, index_list
#         for collection_name in self.collection_list:
#             item_list, index_list = arrange_item_list(collection_name, all_item_list)

#             N = len(item_list)
#             if N == 0: return
#             item_list.sort(key=lambda x: x['top_k'])
#             vec_list = [item['vec'] for item in item_list]
#             topk_list = [item['top_k'] for item in item_list]
#             idx_list = [i for i in range(N)]
#             def deal_topk(k):
#                 for i in range(3,10):
#                     U=2**i
#                     if k<U: return U
#                 return 1000
            
#             topk_list = [deal_topk(k) for k in topk_list]
#             cluster_vec = defaultdict(list)
#             cluster_idx = defaultdict(list)
#             for k,v in zip(topk_list,vec_list): cluster_vec[k].append(v)
#             for k,i in zip(topk_list,idx_list): cluster_idx[k].append(i)
#             async def task(top_k):
#                 query_records=cluster_vec[top_k]
#                 _idx_list = cluster_idx[top_k]
#                 feature = self.client.search(collection_name=collection_name, top_k=top_k,query_records=np.concatenate(query_records, axis=0), params={'ef':2*top_k}, _async=True)
#                 while not feature._done: await asyncio.sleep(0.1)
#                 status, res = feature.result()
#                 for i in range(len(_idx_list)):
#                     idx = _idx_list[i]
#                     item = item_list[index_list[idx]]
#                     item['status'] = status
#                     if status.code==0:
#                         item['id_list'] = res[i]._id_list
#                         item['dis_list'] = res[i]._dis_list
#             tasks = [task(top_k) for top_k  in cluster_vec.keys()]
#             asyncio.run_coroutine_threadsafe(asyncio.wait(tasks), loop=self.__loop)

@singleton
class AioMilvus():
    def __init__(self, loop, collection_list):
        self.collection_list = collection_list  # [object_detection, face_recognition]
        self.milvus = Milvus(**milvus_config)
        self.__loop = loop
        self.aio_milvus_query = AioMilvusQuery(client=self.milvus, loop=self.__loop, collection_list=collection_list)
        # self.aio_milvus_search = AioMilvusSearch(client=self.milvus, loop=self.__loop, collection_list=collection_list)
        asyncio.run_coroutine_threadsafe(self.aio_milvus_query.main_loop(), loop=self.__loop)
        # asyncio.run_coroutine_threadsafe(self.aio_milvus_search.main_loop(), loop=self.__loop)
        
        
    async def get_vector_by_id(self, collection_name, vid):
        return await self.aio_milvus_query.async_request(vid=vid[0], collection_name=collection_name)

    async def search(self, collection_name, top_k, partition_list, vec):
        feature = self.milvus.search(collection_name=collection_name, partition_tags=partition_list, query_records=vec, top_k=top_k, params={'nprobe': 20}, _async=True, timeout=3000)
        if not feature._done is True: await asyncio.sleep(0.5)
        status, result = feature.result()
        if status.OK():
            return dict(status=0, message=result)
        else:
            return dict(status=1, message=status.message, details=traceback.format_exc()) # 001
            
    def sync_get_vector_by_id(self, collection_name, vid):
        result = self.milvus.get_entity_by_id(collection_name, vid)

    async def get_entity_by_id(self, collection_name, vid):
        status, vector_list = self.milvus.get_entity_by_id(collection_name, [int(vid)])
        if status.OK():
            return dict(status=0, message=vector_list[0])
            # return dict(status=0, message=vector_list)  # 返回向量的list，二维数组

        else:
            return dict(status=1, message=status.message, details=traceback.format_exc()) # 001
            
    def insert(self,collection_name, vectors, partition_tag):
        status, ok = self.milvus.has_collection(collection_name)
        if ok:
            status, ids = self.milvus.insert(
                collection_name=collection_name, records=vectors, partition_tag=partition_tag)
            if not status.OK():
                return dict(status=1, message=status.message, details=traceback.format_exc()) # 001
            else:
                return dict(status=0, message=ids)

        else:
            return dict(status=1, message="collection has not been created", details=traceback.format_exc()) # 001
    
    def flush(self, collection_name):
        status = self.milvus.flush([collection_name])
        if status.OK():
            return dict(status=0, message="flush success")
        else:
            return dict(status=1, message="flush failed", details=traceback.format_exc()) # 001
    def list_partition(self, collection_name):
        status, partition_list = self.milvus.list_partitions(collection_name)
        if status.OK(): 
            return dict(status=0, message=partition_list)
        else:
            return dict(status=1, message=status.message, details=traceback.format_exc())
    def has_collection(self, collection_name):
        return self.milvus.has_collection(collection_name)

    def list_id_in_segment(self, collection_name, segment_name):
        return self.milvus.list_id_in_segment(collection_name=collection_name, segment_name=segment_name)

    def get_collection_stats(self, collection_name):
        status, collection_stats = self.milvus.get_collection_stats(collection_name)
        if status.OK():
            return dict(status=0, message=collection_stats)
        else:
            return dict(status=1, message=status.message, details=traceback.format_exc()) # 001
    def delete_entity_by_id(self, collection_name, milvus_id_list):
        print(f"milvus_id_list: {milvus_id_list}")
        if len(milvus_id_list) == 0:
            return dict(status=1, message="no milvus_id belong to this url", details=traceback.format_exc()) # 001
        status = self.milvus.delete_entity_by_id(collection_name, milvus_id_list, timeout=10)
        if status.OK():
            return dict(status=0, message="success delete")
        else:
            return dict(status=1, message=status.message, details=traceback.format_exc()) # 001

    def count_entities(self, collection_name):
        _, result = self.milvus.count_entities(collection_name)
        print(f"有向量 {result} 条")

if __name__ == "__main__":
    milvus = AioMilvus(loop=asyncio.get_event_loop(), collection_list=["1","2"])
    print(milvus)