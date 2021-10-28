import sys
import unittest
from match_image.check_parameters import *


def SetTestImage():
    image_path = sys.path[0] + "/image000.jpg"
    with open(image_path, "rb") as f:
        image = f.read()
    return image
    
def CatchMissingParamsError(CheckFunc, error):
    try:
        result = CheckFunc(error)
        return False
    except BaseException as err:
        ifcondi_1 = bool(err.code[:3] == "400")
        ifcondi_2 = bool(err.code[-3:] == "001")
        if ifcondi_1 and ifcondi_2:
            return True
        else:
            print(f"Error_Code: {err.code}, Error_Cause: {err.cause}")
            return False

def CatchParamsTypeError(CheckFunc, error):
    try:
        result = CheckFunc(error)
        return False
    except BaseException as err:
        ifcondi_1 = bool(err.code[:3] == "400")
        ifcondi_2 = bool(err.code[-3:] == "002")
        if ifcondi_1 and ifcondi_2:
            return True
        else:
            print(f"Error_Code: {err.code}, Error_Cause: {err.cause}")
            return False

def CatchInvalidParamsError(CheckFunc, error):
    try:
        result = CheckFunc(error)
        return False
    except BaseException as err:
        ifcondi_1 = bool(err.code[:3] == "400")
        ifcondi_2 = bool(err.code[-3:] == "003")
        if ifcondi_1 and ifcondi_2:
            return True
        else:
            print(f"Error_Code: {err.code}, Error_Cause: {err.cause}")
            return False


class TestChechParameters(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        pass

    @classmethod
    def tearDownClass(cls):
        pass

    def testCheckParamsIndexPost(self):
        # ===============================================================
        # 必要参数（'label'）缺失错误
        params = dict(
            image=str(base64.b64encode(SetTestImage()), encoding="utf-8"), 
        )
        self.assertTrue(CatchMissingParamsError(CheckIndexPost, params))
        # ===============================================================
        # 必要参数（'image'）缺失错误
        params = dict(
            label=str(b"There is a label.", encoding="utf-8"),
        )
        self.assertTrue(CatchMissingParamsError(CheckIndexPost, params))
        # ===============================================================
        # 必要参数（'label', 'image'）同时缺失错误
        params = dict()
        self.assertTrue(CatchMissingParamsError(CheckIndexPost, params))
        # ===============================================================
        # 必要参数（'label'）整型类型错误
        params = dict(
            image=str(base64.b64encode(SetTestImage()), encoding="utf-8"), 
            label=int(123456), 
        )
        self.assertTrue(CatchParamsTypeError(CheckIndexPost, params))
        # ===============================================================
        # 必要参数（'label'）布尔类型错误
        params = dict(
            image=str(base64.b64encode(SetTestImage()), encoding="utf-8"), 
            label=False, 
        )
        self.assertTrue(CatchParamsTypeError(CheckIndexPost, params))
        # ===============================================================
        # 必要参数（'label'）None类型错误
        params = dict(
            image=str(base64.b64encode(SetTestImage()), encoding="utf-8"), 
            label=None, 
        )
        self.assertTrue(CatchParamsTypeError(CheckIndexPost, params))
        # ===============================================================
        # 必要参数（'image'）整型类型错误
        params = dict(
            image=int(123456), 
            label=str(b"There is a label.", encoding="utf-8"),
        )
        self.assertTrue(CatchParamsTypeError(CheckIndexPost, params))
        # ===============================================================
        # 必要参数（'image'）布尔类型错误
        params = dict(
            image=False,
            label=str(b"There is a label.", encoding="utf-8"),
        )
        self.assertTrue(CatchParamsTypeError(CheckIndexPost, params))
        # ===============================================================
        # 必要参数（'image'）None类型错误
        params = dict(
            image=None,
            label=str(b"There is a label.", encoding="utf-8"),
        )
        self.assertTrue(CatchParamsTypeError(CheckIndexPost, params))
        # ===============================================================
        # 必要参数（'image'）无效错误：非图片base64编码字符串
        params = dict(
            image=str(base64.b16encode(SetTestImage()), encoding="utf-8"),
            label=str(b"There is a label.", encoding="utf-8"),
        )
        self.assertTrue(CatchInvalidParamsError(CheckIndexPost, params))
        # ===============================================================
        # 必要参数（'image'）无效错误：图片base64编码字符缺失
        params = dict(
            image=str(base64.b64encode(SetTestImage()), encoding="utf-8")[:100],
            label=str(b"There is a label.", encoding="utf-8"),
        )
        self.assertTrue(CatchInvalidParamsError(CheckIndexPost, params))

    def testCheckParamsIndexDelete(self):
        # ===============================================================
        # 必要参数（'labels'）缺失错误
        params = dict()
        self.assertTrue(CatchMissingParamsError(CheckIndexDelete, params))
        # ===============================================================
        # 必要参数（'labels'）整型类型错误
        params = dict(
            labels=int(123456), 
        )
        self.assertTrue(CatchParamsTypeError(CheckIndexDelete, params))
        # ===============================================================
        # 必要参数（'labels'）布尔类型错误
        params = dict(
            labels=False, 
        )
        self.assertTrue(CatchParamsTypeError(CheckIndexDelete, params))
        # ===============================================================
        # 必要参数（'labels'）None类型错误
        params = dict(
            labels=None, 
        )
        self.assertTrue(CatchParamsTypeError(CheckIndexDelete, params))
        # ===============================================================
        # 必要参数（'labels'）字符串类型错误
        params = dict(
            labels=str(b"There is a label.", encoding="utf-8"),
        )
        self.assertTrue(CatchParamsTypeError(CheckIndexDelete, params))
        # ===============================================================
        # 必要参数（'labels'）元素整型类型错误
        params = dict(
            labels=[1, 2, 3, 4],
        )
        self.assertTrue(CatchParamsTypeError(CheckIndexDelete, params))
        # ===============================================================
        # 必要参数（'labels'）元素布尔类型错误
        params = dict(
            labels=[False, str(b"There is a label.", encoding="utf-8")],
        )
        self.assertTrue(CatchParamsTypeError(CheckIndexDelete, params))
        # ===============================================================
        # 必要参数（'labels'）元素None类型错误
        params = dict(
            labels=[None, str(b"There is a label.", encoding="utf-8")],
        )
        self.assertTrue(CatchParamsTypeError(CheckIndexDelete, params))

    def testCheckParamsSearchPost(self):
        # ===============================================================
        # 必要参数（'image'）缺失错误
        params = dict()
        self.assertTrue(CatchMissingParamsError(CheckSearchPost, params))
        # ===============================================================
        # 必要参数（'image'）整型类型错误
        params = dict(
            image=int(123456), 
        )
        self.assertTrue(CatchParamsTypeError(CheckSearchPost, params))
        # ===============================================================
        # 必要参数（'image'）布尔类型错误
        params = dict(
            image=False,
        )
        self.assertTrue(CatchParamsTypeError(CheckSearchPost, params))
        # ===============================================================
        # 必要参数（'image'）None类型错误
        params = dict(
            image=None,
        )
        self.assertTrue(CatchParamsTypeError(CheckSearchPost, params))
        # ===============================================================
        # 必要参数（'image'）无效错误：非图片base64编码字符串
        params = dict(
            image=str(base64.b16encode(SetTestImage()), encoding="utf-8"),
        )
        self.assertTrue(CatchInvalidParamsError(CheckSearchPost, params))
        # ===============================================================
        # 必要参数（'image'）无效错误：图片base64编码字符缺失
        params = dict(
            image=str(base64.b64encode(SetTestImage()), encoding="utf-8")[:100],
        )
        self.assertTrue(CatchInvalidParamsError(CheckSearchPost, params))

if __name__ == "__main__":
    unittest.main()