import numpy as np
from PIL import Image
from read_config import elasticsearch_config, dl_inference_server_config, delg_config
from exception_handler import InternalErrorException


def Normal(image, _type):
    # Normalize the image
    (hx, hy) = image.size[:2]
    area = hx * hy
    if _type == 0:
        return image
    elif _type == 1:
        scale = np.sqrt(65536 / area)
        return image.resize((int(round(hx * scale)), int(round(hy * scale))), resample=Image.BILINEAR)
    elif _type == 2:
        scale = np.sqrt(131072 / area)
        return image.resize((int(round(hx * scale)), int(round(hy * scale))), resample=Image.BILINEAR)
    elif _type == 3:
        scale = np.sqrt(262144 / area)
        return image.resize((int(round(hx * scale)), int(round(hy * scale))), resample=Image.BILINEAR)
    else:
        return image

def AverageHash(image, length):
    # Average hash of image
    (hxl, hyl) = image.shape[:2]
    number = int(np.ceil(np.sqrt(length)))
    hx = [int(np.round(hxl * i / number)) for i in range(number + 1)]
    hy = [int(np.round(hyl * i / number)) for i in range(number + 1)]
    egray = np.zeros([number, number])
    for y in range(number):
        for x in range(number):
            egray[x, y] = np.mean(image[hx[x]:hx[x + 1], hy[y]:hy[y + 1]])

    acode = np.where(egray >= np.mean(image), 1, 0)
    acode_split = acode.flatten()[:length]
    
    return hex(int("".join(str(i) for i in acode_split), 2))

def ScoreFilter(labels_score):
    # results labels filtering
    labels = []

    if len(labels_score) == 0:  # No labels
        return labels

    if labels_score[-1][0] <= 15:  # Highest score judgment
        return labels
    
    if len(labels_score) == 1:  # Only one image has some labels
        labels = labels_score[-1][1]
    elif len(labels_score) == 2:  # Only two image has some labels
        if labels_score[-1][0] >= labels_score[-2][0] * 1.5:
            labels = labels_score[-1][1]
        else:
            labels = labels_score[-1][1] + labels_score[-2][1]
    else:  # More than two image has some labels
        score = np.array([x[0] for x in labels_score])
        if (score[-1] >= score[-2] * 1.5) and (score[-1] >= 30):
            labels = labels_score[-1][1]
        else:
            for i in range(1, len(labels_score)):
                mean_score = np.mean(score[:-i])
                var_score = np.linalg.norm(score[:-i] - mean_score)
                labels = [x[1] for x in labels_score[-i:] if ((x[0] - mean_score) >= 3 * var_score)]
                if labels:
                    labels = sum(labels, [])
                    break
            if not labels:
                labels = labels_score(labels_score[-2:])

    return labels

def CheckESErrorException(status_code, content):
    if status_code == 429:
        cause = "Service is busy."
        error_detail = {
            "Error": content["error"],
            "traceback": traceback.format_exc(),
        }
        raise InternalErrorException(cause=cause, detail=error_detail)


MODEL_CONFIG = {
    "codebook": {
        'global': {
            '1': {
                'path': delg_config["global_path_1"],
            },
            '2': {
                'path': delg_config["global_path_2"],
            },
        },
        'local': {
            '1': {
                'path': delg_config["local_path_1"],
            },
            '2': {
                'path': delg_config["local_path_2"],
            },
        },
    },
    "model": {
        "name": "delg",
        "signature_name": "serving_default",
        "scales": [0.70710677, 1., 1.4142135],
        "max_feature_num": 300,
        "abs_thres": 454.6,
        "global_scales_ind": [0, 1, 2],
    },
    "grpc": {
        "timeout": 30.0,
        "path": f"{dl_inference_server_config['host']}:{dl_inference_server_config['port']}",
    },
}

ELASTICSEARCH_PATH = "http://{host}:{port}".format(
    host=elasticsearch_config["host"],
    port=elasticsearch_config["port"]
)

ALIASES = elasticsearch_config["aliases"]
INDEX_NUM = elasticsearch_config["index_num"]
INDEX_TYPE = elasticsearch_config["index_type"]
