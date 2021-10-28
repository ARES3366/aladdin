import base64
import io
import json
import traceback
import face_recognition as fr
import numpy as np
from read_config import milvus_config, mongo_config


async def face_image_embedding_and_save(input_data, milvus):
    url = input_data["url"]  # 图片地址
    rows = input_data["rows"]
    cols = input_data["cols"]
    channel_last_rgb_array = input_data["rgb_array_channel_last"]
    extension = input_data["extension"]
    locations = fr.face_locations(channel_last_rgb_array)
    face_meta_info_list = []
    if len(locations) == 0:
        # 如果没有人脸
        return face_meta_info_list
    else:    
        encodings = fr.face_encodings(channel_last_rgb_array, known_face_locations=locations)
        vecs = np.array(encodings)
        result = milvus.insert(vectors=vecs, partition_tag=None)
        if result.get("status") == 1:
            cause = "failed to insert vector into Milvus"
            error_detail = {
                "traceback": result["details"],
                "error": result["message"]
            }
            raise InternalErrorException(
                cause=cause, detail=error_detail, error_code="000")
        milvus_id_list = result["message"]
        for i in range(len(milvus_id_list)):
            box = locations[i]
            top = int(box[0])
            right = int(box[1])
            bottom = int(box[2])
            left = int(box[3])
            areas = ((bottom - top) * (right - left)) * 1.0 / (rows * cols)
            milvus_id = str(milvus_id_list[i])
            face_meta_data = {
                "url":url,
                "position":{
                    "left":left,
                    "top":top,
                    "right":right,
                    "bottom": bottom
                },
                "areas": areas,
                "extension":extension,
                "is_face":True,
                "vid": milvus_id
            }
            cls_result = {
                "label_1": "",
                "confidence_1": 1.0
            }
            face_meta_data.update(cls_result)
            face_meta_info_list.append(face_meta_data)
        
    return face_meta_info_list