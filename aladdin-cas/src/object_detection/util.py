from exception_handler import ParamsException, InternalErrorException, ParamsWrongTypeException, MissingParamsException, InvalidParamsException
from read_config import globalization_lang, service_code, exception_level
import asyncio
import base64
import io
import logging
import os
import sys
from traceback import format_exception_only
import traceback
import time
import numpy as np
from PIL import Image, ImageFile
ImageFile.LOAD_TRUNCATED_IMAGES = True


def _get_module_path(path): return os.path.normpath(
    os.path.join(os.getcwd(), os.path.dirname(__file__), path))


detection_resize_map = {
    "D0": 512,
    "D1": 640,
    "D2": 768,
    "D3": 896,
    "D4": 1024,
    "D5": 1280,
    "D6": 1280,
    "D7": 1536
}


def preprocess_for_fbnet(channel_last_sub_image):
    resized_sub_image = channel_last_sub_image.resize((288, 288))
    resized_sub_image_array = np.asarray(resized_sub_image)
    rgb_mean = np.array([0.485, 0.456, 0.406], dtype=np.float32)
    rgb_std = np.array([0.229, 0.224, 0.225], dtype=np.float32)
    zero_one_sub_image = resized_sub_image_array/255.0
    normlization_sub_image_array = (zero_one_sub_image - rgb_mean)/rgb_std
    normlization_sub_image_array = np.transpose(
        normlization_sub_image_array, (2, 0, 1))
    normlization_sub_image_array = np.expand_dims(
        normlization_sub_image_array, axis=0)
    # normlization_sub_image_tensor = tf.convert_to_tensor(normlization_sub_image_array)
    return normlization_sub_image_array


def update_data_check(input_params):
    if input_params is None:
        cause = "wrong number of parameters"
        error_detail = {
            "parameters": ["vid", "label"]
        }
        raise ParamsException(
            cause=cause, detail=error_detail, error_code="000")
    if len(input_params) == 0:
        cause = "wrong number of parameters"
        error_detail = {
            "parameters": ["vid", "label"]
        }
        raise ParamsException(
            cause=cause, detail=error_detail, error_code="000")
    if not isinstance(input_params, list):
        cause = "parameters type must be list"
        error_detail = {
            "parameters": ["vid", "label"]
        }
        raise ParamsException(
            cause=cause, detail=error_detail, error_code="000")
    for param in input_params:
        if "vid" not in param.keys():
            cause = "missing parameters"
            error_detail = {
                "parameters": ["vid"],
                "details":param
            }
            raise ParamsException(
                cause=cause, detail=error_detail, error_code="000")
        vid = param["vid"]
        if not isinstance(vid, str):
            cause = "parameters type error"
            error_detail = {
                "parameters": ["vid"],
                "details":param
            }
            raise ParamsException(
                cause=cause, detail=error_detail, error_code="000")
        if len(vid) == 0:
            cause = "parameters length error"
            error_detail = {
                "parameters": ["vid"],
                "details":param
            }
            raise ParamsException(
                cause=cause, detail=error_detail, error_code="000")            
        if "label" not in param.keys():
            cause = "missing parameters"
            error_detail = {
                "parameters": ["label"],
                "details":param
            }
            raise ParamsException(
                cause=cause, detail=error_detail, error_code="000")
        label = param["label"]
        if not isinstance(vid, str):
            cause = "parameters type error"
            error_detail = {
                "parameters": ["label"],
                "details":param
            }
            raise ParamsException(
                cause=cause, detail=error_detail, error_code="000")

        
def update_data_handler(input_params):
    return_input_params = []
    for param in input_params:
        vid = str(param["vid"]).replace("\\", "/").strip()
        label = str(param["label"]).replace("\\", "/").strip()
        return_input_params.append(dict(vid=vid, label=label))
    return return_input_params





def check_search_params(query_params, body_params):
    checked_dict = dict()
    offset = 0
    limit = 20
    if body_params is None:
        raise MissingParamsException(detail=dict(parameters=["url","image","vid"]))
    count_of_body_params = len(body_params)
    if count_of_body_params == 0:
        raise MissingParamsException(detail=dict(parameters=["url","image","vid"]))

    if count_of_body_params != 1:
        raise InvalidParamsException(detail=dict(parameters="body parameter must be one of ('url', 'image', 'vid') and only one"))
    if list(body_params.keys())[0] not in ["url", "vid", "image"]:
        raise MissingParamsException(detail=dict(parameters="body parameter must be one of ('url', 'image', 'vid') and only one"))
    if "url" in list(body_params.keys()):
        url = body_params["url"]
        if not isinstance(url, str):
            raise ParamsWrongTypeException(detail=dict(parameters=["url"]))
        if len(url) == 0:
            raise InvalidParamsException(detail=dict(parameters=["url"]))
        if url is None:
            raise InvalidParamsException(detail=dict(parameters=["url"]))
        checked_dict["url"] = url
        checked_dict["flag"] = 0
    elif "image" in list(body_params.keys()):
        image_base64 = body_params["image"]
        if not isinstance(image_base64, str):
            raise ParamsWrongTypeException(detail=dict(parameters=["image"]))
        if len(image_base64) == 0:
            raise InvalidParamsException(detail=dict(parameters=["image"]))
        if image_base64 is None:
            raise InvalidParamsException(detail=dict(parameters=["image"]))
        if checkSize(image_base64) is False:
            raise InvalidParamsException(detail=dict(parameters="image length over limit 3M"))
        try:
            image_data = base64.b64decode(image_base64)
            image = io.BytesIO(image_data)
            image = Image.open(image)
            image = image.convert("RGB")
        except Exception as err:
            raise InvalidParamsException(detail=dict(parameters="image conversion from Base64 encoding failed", traceback=traceback.format_exc(), error=repr(err)))
        cols, rows = image.size
        new_image = resize_image(image, rows, cols, detection_resize_map["D1"])
        channel_last_rgb_array = np.array(image)
        channel_last_rgb_array_resize = np.array(new_image)
        checked_dict['image'] = channel_last_rgb_array
        checked_dict["rgb_array_channel_last"] = channel_last_rgb_array
        checked_dict["rgb_array_channel_last_resize"] = channel_last_rgb_array_resize
        checked_dict["rows"] = rows
        checked_dict["cols"] = cols
        checked_dict["flag"] = 1
    elif "vid" in list(body_params.keys()):
        vid = body_params["vid"]
        if not isinstance(vid, str):
            raise ParamsWrongTypeException(detail=dict(parameters=["vid"]))
        if len(vid) == 0:
            raise InvalidParamsException(detail=dict(parameters=["vid"]))
        if vid is None:
            raise InvalidParamsException(detail=dict(parameters=["vid"]))
        checked_dict["vid"] = vid
        checked_dict["flag"] = 2
    else:
        raise MissingParamsException(detail=dict(parameters=["url","image","vid"]))
    if "offset" in list(query_params.keys()):
        offsetStr = query_params.get("offset")
        if offsetStr.isdigit() is True:
            offset = int(offsetStr)
        else:
            raise InvalidParamsException(detail=dict(parameters="offset must be Positive integer and must more than 0"))
    if "limit" in list(query_params.keys()):
        limitStr = query_params.get("limit")
        if limitStr.isdigit() is True:
            limit = int(limitStr)
        else:
            raise InvalidParamsException(detail=dict(parameters="limit must be Positive integer, and must more than 0 and less than 100"))
    if offset <0:
        raise InvalidParamsException(detail=dict(parameters="offset must be Positive integer and must more than 0"))
    if limit <0 or limit >100:
        raise InvalidParamsException(detail=dict(parameters="limit must be Positive integer, and must more than 0 and less than 100"))
    checked_dict["offset"] = offset
    checked_dict["limit"] = limit
    return checked_dict

def check_search_params_old(search_param):
    if search_param is None:
        cause = "wrong number of parameters"
        error_detail = {
            "parameters": ["url", "image", "vid", "top_k"]
        }
        raise ParamsException(
            cause=cause, detail=error_detail, error_code="000")
    len_of_params = len(search_param)
    if len_of_params != 2:
        cause = "wrong number of parameters"
        error_detail = {
            "parameters": ["url", "image", "vid", "top_k"]
        }
        raise ParamsException(
            cause=cause, detail=error_detail, error_code="000")

    if "top_k" not in search_param.keys():
        cause = "missing parameters"
        error_detail = {
            "parameters": ["top_k"]
        }
        raise ParamsException(
            cause=cause, detail=error_detail, error_code="000")
    top_k = search_param["top_k"]

    if not isinstance(top_k, int):
        cause = "parameter type error"
        error_detail = {
            "parameters": ["top_k"]
        }
        raise ParamsException(
            cause=cause, detail=error_detail, error_code="000")

    if top_k > 100:
        cause = "parameter value is incorrect (0<top_k<=100)"
        error_detail = {
            "parameters": ["top_k"]
        }
        raise ParamsException(
            cause=cause, detail=error_detail, error_code="000")

    if top_k <= 0:
        cause = "parameter value is incorrect (0<top_k<=100)"
        error_detail = {
            "parameters": ["top_k"]
        }
        raise ParamsException(
            cause=cause, detail=error_detail, error_code="000")

    checked_dict = {
        "top_k": top_k,
    }
    if "url" in search_param.keys():
        url = search_param["url"]
        if not isinstance(url, str):
            cause = "parameter type error"
            error_detail = {
                "parameters": ["url"]
            }
            raise ParamsException(
                cause=cause, detail=error_detail, error_code="000")

        if len(url) == 0:
            cause = "parameter format error"
            error_detail = {
                "parameters": ["url"]
            }

            raise ParamsException(
                cause=cause, detail=error_detail, error_code="000")

        if url is None:
            cause = "parameter type error"
            error_detail = {
                "parameters": ["url"]
            }
            raise ParamsException(
                cause=cause, detail=error_detail, error_code="000")

        checked_dict["url"] = url
        checked_dict["flag"] = 0
        return checked_dict

    elif "image" in search_param:
        image_base64 = search_param["image"]
        if not isinstance(image_base64, str):
            cause = "parameter type error"
            error_detail = {
                "parameters": ["image"]
            }
            raise ParamsException(
                cause=cause, detail=error_detail, error_code="000")
        if len(image_base64) == 0:
            cause = "parameter format error"
            error_detail = {
                "parameters": ["image"]
            }
            raise ParamsException(
                cause=cause, detail=error_detail, error_code="000")

        if image_base64 is None:
            cause = "parameter type error"
            error_detail = {
                "parameters": ["image"]
            }
            raise ParamsException(
                cause=cause, detail=error_detail, error_code="000")
        if checkSize(image_base64) is False:
            cause = "image length over limit 3M"
            error_detail = {
                "parameters": ["image"]
            }
            raise ParamsException(cause=cause, detail=error_detail, error_code="000")

        try:
            image_data = base64.b64decode(image_base64)
            image = io.BytesIO(image_data)
            image = Image.open(image)
            image = image.convert("RGB")
        except Exception as err:
            cause = "Image conversion from Base64 encoding failed"
            error_detail = {
                "parameters": ["image"],
                "traceback": traceback.format_exc(),
                "error": repr(err)
            }
            raise ParamsException(
                cause=cause, detail=error_detail, error_code="000")

        cols, rows = image.size
        new_image = resize_image(image, rows, cols, detection_resize_map["D1"])
        channel_last_rgb_array = np.array(image)
        channel_last_rgb_array_resize = np.array(new_image)
        checked_dict['image'] = channel_last_rgb_array
        checked_dict["rgb_array_channel_last"] = channel_last_rgb_array
        checked_dict["rgb_array_channel_last_resize"] = channel_last_rgb_array_resize
        checked_dict["rows"] = rows
        checked_dict["cols"] = cols
        checked_dict["flag"] = 1
        return checked_dict
    elif "vid" in search_param:
        vid = search_param["vid"]
        if not isinstance(vid, str):
            cause = "parameter type error"
            error_detail = {
                "parameters": ["vid"]
            }
            raise ParamsException(
                cause=cause, detail=error_detail, error_code="000")

        if len(vid) == 0:
            cause = "parameter format error"
            error_detail = {
                "parameters": ["vid"]
            }
            raise ParamsException(
                cause=cause, detail=error_detail, error_code="000")

        if vid is None:
            cause = "parameter type error"
            error_detail = {
                "parameters": ["vid"]
            }
            raise ParamsException(
                cause=cause, detail=error_detail, error_code="000")

        checked_dict["vid"] = vid
        checked_dict["flag"] = 2
        return checked_dict
    else:
        cause = "invalid parameter"
        error_detail = {
            "parameters": search_param.keys()
        }
        raise ParamsException(
            cause=cause, detail=error_detail, error_code="000")


def check_meta_data_and_milvus(milvus, dbclient):
    def get_all_vectors_in_collections(milvus, collection_info):
        all_milvus_id = []
        partition_list = collection_info["partitions"]
        for partition in partition_list:
            segments_list = partition["segments"]
            for segment in segments_list:
                segment_name = segment["name"]
                _, seg_milvus_id_list = milvus.list_id_in_segment(segment_name)
                all_milvus_id.extend(seg_milvus_id_list)
        return all_milvus_id
    collection_info = milvus.get_collection_stats()
    milvus_id_count = collection_info["row_count"]
    meta_data_count = dbclient.count_record()
    if meta_data_count == milvus_id_count:
        return
    elif meta_data_count < milvus_id_count:
        all_milvus_list = get_all_vectors_in_collections(
            milvus, collection_info)
        meta_data_list = dbclient.get_all_milvus_id()
        milvus.delete_entity_by_id(
            list(set(all_milvus_list) ^ set(meta_data_list)))
    else:
        pass


def resize_image(image, rows, cols, max_edge):
    cur_max_edge = max(rows, cols)
    if cur_max_edge < max_edge:
        return image
    else:
        zoom_scale = (cur_max_edge * 1.) / max_edge
        new_rows = int(rows/zoom_scale)
        new_cols = int(cols/zoom_scale)
        new_image = image.resize((new_cols, new_rows), Image.BICUBIC)
        # print(f"新图片尺寸：{new_image.size}")
        # print(f"就图片尺寸：{image.size}")
        return new_image


def post_data_handler(input_params):
    url = input_params["url"].replace("\\", "/").strip()
    base64_code_string = input_params["image"].strip()
    del input_params["url"]
    del input_params["image"]
    image = None
    try:
        image_from_base64 = base64.b64decode(base64_code_string)
        image_io = io.BytesIO(image_from_base64)
        image = Image.open(image_io)
        image = image.convert("RGB")
    except Exception as err:
        cause = "Image conversion from Base64 encoding failed"
        error_detail = {
            "parameters": ["image"],
            "traceback": traceback.format_exc(),
            "error": repr(err)
        }
        raise ParamsException(
            cause=cause, detail=error_detail, error_code="000")
    cols, rows = image.size
    new_image = resize_image(image, rows, cols, detection_resize_map["D1"])
    channel_last_rgb_array = np.array(image)
    channel_last_rgb_array_resize = np.array(new_image)

    input_data = {
        "url": url,
        "rgb_array_channel_last": channel_last_rgb_array,
        "rows": rows,
        "cols": cols,
        "rgb_array_channel_last_resize": channel_last_rgb_array_resize,
        "extension": input_params
    }
    return input_data


def checkSize(b64):
    b64 = b64.replace("=","")
    length = len(b64)
    file_length = int(length - (length/8*2))
    if file_length/1024/1024 > 3.:
        return False
    else:
        return True

def post_data_check(input_params):
    if input_params is None:
        cause = "missing parameters"
        error_detail = {
            "parameters": ["url", "image"]
        }
        raise ParamsException(
            cause=cause, detail=error_detail, error_code="000")
    if "url" not in input_params.keys():
        cause = "missing parameters"
        error_detail = {
            "parameters": ["url"]
        }
        raise ParamsException(
            cause=cause, detail=error_detail, error_code="000")
    url = input_params["url"]
    if "image" not in input_params.keys():
        cause = "missing parameters"
        error_detail = {
            "parameters": ["image"]
        }
        raise ParamsException(
            cause=cause, detail=error_detail, error_code="000")
    base64_string = input_params["image"]
    
    if not isinstance(url, str):
        cause = "parameter type error"
        error_detail = {
            "parameters": ["url"]
        }
        raise ParamsException(
            cause=cause, detail=error_detail, error_code="000")
    if len(url) == 0:
        cause = "parameter format error"
        error_detail = {
            "parameters": ["url"]
        }

        raise ParamsException(
            cause=cause, detail=error_detail, error_code="000")

    if url is None:
        cause = "parameter type error"
        error_detail = {
            "parameters": ["url"]
        }
        raise ParamsException(
            cause=cause, detail=error_detail, error_code="000")

    if not isinstance(base64_string, str):
        cause = "parameter type error"
        error_detail = {
            "parameters": ["image"]
        }
        raise ParamsException(
            cause=cause, detail=error_detail, error_code="000")
    if len(base64_string) == 0:
        cause = "parameter format error"
        error_detail = {
            "parameters": ["image"]
        }
        raise ParamsException(
            cause=cause, detail=error_detail, error_code="000")

    if base64_string is None:
        cause = "parameter type error"
        error_detail = {
            "parameters": ["image"]
        }
        raise ParamsException(
            cause=cause, detail=error_detail, error_code="000")
    if checkSize(base64_string) is False:
        cause = "image length over limit 3M"
        error_detail = {
            "parameters": ["image"]
        }
        raise ParamsException(cause=cause, detail=error_detail, error_code="000")


def delete_data_check(input_params, types):
    if types == "vid":
        if not isinstance(input_params, list):
            cause = "parameter need list type"
            error_detail = {
                "parameters": ["vids"]
            }
            raise ParamsException(
                cause=cause, detail=error_detail, error_code="000")
        if len(input_params) == 0:
            cause = "wrong number of parameters"
            error_detail = {
                "parameters": ["vids"]
            }
            raise ParamsException(
                cause=cause, detail=error_detail, error_code="000")
                    
        for item in input_params:
            if not isinstance(item, str):
                cause = "parameter type error"
                error_detail = {
                    "parameters": ["vid"]
                }
                raise ParamsException(
                    cause=cause, detail=error_detail, error_code="000")
                break
            if len(item) == 0:
                cause = "parameter format error"
                error_detail = {
                    "parameters": ["vid"]
                }
                raise ParamsException(
                    cause=cause, detail=error_detail, error_code="000")       
    elif types == "url":
        if not isinstance(input_params, list):
            cause = "parameter need list type"
            error_detail = {
                "parameters": ["urls"]
            }
            raise ParamsException(
                cause=cause, detail=error_detail, error_code="000")
        if len(input_params) == 0:
            cause = "wrong number of parameters"
            error_detail = {
                "parameters": ["urls"]
            }
            raise ParamsException(
                cause=cause, detail=error_detail, error_code="000")
                    
        for item in input_params:
            if not isinstance(item, str):
                cause = "parameter type error"
                error_detail = {
                    "parameters": ["url"]
                }
                raise ParamsException(
                    cause=cause, detail=error_detail, error_code="000")
                break
            if len(item) == 0:
                cause = "parameter format error"
                error_detail = {
                    "parameters": ["url"]
                }
                raise ParamsException(
                    cause=cause, detail=error_detail, error_code="000")
    elif types == "cid":
        if not isinstance(input_params, list):
            cause = "parameter need list type"
            error_detail = {
                "parameters": ["cids"]
            }
            raise ParamsException(
                cause=cause, detail=error_detail, error_code="000")
        if len(input_params) == 0:
            cause = "wrong number of parameters"
            error_detail = {
                "parameters": ["cids"]
            }
            raise ParamsException(
                cause=cause, detail=error_detail, error_code="000")
                    
        for item in input_params:
            if not isinstance(item, str):
                cause = "parameter type error"
                error_detail = {
                    "parameters": ["cid"]
                }
                raise ParamsException(
                    cause=cause, detail=error_detail, error_code="000")
                break
            if len(item) == 0:
                cause = "parameter format error"
                error_detail = {
                    "parameters": ["cid"]
                }
                raise ParamsException(
                    cause=cause, detail=error_detail, error_code="000") 
    else:
        raise ParamsException(cause="type error", detail={"parameters": ["vid","url","cid"] }, error_code="000")           


def delete_data_handler(input_params, types):
    return_input_params = []
    for item in input_params:
        return_input_params.append(str(item).replace("\\", " / ").strip())
    return return_input_params


def get_data_check(input_params):
    if input_params is None:
        raise ParamsException(cause="wrong number of parameters", detail={"parameters":["url"]}, error_code="000")
    if "url" in input_params.keys() and "vid" in input_params.keys():
        raise ParamsException(cause="wrong number of parameters", detail={"parameters":["url","vid"]}, error_code="000")
    if "url" in input_params.keys():
        url = input_params["url"]
        if not isinstance(url, str):
            raise ParamsException(cause="parameter type error", detail={"parameters": ["url"]}, error_code="000")
        if len(url) == 0:
            raise ParamsException(cause="parameter format error", detail={"parameters": ["url"]}, error_code="000")
        if url is None:
            raise ParamsException(cause="missing parameters", detail={"parameters": ["url"]}, error_code="000")
        return "url"
    elif "vid" in input_params.keys():
        vid = input_params["vid"]
        if not isinstance(vid, str):
            raise ParamsException(cause= "parameter type error", detail={"parameters": ["vid"]}, error_code="000")
        if len(vid) == 0:
            raise ParamsException(cause="parameter format error", detail={"parameters": ["vid"]}, error_code="000")
        if vid is None:
            raise ParamsException(cause="missing parameters", detail={"parameters": ["vid"]}, error_code="000")
        return "vid"
    else:
        raise ParamsException(cause= "parameter type error", detail={"parameters": ["url", "vid"]}, error_code="000")      


def get_data_handler(input_params, types):
    if types == "url":
        return {"url": input_params["url"].replace("\\", "/").strip()}
    else:
        return {"vid": input_params["vid"].replace("\\", "/").strip()}


def clip_sub_image(image_array, sub_image_coord):
    image = Image.fromarray(np.uint8(image_array))
    sub_image = image.crop(
        (sub_image_coord[0], sub_image_coord[1], sub_image_coord[2], sub_image_coord[3]))
    return sub_image


def choose_partition(vector):
    vector = vector.reshape((1, 1, -1))
    vector_expand = np.tile(vector, (1000, 10, 1))
    dist_matrix = np.sqrt(
        np.sum(np.power(vector_expand - support_collection, 2), axis=2))
    order_cluster_list = list(np.unravel_index(np.argsort(
        dist_matrix.ravel())[:100], dist_matrix.shape)[0])

    order_cluster_set = sorted(
        set(order_cluster_list), key=order_cluster_list.index)
    top_1_partition = order_cluster_set[0]
    return order_cluster_set


from prework.CN_class_dict import class_dict
support_collection = np.load(_get_module_path("support_collection.npy"))
class_dict = class_dict
