#coding=utf-8
from configparser import ConfigParser

from aliyunsdkcore.client import AcsClient
from aliyunsdkcore.acs_exception.exceptions import ClientException
from aliyunsdkcore.acs_exception.exceptions import ServerException
from aliyunsdkimagerecog.request.v20190930.RecognizeImageColorRequest import RecognizeImageColorRequest
from aliyunsdkimageseg.request.v20191230.ParseFaceRequest import ParseFaceRequest
from aliyunsdkimageseg.request.v20191230.SegmentCommodityRequest import SegmentCommodityRequest
from aliyunsdkfacebody.request.v20191230.FaceMakeupRequest import FaceMakeupRequest
from aliyunsdkfacebody.request.v20191230.DetectFaceRequest import DetectFaceRequest
# from aliyunsdkviapiutils.request.v20200401.GetOssStsTokenRequest import FileUtils
from viapi.fileutils import FileUtils

import os

# def readKS():
#     conn = ConfigParser()
#     file_path = os.path.join(os.path.abspath('.'), 'config.ini')
#     if(not os.path.exists(file_path)):
#         raise FileNotFoundError("文件不存在")

#     conn.read(file_path)
#     akkey = conn.get('root', 'akkey')
#     assec = conn.get('root', 'assec')
#     return akkey, assec
class Cosmetics:

    def __init__(self):
        self.akkey = "LTAI4GBvsVgxXcFe2fa2cDho"
        self.assec = "b9yxczP7OPLfi7G2KDjkqKvYSsfNxN"
        self.client = AcsClient(self.akkey, self.assec, 'cn-shanghai')

    
    '''
    将图片转化为网址链接
    '''
    def getImageUrl(self, file_path, suffix, isLocal):
        file_utils = FileUtils(self.akkey, self.assec)
        oss_url = file_utils.get_oss_url(file_path, suffix, isLocal)
        return oss_url

    '''
    检测图片中是否有人脸
    '''
    def DetecFace(self, img):
        request = DetectFaceRequest()
        request.set_accept_format('json')
        request.set_ImageURL(img)
        response = self.client.do_action_with_exception(request)
        rs = str(response, encoding='utf-8')
        rs = eval(rs)
        return rs['Data']['FaceCount']

    '''
    颜色识别
    '''
    def Color_Request(self, img):
        request = RecognizeImageColorRequest()
        request.set_accept_format('json')
        request.set_ColorCount("1")
        request.set_Url(img)
        response = self.client.do_action_with_exception(request)
        rs = str(response, encoding='utf-8')
        rs = eval(rs)
        #print(rs['Data']['ColorTemplateList'][0]['Color'])
        return rs['Data']['ColorTemplateList'][0]['Color'], rs['Data']['ColorTemplateList'][0]['Label']

    '''
    面部分割
    '''
    def Face_Request(self, img):
        request = ParseFaceRequest()
        request.set_accept_format('json')
        request.set_ImageURL(img)
        response = self.client.do_action_with_exception(request)
        rs = str(response, encoding='utf-8')
        rs = eval(rs)
        return rs
    
    def lip_color(self, img):
        face = self.Face_Request(img)
        face_img = face['Data']['Elements']
        lip = dict()
        for i in range(len(face_img)-1, -1, -1):
            if(face_img[i]['Name'] == "l_lip"):
                lip['l_lip'] = face_img[i]['ImageURL']
            elif(face_img[i]['Name'] == "u_lip"):
                lip['u_lip'] = face_img[i]['ImageURL']
            if(len(lip) == 2):
                break
        l_lip_color, l_lip_color_label = self.Color_Request(lip['l_lip']) 
        u_lip_color, u_lip_color_label = self.Color_Request(lip['u_lip']) 
        return l_lip_color, l_lip_color_label

    '''
    口红分割
    '''
    def Lipstick_seg(self, img):
        request = SegmentCommodityRequest()
        request.set_accept_format('json')
        request.set_ImageURL(img)
        response = self.client.do_action_with_exception(request)
        rs = str(response, encoding='utf-8')
        rs = eval(rs)
        return rs['Data']['ImageURL']

    '''
    美妆
    '''
    def Face_makeup(self, img):
        request = FaceMakeupRequest()
        request.set_accept_format('json')

        request.set_MakeupType("whole")
        request.set_ResourceType("2")
        request.set_Strength("1")
        request.set_ImageURL(img)

        response = self.client.do_action_with_exception(request)
        rs = str(response, encoding='utf-8')
        rs = eval(rs)
        return rs['Data']['ImageURL']

    '''
    嘴唇上口红色号识别
    输入：
    file_path: 图片路径
    suffix：图片格式
    isLocal：图片是否在本地
    '''
    def Face_lip_color(self, file_path, suffix, isLocal):
        img = self.getImageUrl(file_path, suffix, isLocal)
        color, label = self.lip_color(img)
        return color, label

    '''
    实物口红色号识别
    '''
    def Lipstick_color(self, img):
        img_seg = self.Lipstick_seg(img)
        color, label = self.Color_Request(img_seg)
        return color, label

    '''
    色号识别，会自动判断图片为人脸还是物品
    输入：
    file_path: 图片路径
    suffix：图片格式
    isLocal：图片是否在本地
    输出：
    颜色RGB码、标签
    '''
    def Lipstick_color_D(self, file_path, suffix, isLocal):
        img = self.getImageUrl(file_path, suffix, isLocal)
        rs = self.DetecFace(img)
        if(0 == rs):
            color, label = self.Lipstick_color(img)
            return color, label
        elif(rs > 0):
            color, label = self.lip_color(img)
            return color, label
        else:
            print("error!")
            return

    '''
    口红色号推荐
    输入：
    file_path: 图片路径
    suffix：图片格式
    isLocal：图片是否在本地
    输出：
    颜色RGB码、标签
    '''
    def Lipstick_color_recommend(self, file_path, suffix, isLocal):
        img = self.getImageUrl(file_path, suffix, isLocal)
        img_make_up = self.Face_makeup(img)
        color, label = self.lip_color(img_make_up)
        return color, label

if __name__ == "__main__":
    cosmetics = Cosmetics()
    color, label = cosmetics.Lipstick_color_D("./image/5.jpg", "jpg", True)
    print(color)
    print(label)

