from read_config import globalization_lang, service_code, exception_level
import json
import logging



global_error = {
    "400":{  # status code -> message
        "zh_CN":"参数请求错误",
        "zh_TW":"参数请求错误",
        "en_US":"Bad Request",
        "001":{ # service_code -> service_type
            "000":{  # error_code
                "zh_CN":"",
                "zh_TW":"参数请求错误",
                "en_US":"",
                "001":{ #cause
                    "zh_CN":"url error",
                    "zh_TW":"参数请求错误",
                    "en_US":"",  
                }
            }
        }
    },
    "500":{  # status code -> message
        "zh_CN":"服务器内部错误",
        "zh_TW":"服务器内部错误",
        "en_US":"Internal Server Error",
        "000":{  # service_code -> service_type

        }
    }
}


status_code_i18n = {
    "400":{  # status code -> message
        "zh_CN":"参数请求错误",
        "zh_TW":"参数请求错误",
        "en_US":"Bad Request"
    },
    "500":{  # status code -> message
        "zh_CN":"服务器内部错误",
        "zh_TW":"服务器内部错误",
        "en_US":"Internal Server Error"
    }
}

error_400_i18n = {
    "001":{  # error_code
        "zh_CN":"参数缺失",
        "zh_TW":"參數缺失",
        "en_US":"missing parameter"
    },
    "002":{
        "zh_CN":"参数类型错误",
        "zh_TW":"參數類型錯誤",
        "en_US":"parameter type error"
    },
    "003":{
        "zh_CN":"无效参数",
        "zh_TW":"無效參數",
        "en_US":"invalid parameter"
    }
}

error_500_i18n = {
    "000":{
        "zh_CN":"",
        "zh_TW":"",
        "en_US":""
    }
}




class BasicException(Exception):
    def __init__(self, cause, detail, error_code="000", cause_code_on=False):
        self.service_code = service_code
        self.language = globalization_lang
        self.exception_level = exception_level
        self.error_code = error_code
        self.cause_code_on = cause_code_on
        self.cause = cause
        self.detail_info = self.format_detail_info(detail)
        self.code = self.generate_9_error_code()
        self.message = self.format_message()
        
    def format_message(self):
        return status_code_i18n[str(self.status_code)][str(self.language)]

    def format_cause(self):
        return global_error[str(self.status_code)][str(self.error_code)][str(self.language)]

    def format_cause_ex(self):
        return global_error[str(self.status_code)][str(self.error_code)][str(self.cause_code)][str(self.language)]

    def format_detail(self):
        return global_error[str(self.status_code)][str(self.error_code)][str(self.cause_code)][str(self.detail_code)][str(self.language)]

    def format_string_message(self, detail):
        return detail
    
    def format_exception_message(self, detail):
        return detail
    
    def format_detail_info(self, detail):
        re_detail = detail
        if isinstance(detail, str):
            print("string")
            re_detail = self.format_string_message(detail)
        elif isinstance(detail, Exception):
            print("exception")
            re_detail = self.format_exception_message(detail)
        elif isinstance(detail, dict):
            re_detail = detail
        return re_detail

    def generate_9_error_code(self):
        return str(self.status_code)+str(self.service_code)+str(self.error_code)
    
    def generate_response(self):
        return_dict = {
            "code":int(self.code),
            "message":str(self.message),
            "cause":str(self.cause),
            "detail":str(self.detail_info)
        }
        return_message =  json.dumps(return_dict, ensure_ascii=False)
        logging.error(return_message)
        return return_message




class ParamsException(BasicException):
    def __init__(self, cause, detail, error_code="000", cause_code_on=False):
        self.status_code = 400
        super(ParamsException, self).__init__(cause, detail, error_code, cause_code_on)

class ParamsExceptionI18n(ParamsException):
    def __init__(self, detail, error_code):
        cause = error_400_i18n[str(error_code)][globalization_lang]
        super(ParamsExceptionI18n, self).__init__(cause, detail, error_code)




class MissingParamsException(ParamsExceptionI18n):
    def __init__(self, detail):
        super(MissingParamsException, self).__init__(detail=detail, error_code="001")
    
class ParamsWrongTypeException(ParamsExceptionI18n):
    def __init__(self, detail):
        super(ParamsWrongTypeException, self).__init__(detail=detail, error_code="002")

class InvalidParamsException(ParamsExceptionI18n):
    def __init__(self, detail):
        super(InvalidParamsException, self).__init__(detail=detail, error_code="003")







class InternalErrorException(BasicException):
    def __init__(self, cause, detail, error_code="000", cause_code_on=False):
        self.status_code = 500
        super(InternalErrorException, self).__init__(cause, detail, error_code, cause_code_on)

class InternalErrorExceptionI18n(InternalErrorException):
    def __init__(self, detail, error_code):
        cause = error_500_i18n[str(error_code)][globalization_lang]
        super(ParamsExceptionI18n, self).__init__(cause, detail, error_code)