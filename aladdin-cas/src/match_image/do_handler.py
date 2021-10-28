import asyncio
import traceback
from exception_handler import ParamsException, InternalErrorException
from match_image import check_parameters
from match_image.create_index import AddImageLabel
from match_image.delete_index import RemoveImageLabels
from match_image.search_labels import SearchImageLabels


async def MatchImageIndexPost(input_params):
    try:
        params = check_parameters.CheckIndexPost(input_params)
        image = params["image"]
        label = params["label"]
        for i in range(1000):
            result = await AddImageLabel(image, label)
            if result: return {"message": "OK!"}
        raise Exception
    except ParamsException:
        raise
    except InternalErrorException:
        raise
    except:
        cause = "Data conflict error."
        error_detail = {
            "error": "Create image index conflict, try again later.",
            "traceback": traceback.format_exc(),
        }
        raise InternalErrorException(cause=cause, detail=error_detail)

async def MatchImageIndexDelete(input_params):
    try:
        params = check_parameters.CheckIndexDelete(input_params)
        labels = params["labels"]
        for i in range(1000):
            result, labels = await RemoveImageLabels(labels)
            if result: return {"message": "OK!"}
        raise Exception
    except ParamsException:
        raise
    except InternalErrorException:
        raise
    except:
        cause = "Data conflict error."
        error_detail = {
            "error": "Delete image index conflict, try again later.",
            "traceback": traceback.format_exc(),
        }
        raise InternalErrorException(cause=cause, detail=error_detail)

async def MatchImageSearchPost(input_params):
    try:
        params = check_parameters.CheckSearchPost(input_params)
        labels = await SearchImageLabels(params["image"])
        response = {
            "message": "OK!",
            "labels": labels,
        }
        return response
    except ParamsException:
        raise
    except InternalErrorException:
        raise
    except:
        cause = "Unknown data error."
        error_detail = {
            "error": "Unknown data error, try again later.",
            "traceback": traceback.format_exc(),
        }
        raise InternalErrorException(cause=cause, detail=error_detail)