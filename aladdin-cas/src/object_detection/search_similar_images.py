import traceback

import numpy as np
from exception_handler import InternalErrorException, ParamsException
from PIL import Image

import face_recognition as fr
from object_detection.embedding_and_save import (classify_net_by_tfserving,
                                                 detection_net_by_tfserving)
from object_detection.math_func import fake_nms, softmax, get_iou_by_min
from object_detection.util import clip_sub_image, support_collection, choose_partition

def check_face_or_sub(face_box, image_box):
    # sub_type = image_box[-1]


    face_left = face_box[-1]
    face_top = face_box[0]
    face_right = face_box[1]
    face_bottom = face_box[2]
    
    sub_left = image_box[0]
    sub_top = image_box[1]
    sub_right = image_box[2]
    sub_bottom = image_box[3]

    improve_iou = get_iou_by_min((face_left, face_top, face_right, face_bottom), (sub_left, sub_top, sub_right, sub_bottom))
    if improve_iou > 0.82:
        return "face"
    else:
        return "sub"

def post_process_result(old_list, offset, limit):
    url_list = de_duplication_old_result(old_list)
    page_url_list = get_offset_limit_list(offset, limit, url_list)
    result = dict(offset=offset, limit=limit, count=len(page_url_list), similar_image_list=page_url_list)
    return result


def de_duplication_old_result(old_list):
    similar_url_dict = dict()
    for item in old_list:
        vid = item["vid"]
        url = item["url"]
        if url not in similar_url_dict.keys():
            similar_url_dict[url] = 1
    return list(similar_url_dict.keys())

def get_offset_limit_list(offset, limit, url_list):
    return url_list[offset:offset+limit]

async def search_by_url(search_params, sub_milvus, face_mlivus, dbclient):
    try:
        url = str(search_params["url"])
        offset = int(search_params["offset"])
        limit = int(search_params["limit"])
        top_k = offset + limit * 2
        meta_data_list = await dbclient.select_sorted({"url": url}, "areas")
        len_of_meta_data = len(meta_data_list)
        # 如果url搜索不到则报错
        if len_of_meta_data == 0:
            cause = "failed to search data from mongodb"
            error_detail = {
                "error": f"the url entered is not in the metadata. Please confirm that the url is entered correctly"
            }
            raise InternalErrorException(cause=cause, detail=error_detail, error_code="001")
        meta_data = meta_data_list[0]
        if "is_face" in meta_data.keys() and meta_data.get("is_face","") is True:
            milvus_id = int(meta_data["vid"])
            result = await face_mlivus.get_vector_by_id([milvus_id])
            if result.code != 0:
                cause = "failed to get vector from face_mlivus"
                error_detail = {
                    "traceback": result["details"],
                    "error": result["message"]
                }
                raise InternalErrorException(
                    cause=cause, detail=error_detail, error_code="000")
            vector = result.vec
            if len(vector) == 0:
                cause = "failed to search data from mongodb"
                error_detail = {
                    "error": f"the url entered is not in the metadata. Please confirm that the url is entered correctly"
                }
                raise InternalErrorException(
                    cause=cause, detail=error_detail, error_code="001")
            vector = np.array(vector).reshape((1, -1)).astype(np.float32)
            search_milvus_id_list = None
            result = await face_mlivus.search(top_k=top_k, partition_list=None, vec=vector)
            if result["status"] == 1:
                cause = "failed to search vector from face_mlivus"
                error_detail = {
                    "traceback": traceback.format_exc(),
                    "error": result["message"]
                }
                raise InternalErrorException(
                    cause=cause, detail=error_detail, error_code="000")

            search_milvus_id_list = result["message"]
            if len(search_milvus_id_list) == 0:return []
            similar_milvus_id_list, dis_list = search_milvus_id_list._id_array[
                0], search_milvus_id_list._dis_array[0]
            search_result_list = None
            truncate_similar_milvus_id_list = [str(milvus_id) for milvus_id in similar_milvus_id_list]
            result = await dbclient.select({"vid": {"$in": truncate_similar_milvus_id_list}})
            # todo 查看mongodb中不存在
            search_result_list = result



            for item in search_result_list:
                del item["_id"]
                del item["areas"]
                vid = item["vid"]
                item["distance"] = dis_list[truncate_similar_milvus_id_list.index(
                    vid)]
            rule_list = dict(zip(truncate_similar_milvus_id_list, range(len(truncate_similar_milvus_id_list))))
            return_result_list = sorted(
                search_result_list, key=lambda elem: rule_list[elem["vid"]])
            return_url_dict = post_process_result(return_result_list, offset, limit)
            del return_result_list   
            return_url_dict["is_face"] = True         
            return return_url_dict



        else:
            partition_list = meta_data["top_10_partition"]
            partition_list = [str(i) for i in partition_list]
            milvus_id = int(meta_data["vid"])
            result = await sub_milvus.get_vector_by_id([milvus_id])
            if result.code != 0:
                cause = "failed to get vector from sub_milvus"
                error_detail = {
                    "traceback": result["details"],
                    "error": result["message"]
                }
                raise InternalErrorException(
                    cause=cause, detail=error_detail, error_code="000")
            vector = result.vec
            if len(vector) == 0:
                cause = "failed to search data from mongodb"
                error_detail = {
                    "error": f"the url entered is not in the metadata. Please confirm that the url is entered correctly"
                }
                raise InternalErrorException(
                    cause=cause, detail=error_detail, error_code="001")
            vector = np.array(vector).reshape((1, -1)).astype(np.float32)
            search_milvus_id_list = None
            result = await sub_milvus.search(top_k=top_k, partition_list=partition_list, vec=vector)
            if result["status"] == 1:
                cause = "failed to search vector from sub_milvus"
                error_detail = {
                    "traceback": traceback.format_exc(),
                    "error": result["message"]
                }
                raise InternalErrorException(
                    cause=cause, detail=error_detail, error_code="000")
            search_milvus_id_list = result["message"]
            if len(search_milvus_id_list) == 0:
                return []
            similar_milvus_id_list, dis_list = search_milvus_id_list._id_array[
                0], search_milvus_id_list._dis_array[0]
            search_result_list = None
            truncate_similar_milvus_id_list = [str(milvus_id) for milvus_id in similar_milvus_id_list]
            result = await dbclient.select({"vid": {"$in": truncate_similar_milvus_id_list}})
            search_result_list = result
            for item in search_result_list:
                del item["_id"]
                del item["top_10_partition"]
                del item["areas"]
                vid = item["vid"]
                item["distance"] = dis_list[truncate_similar_milvus_id_list.index(
                    vid)]
                if "is_face" not in item.keys():
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
            rule_list = dict(zip(truncate_similar_milvus_id_list,
                                range(len(truncate_similar_milvus_id_list))))
            return_result_list = sorted(
                search_result_list, key=lambda elem: rule_list[elem["vid"]])
            return_url_dict = post_process_result(return_result_list, offset, limit)
            del return_result_list   
            return_url_dict["is_face"] = False         
            return return_url_dict
    except BaseException as err:
        raise err
    except Exception as err:
        cause = "failed to search by url"
        error_detail = {
            "traceback": traceback.format_exc(),
        }
        raise InternalErrorException(cause=cause, detail=error_detail, error_code="000")        


async def search_by_b64(search_params, sub_milvus, face_milvus, dbclient):
    try:
        offset = int(search_params["offset"])
        limit = int(search_params["limit"])
        top_k = offset + limit * 2
        channel_last_rgb_array = search_params["rgb_array_channel_last"]
        channel_last_rgb_array_resize = search_params["rgb_array_channel_last_resize"]
        rows = search_params["rows"]
        cols = search_params["cols"]
        full_area = rows * cols
        locations = fr.face_locations(channel_last_rgb_array)
        # 进行目标检测
        origin_coordinate_list = await detection_net_by_tfserving(channel_last_rgb_array_resize, rows, cols)
        # 使用nms对bbox进行筛选
        origin_coordinate_list = fake_nms(origin_coordinate_list)
        # 找到最大的人脸
        new_face_box_list = []
        max_face_area = 0.0
        max_face_id = 0
        for face_box_id in range(len(locations)):
            box = locations[face_box_id]
            top = int(box[0])
            right = int(box[1])
            bottom = int(box[2])
            left = int(box[3])
            area = ((bottom - top) * (right - left)) * 1.0 / (rows * cols)
            if area > max_face_area:
                max_face_id = face_box_id
                max_face_area = area
        # face locations 可能为空
        if len(locations) == 0:
            max_face_box = None  
        else:  
            max_face_box = locations[max_face_id]
        # 找到最大的子图
        max_sub_area = 0.0
        max_sub_index = 0
        for sub_box_id in range(len(origin_coordinate_list)):
            box = origin_coordinate_list[sub_box_id]
            left = int(box[0])
            top = int(box[1])
            right = int(box[2])
            bottom = int(box[3])
            area = ((bottom - top) * (right - left)) * 1.0 / (rows * cols)
            if area > max_sub_area:
                max_sub_index = sub_box_id
                max_sub_area = area
        max_sub_box = origin_coordinate_list[max_sub_index]
        max_area_type = None
        max_area_box = None
        max_area = None
        if len(locations) != 0 and len(origin_coordinate_list) != 0:
            max_area_type, max_area_box, max_area = None, None, None
            if max_sub_area < max_face_area:
                max_area_type, max_area_box, max_area = "face", locations[max_face_id], max_face_area
            else:
                if check_face_or_sub(max_face_box, max_sub_box) == "face":
                    max_area_type, max_area_box, max_area = "face", locations[max_face_id], max_face_area
                else:
                    max_area_type, max_area_box, max_area = "sub", origin_coordinate_list[max_sub_index], max_sub_area

            # max_area_type, max_area_box, max_area = ("sub", origin_coordinate_list[max_sub_index], max_sub_area) if max_sub_area > max_face_area else ("face", locations[max_face_id], max_face_area)
        elif len(locations) == 0 and len(origin_coordinate_list) != 0:
            max_area_type = "sub"
            max_area_box = origin_coordinate_list[max_sub_index]
            max_area = max_sub_area
        elif len(locations) != 0 and len(origin_coordinate_list) == 0:
            max_area_type = "face"
            max_area_box = locations[max_face_id]
            max_area = max_face_area
        else:
            max_area_type = "sub"
            max_area_box = (0, 0, cols, rows)
            max_area = full_area
        if max_area_type == "sub":
            channel_last_sub_image = clip_sub_image(
                channel_last_rgb_array, (left, top, right, bottom))
            cls_result = await classify_net_by_tfserving(channel_last_sub_image)
            vecs = cls_result["hash_vector"]
            partition_list = choose_partition(vecs)
            partition_list = partition_list[:10]
            partition_list = [str(i) for i in partition_list]
            search_result_list = []
            result = await sub_milvus.search(top_k=top_k, partition_list=partition_list, vec=vecs)
            if result["status"] == 1:
                cause = "failed to search vector from milvus"
                error_detail = {
                    "traceback": result["details"],
                    "error": result["message"]
                }
                raise InternalErrorException(
                    cause=cause, detail=error_detail, error_code="000")
            search_result_list = result["message"]
            # 如果base64编码所在的10个partition没有相似数据，则返回空
            if len(search_result_list) == 0:
                return []
            similar_milvus_id_list, dis_list = search_result_list._id_array[0], search_result_list._dis_array[0]
            search_result_list = None
            transform_similar_milvus_id_list = [
                str(milvus_id) for milvus_id in similar_milvus_id_list]
            result = await dbclient.select({"vid": {"$in": transform_similar_milvus_id_list}})
            dis_list = np.array(dis_list)
            search_mongodb_list = []
            # todo 检测mongodb
            search_result_list = result
            for item in search_result_list:
                del item["_id"]
                del item["top_10_partition"]
                del item["areas"]
                vid = item["vid"]
                item["distance"] = dis_list[transform_similar_milvus_id_list.index(vid)]
                if "is_face" not in item.keys():
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
            rule_list = dict(zip(transform_similar_milvus_id_list,
                                range(len(transform_similar_milvus_id_list))))
            return_result_list = sorted(
                search_result_list, key=lambda elem: rule_list[elem["vid"]])
            return_url_dict = post_process_result(return_result_list, offset, limit)
            del return_result_list
            return_url_dict["is_face"] = False
            return return_url_dict
        else:
            encodings = fr.face_encodings(channel_last_rgb_array, known_face_locations=[
                                        locations[max_face_id]])
            vecs = np.array(encodings)
            search_result_list = []
            result = await face_milvus.search(top_k=top_k, partition_list=None, vec=vecs)
            if result["status"] == 1:
                cause = "failed to search vector from milvus"
                error_detail = {
                    "traceback": result["details"],
                    "error": result["message"]
                }
                raise InternalErrorException(
                    cause=cause, detail=error_detail, error_code="000")
            search_result_list = result["message"]
            if len(search_result_list) == 0:
                return []
            similar_milvus_id_list, dis_list = search_result_list._id_array[
                0], search_result_list._dis_array[0]
            search_result_list = None
            transform_similar_milvus_id_list = [
                str(milvus_id) for milvus_id in similar_milvus_id_list]
            result = await dbclient.select({"vid": {"$in": transform_similar_milvus_id_list}})
            dis_list = np.array(dis_list)
            search_mongodb_list = []
            search_result_list = result
            for item in search_result_list:
                del item["_id"]
                del item["areas"]
                vid = item["vid"]
                item["distance"] = dis_list[transform_similar_milvus_id_list.index(vid)]
            rule_list = dict(zip(transform_similar_milvus_id_list,
                                range(len(transform_similar_milvus_id_list))))
            return_result_list = sorted(
                search_result_list, key=lambda elem: rule_list[elem["vid"]])
            return_url_dict = post_process_result(return_result_list, offset, limit)
            del return_result_list
            return_url_dict["is_face"] = True      
            return return_url_dict

    except InternalErrorException as err:
        raise err
    except Exception as err:
        cause = "failed search by base64"
        error_detail = {
            "traceback": traceback.format_exc(),
            "error": repr(err)
        }
        raise InternalErrorException(
            cause=cause, detail=error_detail, error_code="000")
async def search_by_vid(search_params, sub_milvus, face_milvus, dbclient):
    try:
        milvus_id = int(search_params["vid"])
        offset = int(search_params["offset"])
        limit = int(search_params["limit"])
        top_k = offset + limit * 2
        meta_data = None
        result = await dbclient.select({"vid": str(milvus_id)})
        if len(result) == 0:
            cause = "failed to search data from mongodb"
            error_detail = {
                "error": f"the vid entered is not in the metadata. Please confirm that the vid is entered correctly"
            }
            raise InternalErrorException(
                cause=cause, detail=error_detail, error_code="001")
        meta_data = result[0]
        if "is_face" in meta_data.keys() and meta_data.get("is_face", "") is True:
            vector = None
            result = await face_milvus.get_vector_by_id([milvus_id])
            if result.code != 0:
                cause = "failed to get vector from face_milvus"
                error_detail = {
                    "traceback": result["details"],
                    "error": result["message"]
                }
                raise InternalErrorException(
                    cause=cause, detail=error_detail, error_code="000")
            vector = result.vec
            if len(vector) == 0:
                cause = "failed to search data from mongodb"
                error_detail = {
                    "error": f"the url entered is not in the metadata. Please confirm that the url is entered correctly"
                }
                raise InternalErrorException(
                    cause=cause, detail=error_detail, error_code="001")
            vector = np.array(vector).reshape((1, -1)).astype(np.float32)
            search_result_list = []
            result = await face_milvus.search(top_k=top_k, partition_list=None, vec=vector)
            if result["status"] == 1:
                cause = "failed to search vector from face_milvus"
                error_detail = {
                    "traceback": traceback.format_exc(),
                    "error": result["message"]
                }
                raise InternalErrorException(
                    cause=cause, detail=error_detail, error_code="000")
            search_result_list = result["message"]
            if len(search_result_list) == 0:
                return []
            similar_milvus_id_list, dis_list = search_result_list._id_array[
                0], search_result_list._dis_array[0]
            search_result_list = None
            truncate_similar_milvus_id_list = [
                str(milvus_id) for milvus_id in similar_milvus_id_list]
            result = await dbclient.select({"vid": {"$in": truncate_similar_milvus_id_list}})
            search_result_list = result
            for item in search_result_list:
                del item["_id"]
                del item["areas"]
                vid = item["vid"]
                item["distance"] = dis_list[truncate_similar_milvus_id_list.index(
                    vid)]
            rule_list = dict(zip(truncate_similar_milvus_id_list,
                                range(len(truncate_similar_milvus_id_list))))
            return_result_list = sorted(
                search_result_list, key=lambda elem: rule_list[elem["vid"]])
            return_url_dict = post_process_result(return_result_list, offset, limit)
            del return_result_list
            return_url_dict["is_face"] = True       
            return return_url_dict
        else:
            vector = None
            result = await sub_milvus.get_vector_by_id([milvus_id])
            if result.code != 0:
                cause = "failed to get vector from sub_milvus"
                error_detail = {
                    "traceback": result["details"],
                    "error": result["message"]
                }
                raise InternalErrorException(
                    cause=cause, detail=error_detail, error_code="000")
            vector = result.vec
            if len(vector) == 0:
                cause = "failed to search data from mongodb"
                error_detail = {
                    "error": f"the url entered is not in the metadata. Please confirm that the url is entered correctly"
                }
                raise InternalErrorException(
                    cause=cause, detail=error_detail, error_code="001")
            vector = np.array(vector).reshape((1, -1)).astype(np.float32)
            search_result_list = []
            partition_list = [str(i) for i in meta_data["top_10_partition"]]
            result = await sub_milvus.search(top_k=top_k, partition_list=partition_list, vec=vector)
            if result["status"] == 1:
                cause = "failed to search vector from sub_milvus"
                error_detail = {
                    "traceback": traceback.format_exc(),
                    "error": result["message"]
                }
                raise InternalErrorException(
                    cause=cause, detail=error_detail, error_code="000")
            search_result_list = result["message"]
            if len(search_result_list) == 0:
                return []
            similar_milvus_id_list, dis_list = search_result_list._id_array[0], search_result_list._dis_array[0]
            search_result_list = None
            truncate_similar_milvus_id_list = [str(milvus_id) for milvus_id in similar_milvus_id_list]
            result = await dbclient.select({"vid": {"$in": truncate_similar_milvus_id_list}})
            search_result_list = result
            for item in search_result_list:
                del item["_id"]
                del item["top_10_partition"]
                del item["areas"]
                vid = item["vid"]
                item["distance"] = dis_list[truncate_similar_milvus_id_list.index(
                    vid)]
                if "is_face" not in item.keys():
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
            rule_list = dict(zip(truncate_similar_milvus_id_list,
                                range(len(truncate_similar_milvus_id_list))))
            return_result_list = sorted(
                search_result_list, key=lambda elem: rule_list[elem["vid"]])
            return_url_dict = post_process_result(return_result_list, offset, limit)
            del return_result_list
            return_url_dict["is_face"] = False
            return return_url_dict
    except InternalErrorException as err:
        raise err
    except Exception as err:
        cause = "failed search by vid"
        error_detail = {
            "traceback": traceback.format_exc(),
            "error": repr(err)
        }
        raise InternalErrorException(
            cause=cause, detail=error_detail, error_code="000")

async def search_similar_images(search_params, sub_milvus, face_milvus, dbclient):
    similar_image_list = []
    if search_params["flag"] == 0:
        try:
            similar_image_result = await search_by_url(search_params, sub_milvus, face_milvus, dbclient)
        except Exception as err:
            raise err
        return similar_image_result
    elif search_params["flag"] == 1:
        try:
            similar_image_result = await search_by_b64(search_params, sub_milvus, face_milvus, dbclient)

        except Exception as err:
            raise err
        return similar_image_result
    elif search_params["flag"] == 2:
        try:
            similar_image_result = await search_by_vid(search_params, sub_milvus, face_milvus, dbclient)
        except Exception as err:
            raise err
        return similar_image_result
