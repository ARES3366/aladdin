import numpy as np
from protos.tensorflow.core.framework import tensor_pb2
from protos.tensorflow.core.framework import tensor_shape_pb2
from protos.tensorflow.core.framework import types_pb2
from protos.tensorflow_serving.apis import predict_pb2
from protos.tensorflow_serving.apis import prediction_service_pb2_grpc
from read_config import tfserving_config
import asyncio
import grpc


class DLRequest(object):
    def __init__(self, request, stub):
        self.request_id = id(request)
        self.request = request
        self.response = stub.Predict.future(self.request, 1000.0)
        self.message = None

    def set_result(self, result):
        self.response = result
        # self.code = result

class BaseClient(object):
    def __init__(self):
        # print(tfserving_config["tfserving_host"]+ ":"+ tfserving_config["tfserving_port"])
        self.channel = grpc.insecure_channel(tfserving_config["tfserving_host"]+ ":"+ tfserving_config["tfserving_port"],options=[
        ('grpc.max_send_message_length', 100*1024*1024),
        ('grpc.max_receive_message_length', 300*1024*1024),
    ])
        self.stub = prediction_service_pb2_grpc.PredictionServiceStub(self.channel)
        self.task_queue = {}

    async def inference(self, model_name, signature_name, input_data, output_list):
        len_of_input = len(input_data)
        len_of_output = len(output_list)
        request = predict_pb2.PredictRequest()
        request.model_spec.name = model_name
        request.model_spec.signature_name = signature_name
        for input_name, input_value in input_data.items():

            dims = [tensor_shape_pb2.TensorShapeProto.Dim(size=dim) for dim in input_value["data"].shape]
            t_shape = tensor_shape_pb2.TensorShapeProto(dim=dims)
            dtype = input_value["dtype"]
            if dtype == 1:
                input_tensor_protos = tensor_pb2.TensorProto(
                    dtype=input_value["dtype"],
                    tensor_shape=t_shape,
                    float_val=input_value["data"].reshape(-1).tolist()
                )
            elif dtype == 3:
                input_tensor_protos = tensor_pb2.TensorProto(
                    dtype=input_value["dtype"],
                    tensor_shape=t_shape,
                    int_val=input_value["data"].reshape(-1).tolist()
                )
            else:
                input_tensor_protos = tensor_pb2.TensorProto(
                    dtype=input_value["dtype"],
                    tensor_shape=t_shape,
                    float_val=input_value["data"].reshape(-1).tolist()
                )
            request.inputs[input_name].CopyFrom(input_tensor_protos)
        dl_request = DLRequest(request, self.stub)
        result = dl_request.response.result()
        result = result.outputs
        result_dict = {}
        for output_name in output_list:
            output_data = result[output_name]
            result_dict[output_name] = {}
            result_dict[output_name]["dtype"] = output_data.dtype
            result_dict[output_name]["shape"] = [size_item.size for size_item in output_data.tensor_shape.dim]
            result_dict[output_name]["value"] = output_data.float_val
        return result_dict
    def inference_sync(self, model_name, signature_name, input_data, output_list):
        len_of_input = len(input_data)
        len_of_output = len(output_list)
        request = predict_pb2.PredictRequest()
        request.model_spec.name = model_name
        request.model_spec.signature_name = signature_name
        for input_name, input_value in input_data.items():
            dims = [tensor_shape_pb2.TensorShapeProto.Dim(size=dim) for dim in input_value["data"].shape]
            t_shape = tensor_shape_pb2.TensorShapeProto(dim=dims)
            dtype = input_value["dtype"]
            if dtype == 1:
                input_tensor_protos = tensor_pb2.TensorProto(
                    dtype=input_value["dtype"],
                    tensor_shape=t_shape,
                    float_val=input_value["data"].reshape(-1).tolist()
                )
            elif dtype == 3:
                input_tensor_protos = tensor_pb2.TensorProto(
                    dtype=input_value["dtype"],
                    tensor_shape=t_shape,
                    int_val=input_value["data"].reshape(-1).tolist()
                )
            else:
                input_tensor_protos = tensor_pb2.TensorProto(
                    dtype=input_value["dtype"],
                    tensor_shape=t_shape,
                    float_val=input_value["data"].reshape(-1).tolist()
                )
            request.inputs[input_name].CopyFrom(input_tensor_protos)
        dl_request = DLRequest(request, self.stub)
        response = self.stub.Predict(request, 1000.0)
        # result = dl_request.response.result()
        result = response.outputs
        result_dict = {}
        for output_name in output_list:
            output_data = result[output_name]
            result_dict[output_name] = {}
            result_dict[output_name]["dtype"] = output_data.dtype
            result_dict[output_name]["shape"] = [size_item.size for size_item in output_data.tensor_shape.dim]
            result_dict[output_name]["value"] = output_data.float_val
        return result_dict

base_client = BaseClient()
