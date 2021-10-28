import sys
import numpy as np
import traceback
from exception_handler import ParamsException, InternalErrorException
async def update_meta_data_label(input_params, dbclient):
    error_list = []
    success_list = []
    for item in input_params:
        vid = item["vid"]
        label = item["label"]
        conditions = {"find": {"vid": str(vid)}, "update": {"$set":{"label_1": str(label), "confidence_1":1.0}, "$unset":{"label_2":"","label_3":"","label_4":"","label_5":"","confidence_2":"","confidence_3":"","confidence_4":"","confidence_5":""}}}
        
        try:
            update_result = await dbclient.select_one_and_update(conditions)
            # todo 如果更新记录为空，则update失败，返回500001
            if update_result is None:
                error_list.append(vid)
            else:
                if "is_face" not in update_result.keys():
                    conditions = {"find":{"vid": str(vid)},"update":{"$unset":{"classify":""},"$set":{"is_face":False}}}
                    update_result = await dbclient.select_one_and_update(conditions)
                success_list.append(vid)
        except Exception as err:
            cause = "failed to update data from mongodb"
            error_detail = {
                "traceback":traceback.format_exc(),
                "error": repr(err)
            }
            raise InternalErrorException(cause=cause, detail=error_detail, error_code="000")
    if len(error_list) == 0:
        return dict(code="200", message="success")
    else:
        error_detail = {
            "error": "the vid is not in the metadata database",
            "details": dict(success=success_list, error=error_list)
        }
        raise InternalErrorException(cause="failed to update data from mongodb", detail=error_detail, error_code="001")
        
            
        