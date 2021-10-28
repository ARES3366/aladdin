from object_detection.embedding_and_save import sub_image_embedding_and_save
from object_detection.search_similar_images import search_similar_images
from object_detection.update_meta_data import update_meta_data_label
from object_detection.util import (check_search_params,
                                   delete_data_check, delete_data_handler,
                                   get_data_check, get_data_handler,
                                   post_data_check, post_data_handler,
                                   update_data_check, update_data_handler)
from object_detection.face_recognitions import face_image_embedding_and_save
from object_detection.delete_meta_info import delete_meta_data_by_vid, delete_meta_data_by_url
from exception_handler import ParamsException, InternalErrorException, BasicException
from client.milvus_client import AioMilvus
from db_adapter.mongo_adapter import MongoDBClient
from read_config import milvus_config
import asyncio
import traceback
from utils import singleton


sub_vector_collection_name = "object_detection"
face_vector_collection_name = "face_recognition"

async def check_exist(url, milvus_client_for_sub, milvus_client_for_face, dbclient):
    condition = {"url": str(url)}
    select_result = await dbclient.select(condition)
    if len(select_result) > 0:
        try:
            delete_result = await delete_meta_data_by_url([url], milvus_client_for_sub, milvus_client_for_face, dbclient)
        except BasicException as err:
            raise err
        except Exception as err:
            raise InternalErrorException(cause= "failed to clean repeated data", detail={"traceback": traceback.format_exc(),"error": repr(err)}, error_code="000")
    else:
        return


async def aggregate_sub_and_face(sub_meta_info_list, face_meta_info_list, db_client):
    '''
    # 整合子图和人脸的元数据
    '''
    aggregation_meta_info_list = sub_meta_info_list + face_meta_info_list
    insert_result = await db_client.insert_many(aggregation_meta_info_list)
    if insert_result["status"] == 1:
        raise InternalErrorException(cause=insert_result["message"], detail={"traceback": traceback.format_exc(),"error": repr(err)}, error_code="000")


async def image_meta_data_post(input_params):
    try:
        post_data_check(input_params)
        handled_params = post_data_handler(input_params)        
        milvus_client_for_sub = AioMilvus(sub_vector_collection_name, asyncio.get_event_loop())
        milvus_client_for_face = AioMilvus(face_vector_collection_name,asyncio.get_event_loop())
        db_client = MongoDBClient()
        await check_exist(handled_params["url"], milvus_client_for_sub, milvus_client_for_face, db_client)
        sub_meta_info_list = await sub_image_embedding_and_save(handled_params, milvus_client_for_sub)
        face_meta_info_list = await face_image_embedding_and_save(handled_params, milvus_client_for_face)
        await aggregate_sub_and_face(sub_meta_info_list, face_meta_info_list, db_client) 
    except BasicException as err:
        raise err
    except Exception as err:
        raise InternalErrorException(
            cause= "failed to insert meta data", detail={"traceback": traceback.format_exc(),"error": repr(err)}, error_code="000")
    return dict(code=200, message="post success")


async def image_meta_data_get(input_params):
    try:
        types = get_data_check(input_params)    #检查参数
        input_data = get_data_handler(input_params, types) #格式化参数
        dbclient = MongoDBClient()  #创建数据库连接
        result = await dbclient.select(input_data)  #从数据库中搜索查询的内容，如果url不在mongodb中，则mongodb返回空列表(未采用)
        len_of_meta_data = len(result)  #获取数据库的长度
        # 如果url 不存在，则报500001
        if len_of_meta_data == 0:
            raise InternalErrorException(
                cause="failed to search data from mongodb",
                detail=f"the {types} entered is not in the metadata. Please confirm that the {types} is entered correctly",
                error_code="001")
        for item in result:
            if "is_face" in item.keys():
                del item["_id"]
                del item["areas"]
                if item["is_face"] is False:
                    del item["top_10_partition"]
            else:
                del item["_id"]
                del item["areas"]
                classify = item["classify"]
                del item["classify"]
                new_ex = {
                    "label_1":classify["classify_name_1"],
                    "label_2":classify["classify_name_2"],
                    "label_3":classify["classify_name_3"],
                    "label_4":classify["classify_name_4"],
                    "label_5":classify["classify_name_5"],
                    "confidence_1":classify["classify_confidence_1"],
                    "confidence_2":classify["classify_confidence_2"],
                    "confidence_3":classify["classify_confidence_3"],
                    "confidence_4":classify["classify_confidence_4"],
                    "confidence_5":classify["classify_confidence_5"],
                    "is_face":False,
                    "extension":{}

                }
                item.update(new_ex)
                del item["top_10_partition"]
    except BasicException as err:
        raise err
    except Exception as err:
        raise InternalErrorException(cause= "failed to get image meta data", detail={"traceback": traceback.format_exc(),"error": repr(err)}, error_code="000")
    return dict(code=200, message="getsuccess", image_meta_data_list=result)



async def image_meta_data_delete(input_params, types):
    try:
        delete_data_check(input_params, types)
        input_data = delete_data_handler(input_params, types)
        milvus_client_for_sub = AioMilvus(sub_vector_collection_name, asyncio.get_event_loop())
        milvus_client_for_face = AioMilvus(face_vector_collection_name, asyncio.get_event_loop())
        dbclient = MongoDBClient()
        delete_result = None
        if types == "vid":
            delete_result = await delete_meta_data_by_vid(input_data, milvus_client_for_sub, milvus_client_for_face, dbclient)
        if types == "url":
            delete_result = await delete_meta_data_by_url(input_data, milvus_client_for_sub, milvus_client_for_face, dbclient)
    except BasicException as err:
        raise err
    except Exception as err:
        raise InternalErrorException(
            cause="failed to delete meta data", detail={"traceback": traceback.format_exc(),"error": repr(err)}, error_code="000")
    return dict(code=200, message="success")


async def image_meta_data_put(input_params):
    try:
        update_data_check(input_params)
        input_data = update_data_handler(input_params)
        dbclient = MongoDBClient()
        await update_meta_data_label(input_data, dbclient)
    except BasicException as err:
        raise err
    except Exception as err:
        raise InternalErrorException(cause="failed to insert meta data", detail={"traceback": traceback.format_exc(),"error": repr(err)}, error_code="000")
    return dict(code=200, message="put success")


async def similar_image_search_post(query_params, body_params):
    try:
        checked_search_dict = check_search_params(query_params, body_params)
        milvus_client_for_sub = AioMilvus(sub_vector_collection_name, asyncio.get_event_loop())
        milvus_client_for_face = AioMilvus(face_vector_collection_name, asyncio.get_event_loop())
        dbclient = MongoDBClient()
        similar_pic_meta_data = await search_similar_images(checked_search_dict, milvus_client_for_sub, milvus_client_for_face, dbclient)
    except BasicException as err:
        raise err
    except Exception as err:
        raise InternalErrorException(
            cause="failed to search images", detail={"traceback": traceback.format_exc(),"error": repr(err)}, error_code="000")
    return similar_pic_meta_data
