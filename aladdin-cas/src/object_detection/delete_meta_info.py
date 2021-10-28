import traceback

from exception_handler import ParamsException, InternalErrorException
async def delete_meta_data_by_vid(vid_list, milvus_client_for_sub, milvus_client_for_face, dbclient):
    # print("通过vid删除")
    try:
        select_result = await dbclient.select({"vid": {"$in": vid_list}})
    except Exception as err:
        cause = "failed to search data from mongodb by vid"
        error_detail = {
            "traceback": traceback.format_exc(),
            "error": repr(err)
        }
        raise InternalErrorException(
            cause=cause, detail=error_detail, error_code="000")    
    selected_vid_list_face = []
    selected_vid_list_sub = []
    selected_vid_list = []
    for item in select_result:
        if "is_face" in item.keys():
            if item["is_face"] is True:
                selected_vid_list_face.append(int(item["vid"]))
            else:
                selected_vid_list_sub.append(int(item["vid"]))
        else:
            selected_vid_list_sub.append(int(item["vid"]))
        selected_vid_list.append(item["vid"])
    # if len(selected_vid_list) == 0:
    #     print("要删除的vid全都不在元数据中")
    # else:
    #     print(f"所有要删除的vid: {selected_vid_list}")
    # if len(selected_vid_list_sub) == 0:
    #     print("要删除的vid不存在子图vid")
    # if len(selected_vid_list_face) == 0:
    #     print("要删除的vid不存在人脸vid")
    # try:
    delete_mongo_result = await dbclient.delete_many({"vid": {"$in": selected_vid_list}})
    if delete_mongo_result["delete_num"] == 0 and delete_mongo_result["status"] == 0:
        return dict(status=0, message="要删除的vid不在元数据中")
    if len(selected_vid_list_sub) != 0:
        # print(f"开始删除从子图milvus中删除向量: {selected_vid_list_sub}") 
        delete_sub_result = milvus_client_for_sub.delete_entity_by_id(selected_vid_list_sub)
        if delete_sub_result.get("status") == 1:
            cause = "failed to delete vector from sub milvus"
            error_detail = {
                "traceback": delete_sub_result["details"],
                "error": delete_sub_result["message"]
            }
            raise InternalErrorException(
                cause=cause, detail=error_detail, error_code="000")
    if len(selected_vid_list_face) != 0:
        # print(f"开始删除从人脸milvus中删除向量: {selected_vid_list_face}") 
        delete_face_result = milvus_client_for_face.delete_entity_by_id(selected_vid_list_face)
        if delete_face_result.get("status") == 1:
            cause = "failed to delete vector from face milvus"
            error_detail = {
                "traceback": delete_face_result["details"],
                "error": delete_face_result["message"]
            }
            raise InternalErrorException(
                cause=cause, detail=error_detail, error_code="000")
    return dict(status=0, message="删除成功")


async def delete_meta_data_by_url(url_list, milvus_client_for_sub, milvus_client_for_face, dbclient):
    # print("通过url删除")
    try:
        select_result = await dbclient.select({"url": {"$in": url_list}})
    except Exception as err:
        cause = "failed to search data from mongodb by url"
        error_detail = {
            "traceback": traceback.format_exc(),
            "error": repr(err)
        }
        raise InternalErrorException(
            cause=cause, detail=error_detail, error_code="000")

    selected_vid_list_face = []
    selected_vid_list_sub = []
    selected_vid_list = []
    for item in select_result:
        if "is_face" in item.keys(): # 新数据
            if item["is_face"] is True:
                selected_vid_list_face.append(int(item["vid"]))
            else:
                selected_vid_list_sub.append(int(item["vid"]))
        else:   # 老数据
            selected_vid_list_sub.append(int(item["vid"]))

        selected_vid_list.append(item["vid"])
    # if len(selected_vid_list) == 0:
    #     print("要删除的vid全都不在元数据中")
    # else:
    #     print(f"所有要删除的vid: {selected_vid_list}")
    # if len(selected_vid_list_sub) == 0:
    #     print("要删除的vid不存在子图vid")
    # if len(selected_vid_list_face) == 0:
    #     print("要删除的vid不存在人脸vid")
    delete_mongo_result = await dbclient.delete_many({"vid": {"$in": selected_vid_list}})
    if delete_mongo_result["delete_num"] == 0 and delete_mongo_result["status"] == 0:
        return dict(status=0, message="要删除的vid不在元数据中")
    if len(selected_vid_list_sub) != 0:
        # print(f"开始删除从子图milvus中删除向量: {selected_vid_list_sub}") 
        delete_sub_result = milvus_client_for_sub.delete_entity_by_id(selected_vid_list_sub)
        if delete_sub_result.get("status") == 1:
            cause = "failed to delete vector from sub milvus"
            error_detail = {
                "traceback": delete_sub_result["details"],
                "error": delete_sub_result["message"]
            }
            raise InternalErrorException(
                cause=cause, detail=error_detail, error_code="000")
    if len(selected_vid_list_face) != 0:
        # print(f"开始删除从人脸milvus中删除向量: {selected_vid_list_face}") 
        delete_face_result = milvus_client_for_face.delete_entity_by_id(selected_vid_list_face)
        if delete_face_result.get("status") == 1:
            cause = "failed to delete vector from face milvus"
            error_detail = {
                "traceback": delete_face_result["details"],
                "error": delete_face_result["message"]
            }
            raise InternalErrorException(
                cause=cause, detail=error_detail, error_code="000")
    return dict(status=0, message="删除成功")
