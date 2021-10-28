import logging
import sys
import time
import traceback

import numpy as np

from client.tfs_client import BaseClient
from exception_handler import InternalErrorException, ParamsException
from protos.tensorflow.core.framework import types_pb2
from read_config import classify_model_name, detection_confidence_threshold, detection_model_name
from object_detection.math_func import fake_nms, softmax, hashtrick
from object_detection.util import class_dict, clip_sub_image, preprocess_for_fbnet, support_collection, choose_partition


def get_label(index):
    item_class = class_dict[str(index)]
    main_class = item_class["cn_main_class"]
    sub_class = item_class["cn_class_name"]
    if main_class in sub_class:
        return str(sub_class)
    else:
        return str(main_class)+"-"+str(sub_class)

def get_label(index):
    item_class = class_dict[str(index)]
    main_class = item_class["cn_main_class"]
    sub_class = item_class["cn_class_name"]
    if main_class in sub_class:
        return str(sub_class)
    else:
        return str(main_class)+"-"+str(sub_class)

async def format_classify_result(topk, feature_vector, class_vector):
    try:
        feature_vector = np.reshape(feature_vector, (1, -1))
        hashed_feature_vector = hashtrick(feature_vector, 128)
        class_vector = softmax(class_vector)
        top_5_index = np.argsort(-class_vector, axis=-1,
                                 kind='quicksort')[:, :5].tolist()[0]
        top_5_confidence = class_vector[:, top_5_index].tolist()[0]
        classify_result = {
            "label_1": get_label(top_5_index[0]),
            "label_2": get_label(top_5_index[1]),
            "label_3": get_label(top_5_index[2]),
            "label_4": get_label(top_5_index[3]),
            "label_5": get_label(top_5_index[4]),
            "confidence_1": float(top_5_confidence[0]),
            "confidence_2": float(top_5_confidence[1]),
            "confidence_3": float(top_5_confidence[2]),
            "confidence_4": float(top_5_confidence[3]),
            "confidence_5": float(top_5_confidence[4]),
            "hash_vector": hashed_feature_vector
        }
        return classify_result
    except Exception as err:
        cause = "Error in formatting classification result"
        error_detail = {
            "traceback": traceback.format_exc(),
            "error": repr(err)
        }
        raise InternalErrorException(
            cause=cause, detail=error_detail, error_code="000")
    finally:
        del feature_vector, hashed_feature_vector, class_vector, top_5_index, top_5_confidence


async def save_milvus(vector, milvus):
    try:
        orderd_partition_list = choose_partition(vector)
    except Exception as err:
        cause = "failed to choose partition"
        error_detail = {
            "traceback": traceback.format_exc(),
            "error": repr(err)
        }
        raise InternalErrorException(
            cause=cause, detail=error_detail, error_code="000")
    top_10_partition = orderd_partition_list[:10]
    top_1_partition = orderd_partition_list[0]
    milvus_id = None
    result = milvus.insert(vector, str(top_1_partition))
    if result.get("status") == 1:
        cause = "failed to insert vector into Milvus"
        error_detail = {
            "traceback": result["details"],
            "error": result["message"]
        }
        raise InternalErrorException(
            cause=cause, detail=error_detail, error_code="000")
    milvus_id = result["message"]
    save_result = {
        "vid": str(milvus_id[0]),
        "top_10_partition": [int(i) for i in top_10_partition]
    }
    return save_result


async def detection_net_by_tfserving(sub_image, rows, cols):

    tfs_client = BaseClient()
    sub_image_tensor = np.expand_dims(sub_image, axis=0)
    input_data = {
        "input_tensor": {
            "data": sub_image_tensor,
            "dtype": types_pb2.DT_FLOAT
        }
    }
    output_list = ["detection_boxes", "detection_scores",
                   "detection_classes", "num_detections"]
    try:
        result = await tfs_client.inference(str(detection_model_name), "serving_default", input_data, output_list)
    except Exception as err:
        cause = f"failed to access the {str(detection_model_name)} model"
        error_detail = {
            "traceback": traceback.format_exc(),
            "error": repr(err)
        }
        raise InternalErrorException(
            cause=cause, detail=error_detail, error_code="000")
    confidence_data = result["detection_scores"]["value"]
    value_data = result["detection_boxes"]["value"]
    class_data = result["detection_classes"]["value"]
    box_list = np.array(value_data)
    confidence_list = np.array(confidence_data).astype(np.float32)
    class_list = np.array(class_data).astype(np.uint32)
    top_list = np.ceil(box_list[range(0, 397, 4)]*rows).astype(np.uint32)
    left_list = np.ceil(box_list[range(1, 398, 4)]*cols).astype(np.uint32)
    bottom_list = np.floor(box_list[range(2, 399, 4)]*rows).astype(np.uint32)
    right_list = np.floor(box_list[range(3, 400, 4)]*cols).astype(np.uint32)
    origin_coordinate_list = []
    for box_item in zip(left_list, top_list, right_list, bottom_list, confidence_list, class_list):
        confidence = box_item[-2]
        if confidence < detection_confidence_threshold:
            break
        origin_coordinate_list.append(box_item)
    # 如果所有bbox的置信度都小于0.5，则只取第一张(未使用)
    # if len(origin_coordinate_list) == 0:
    #     origin_coordinate_list.append(
    #         (left_list[0], top_list[0], right_list[0], bottom_list[0], confidence_list[0], class_list[0]))
    # 如果所有bbox的置信度都小于0.5，则取整张图作为子图
    if len(origin_coordinate_list) == 0:
        origin_coordinate_list.append((0,0,cols, rows, 1.0, -1))
    return origin_coordinate_list


async def classify_net_by_tfserving(sub_image):
    tfs_client = BaseClient()
    sub_image_input_tensor = preprocess_for_fbnet(sub_image)
    input_data = {
        "input": {
            "data": sub_image_input_tensor,
            "dtype": types_pb2.DT_FLOAT
        }
    }
    output_list = ["class", "feature"]
    try:
        result = await tfs_client.inference(str(classify_model_name), "serving_default", input_data, output_list)
    except Exception as err:
        cause = f"failed to access the {str(classify_model_name)} model"
        error_detail = {
            "traceback": traceback.format_exc(),
            "error": repr(err)
        }
        raise InternalErrorException(
            cause=cause, detail=error_detail, error_code="000")

    class_data = result["class"]
    feature_data = result["feature"]
    class_vector = np.array(
        class_data["value"], dtype=np.float32).reshape(class_data["shape"])
    feature_vector = np.array(
        feature_data["value"], dtype=np.float32).reshape(feature_data["shape"])
    # 分类结果
    cls_result = await format_classify_result(5, feature_vector, class_vector)
    del class_data, feature_data, class_vector, feature_vector
    return cls_result


async def sub_image_embedding_and_save(input_data, milvus):
    url = input_data["url"]  # 图片地址
    rows = input_data["rows"]
    cols = input_data["cols"]
    channel_last_rgb_array = input_data["rgb_array_channel_last"]
    channel_last_rgb_array_resize = input_data["rgb_array_channel_last_resize"]
    extension = input_data["extension"]
    origin_coordinate_list = []
    try:
        # 进行目标检测
        origin_coordinate_list = await detection_net_by_tfserving(channel_last_rgb_array_resize, rows, cols)

    except InternalErrorException as err:
        raise err
    except Exception as err:
        cause = "Error in detection"
        error_detail = {
            "traceback": traceback.repr(),
            "error": repr(err)
        }
        raise InternalErrorException(
            cause=cause, detail=error_detail, error_code="000")
    # 使用nms对bbox进行筛选
    origin_coordinate_list = fake_nms(origin_coordinate_list)
    sub_meta_info_list = []
    for origin_coordinate in origin_coordinate_list:
        left = int(origin_coordinate[0])
        top = int(origin_coordinate[1])
        right = int(origin_coordinate[2])
        bottom = int(origin_coordinate[3])
        detection_class = int(origin_coordinate[-1])
        areas = ((bottom - top) * (right - left)) * 1.0 / (rows * cols)
        # 通过子图的坐标切割出子图, 其中切割的是rgb 像素矩阵 （channel last）
        channel_last_sub_image = clip_sub_image(
            channel_last_rgb_array, (left, top, right, bottom))
        try:
            # 分类，生成向量
            cls_result = await classify_net_by_tfserving(channel_last_sub_image)
        except InternalErrorException as err:
            raise err
        except Exception as err:
            cause = "Error in classify by tfserving"
            error_detail = {
                "traceback": traceback.repr(),
                "error": repr(err)
            }
            raise InternalErrorException(
                cause=cause, detail=error_detail, error_code="000")

        # TODO 保存到milvus
        hash_vector = cls_result["hash_vector"]
        del cls_result["hash_vector"]
        save_milvus_info = None
        try:
            save_milvus_info = await save_milvus(hash_vector, milvus)
        except InternalErrorException as err:
            raise err
        except Exception as err:
            cause = "Error in insert vector into milvus"
            error_detail = {
                "traceback": traceback.repr(),
                "error": repr(err)
            }
            raise InternalErrorException(
                cause=cause, detail=error_detail, error_code="000")

        sub_meta_data = {
            "url": url,
            "position": {
                "left": left,
                "top": top,
                "right": right,
                "bottom": bottom
            },
            "areas": areas,
            "extension": extension,
            "is_face": False
        }
        if detection_class == 0:
            sub_meta_data.update({"label_1":"人","confidence_1":1.0})
        else:
            sub_meta_data.update(cls_result)
        sub_meta_data.update(save_milvus_info)
        sub_meta_info_list.append(sub_meta_data)
    return sub_meta_info_list
