import io
import base64
import numpy as np
from PIL import Image
from exception_handler import MissingParamsException, ParamsWrongTypeException, InvalidParamsException
from match_image.utils import Normal


def CheckIndexPost(input_params):
    # Check missing parameters error.
    miss_parameters = [x for x in ["image", "label"] if x \
        not in input_params.keys()]
    if len(miss_parameters) == 0:
        img_label = input_params["label"]
        img_b64 = input_params["image"]
    else:
        detail = ", ".join(miss_parameters)
        error_detail = {
            "error": f"The parameter fields ({detail}) was not found.",
        }
        raise MissingParamsException(detail=error_detail)
    # Check parameter type error.
    if isinstance(img_label, str) and isinstance(img_b64, str):
        pass
    else:
        detail = ""
        if not isinstance(img_label, str):
            detail += "The parameter (label) should be a type of string."
        if not isinstance(img_b64, str):
            detail += "The parameter (image) should be a type of string."
        error_detail = {
            "error": detail,
        }
        raise ParamsWrongTypeException(detail=error_detail)
    # Check invalid parameter error.
    try:
        img_data = base64.b64decode(img_b64.split(',')[-1])
        img_fp = io.BytesIO(img_data)
        img = Image.open(img_fp)
        img = img.convert('RGB')
        img = Normal(img, 3)
        img_rgb_array = np.array(img)[:, :, :3]
    except:
        error_detail = {
            "error": "The string of image's base64 decoding failed."
        }
        raise InvalidParamsException(detail=error_detail)
    
    output_params = {
        "label": img_label,
        "image": img_rgb_array
    }

    return output_params

def CheckIndexDelete(input_params):
    # Check missing parameters error.
    miss_parameters = [x for x in ["labels", ] if x not in \
        input_params.keys()]
    if len(miss_parameters) == 0:
        img_labels = input_params["labels"]
    else:
        detail = ", ".join(miss_parameters)
        error_detail = {
            "error": f"The parameter fields ({detail}) was not found.",
        }
        raise MissingParamsException(detail=error_detail)
    # Check parameter type error.
    if isinstance(img_labels, list):
        pass
    else:
        error_detail = {
            "error": "The parameter (labels) should be a type of list.",
        }
        raise ParamsWrongTypeException(detail=error_detail)
    # Check parameter type error.
    error_type_list = [x for x in img_labels if not isinstance(x, str)]
    if len(error_type_list) == 0:
        pass
    else:
        error_detail = {
            "error": "The parameter (labels' elements) should \
                be a type of string.",
        }
        raise ParamsWrongTypeException(detail=error_detail)
    
    output_params = {
        "labels": img_labels,
    }

    return output_params

def CheckSearchPost(input_params):
    # Check missing parameters error.
    miss_parameters = [x for x in ["image", ] if x \
        not in input_params.keys()]
    if len(miss_parameters) == 0:
        img_b64 = input_params["image"]
    else:
        detail = ", ".join(miss_parameters)
        error_detail = {
            "error": f"The parameter fields ({detail}) was not found.",
        }
        raise MissingParamsException(detail=error_detail)
    # Check parameter type error.
    if isinstance(img_b64, str):
        pass
    else:
        error_detail = {
            "error": "The parameter (image) should be a type of string.",
        }
        raise ParamsWrongTypeException(detail=error_detail)
    # Check invalid parameter error.
    try:
        img_data = base64.b64decode(img_b64.split(',')[-1])
        img_fp = io.BytesIO(img_data)
        img = Image.open(img_fp)
        img = img.convert('RGB')
        img = Normal(img, 2)
        img_rgb_array = np.array(img)[:, :, :3]
    except:
        error_detail = {
            "error": "The string of image's base64 decoding failed."
        }
        raise InvalidParamsException(detail=error_detail)
    
    output_params = {
        "image": img_rgb_array,
    }

    return output_params