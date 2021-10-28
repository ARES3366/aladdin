from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

import requests
import numpy as np

import asyncio
import traceback
import grpc
from protos.tensorflow_serving.apis import predict_pb2
from protos.tensorflow_serving.apis import prediction_service_pb2_grpc
from protos.tensorflow.core.framework import tensor_pb2
from protos.tensorflow.core.framework import tensor_shape_pb2
from protos.tensorflow.core.framework import types_pb2

import numpy as np
from exception_handler import ParamsException, InternalErrorException


def FeatureExtractor(config):
    # Read Codebook
    try:  
        global_codebook_0 = np.load(config["codebook"]['global']['1']['path'])
        global_codebook_1 = np.load(config["codebook"]['global']['2']['path'])

        local_codebook_0 = np.load(config["codebook"]['local']['1']['path'])
        local_codebook_1 = np.load(config["codebook"]['local']['2']['path'])
    except Exception as err:
        cause = "Failed to loading codebook from config."
        error_detail = {
            "traceback": traceback.format_exc(),
            "error": repr(err)
        }
        raise InternalErrorException(cause=cause, detail=error_detail)
    # Create grpc connection instance
    try:  
        channel = grpc.insecure_channel(config["grpc"]["path"])
        stub = prediction_service_pb2_grpc.PredictionServiceStub(channel)
    except Exception as err:
        cause = "Failed to create grpc connection instance from config."
        error_detail = {
            "traceback": traceback.format_exc(),
            "error": repr(err)
        }
        raise InternalErrorException(cause=cause, detail=error_detail)
    # Load model parameters
    try:
        request = predict_pb2.PredictRequest()
        request.model_spec.name = config["model"]["name"]
        request.model_spec.signature_name = config["model"]["signature_name"]

        input_scales = tensor_pb2.TensorProto(dtype=1,)
        input_scales_dim = input_scales.tensor_shape.dim.add()
        input_scales_dim.size = len(config["model"]["scales"])
        input_scales.float_val.extend(config["model"]["scales"])
        request.inputs["input_scales"].CopyFrom(input_scales)

        input_max_feature_num = tensor_pb2.TensorProto(dtype=3)
        input_max_feature_num.tensor_shape.CopyFrom(tensor_shape_pb2.TensorShapeProto())
        input_max_feature_num.int_val.append(config["model"]["max_feature_num"])
        request.inputs["input_max_feature_num"].CopyFrom(input_max_feature_num) 

        input_abs_thres = tensor_pb2.TensorProto(dtype=1)
        input_abs_thres.tensor_shape.CopyFrom(tensor_shape_pb2.TensorShapeProto())
        input_abs_thres.float_val.append(config["model"]["abs_thres"])
        request.inputs["input_abs_thres"].CopyFrom(input_abs_thres)
        
        input_global_scales_ind = tensor_pb2.TensorProto(dtype=3)
        input_global_scales_ind_dim = input_global_scales_ind.tensor_shape.dim.add()
        input_global_scales_ind_dim.size = len(config["model"]["global_scales_ind"])
        input_global_scales_ind.int_val.extend(config["model"]["global_scales_ind"])
        request.inputs["input_global_scales_ind"].CopyFrom(input_global_scales_ind)
    except Exception as err:
        cause = "Failed to create predictor from config."
        error_detail = {
            "traceback": traceback.format_exc(),
            "error": repr(err)
        }
        raise InternalErrorException(cause=cause, detail=error_detail)

    async def Extract(image):
         # The image array is converted to TensorProto
        try:
            input_image = tensor_pb2.TensorProto(dtype=4)
            dims = [tensor_shape_pb2.TensorShapeProto.Dim(size=dim) for dim in image.shape]
            input_image.tensor_shape.dim.extend(dims)
            input_image.int_val.extend(image.reshape(-1).tolist())
            request.inputs["input_image"].CopyFrom(input_image)
        except Exception as err:
            cause = "Failed to convert picture to TensorProto."
            error_detail = {
                "traceback": traceback.format_exc(),
                "error": repr(err)
            }
            raise ParamsException(cause=cause, detail=error_detail)
        # Get model results by grpc connection instance
        try: 
            result_future = stub.Predict.future(request, timeout=config["grpc"]["timeout"])
            outputs = result_future.result().outputs
        except Exception as err:
            cause = "Failed to get model result from dl-inference-serving"
            error_detail = {
                "traceback": traceback.format_exc(),
                "error": repr(err)
            }
            raise InternalErrorException(cause=cause, detail=error_detail)
        # Generate visual feature vector
        try: 
            global_descriptors = outputs['global_descriptors'].float_val
            global_shape = outputs['global_descriptors'].tensor_shape.dim
            global_shape = [x.size for x in global_shape]
            global_descriptors = np.array(global_descriptors).astype(
                'float32').reshape(global_shape)
            global_descriptor = np.sum(global_descriptors, axis=0)
            global_descriptor_0 = global_descriptor[::2] / np.linalg.norm(
                global_descriptor[::2], ord=2)
            global_descriptor_1 = global_descriptor[1::2] / np.linalg.norm(
                global_descriptor[1::2], ord=2)

            global_score_0 = np.dot(global_descriptor_0, global_codebook_0)
            global_labels_0 = np.argsort(-np.abs(global_score_0)).tolist()
            global_score_1 = np.dot(global_descriptor_1, global_codebook_1)
            global_labels_1 = np.argsort(-np.abs(global_score_1)).tolist()

            local_descriptors = outputs['features'].float_val
            local_shape = outputs['features'].tensor_shape.dim
            local_shape = [x.size for x in local_shape]
            local_descriptors = np.array(local_descriptors).astype(
                'float32').reshape(local_shape)
            length = local_descriptors.shape[0]
            local_descriptors_0 = local_descriptors[:, ::2] / np.linalg.norm(
                local_descriptors[:, ::2], ord=2, axis=1).reshape(length, 1)
            local_descriptors_1 = local_descriptors[:, 1::2] / np.linalg.norm(
                local_descriptors[:, 1::2], ord=2, axis=1).reshape(length, 1)

            local_score_0 = np.dot(local_descriptors_0, local_codebook_0)
            local_labels_0 = np.argsort(-np.abs(local_score_0), axis=1)
            local_score_1 = np.dot(local_descriptors_1, local_codebook_1)
            local_labels_1 = np.argsort(-np.abs(local_score_1), axis=1)
            local_labels = (local_labels_0[:, 0] * local_codebook_1.shape[-1] + \
                local_labels_1[:, 0]).tolist()            

            labels = {
                "global": [
                    global_labels_0,
                    global_labels_1,
                ],
                "local": local_labels, 
            }
        except Exception as err:
            cause = "Failed to generate descriptive label."
            error_detail = {
                "traceback": traceback.format_exc(),
                "error": repr(err)
            }
            raise InternalErrorException(cause=cause, detail=error_detail)
        
        return labels
    return Extract