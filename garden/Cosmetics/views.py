import os
import time
import math

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

from garden import settings
from django.http import JsonResponse
from rest_framework.response import Response
from rest_framework.decorators import api_view
from rest_framework import status
from Cosmetics.models import Brands
from Cosmetics.models import Series
from Cosmetics.models import Lipsticks
from Cosmetics.models import User_Brands
from Cosmetics.models import User_Series
from Cosmetics.models import User_Lipsticks
from Cosmetics.serializers import BrandsSerializer
from Cosmetics.serializers import SeriesSerializer
from Cosmetics.serializers import LipsticksSerializer
from Cosmetics.serializers import UserLipsticksSerializer

class Tool:
    def Str2RGB(self, s):
        R = int(s[0:2], 16)
        G = int(s[2:4], 16)
        B = int(s[4:6], 16)
        return R, G, B

    def Chromatic(self, R1, G1, B1, R2, G2, B2):
        r_mean = (R1 + R2)/2
        R = R1 - R2
        G = G1 - G2
        B = B1 - B2
        return math.sqrt((2+r_mean)/256*(R**2) + 4*(G**2) + (2+(255-r_mean)/256)*(B**2))
    
    def Select_gamut(self, s):
        results = Lipsticks.objects.filter(color_gamut = s)
        rs = LipsticksSerializer(results, many=True)
        return rs

    def Get_similiar_color(self, color):
        colors_rs = self.Select_gamut(color[0]).data
        R, G, B = self.Str2RGB(color)
        colors = [c for c in colors_rs]
        if(len(colors) == 0):
            return -1
        si_c = colors[0]['color']
        si_id = 0
        R1, G1, B1 = self.Str2RGB(si_c)
        min_c = self.Chromatic(R, G, B, R1, G1, B1)
        for i in range(1, len(colors)):
            c = colors[i]['color']
            R1, B1, G1 = self.Str2RGB(c)
            m_c = self.Chromatic(R, G, B, R1, G1, B1)
            if(m_c < min_c):
                si_c = c
                min_c = m_c
                si_id = i
        return colors[si_id]
        

class Cosmetics:
    
    def __init__(self):
        self.akkey = "LTAI4GBvsVgxXcFe2fa2cDho"
        self.assec = "b9yxczP7OPLfi7G2KDjkqKvYSsfNxN"
        self.client = AcsClient(self.akkey, self.assec, 'cn-shanghai')
        self.tool = Tool()
    
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
    def Face_makeup(self, img, ftype):
        request = FaceMakeupRequest()
        request.set_accept_format('json')

        request.set_MakeupType("whole")
        request.set_ResourceType(str(ftype))
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
    -1, -1: 照片不规范
    -2,-2 : 没有识别到该色号
    '''
    def Lipstick_color_recognize(self, file_path, suffix, isLocal):
        img = self.getImageUrl(file_path, suffix, isLocal)
        rs = self.DetecFace(img)
        if(0 == rs):
            color, la = self.Lipstick_color(img)
            si_color = self.tool.Get_similiar_color(color)
            if(si_color == -1):
                return -2
            rs = {'color':color, 'brands' : si_color['series_info']['brands']['name'], 'series': si_color['series_info']['name'], 'lipsticks':si_color['name']}
            return rs
        elif(rs > 0):
            color, la = self.lip_color(img)
            si_color = self.tool.Get_similiar_color(color)
            if(si_color == -1):
                return -2
            rs = {'color':color, 'brands' : si_color['series_info']['brands']['name'], 'series': si_color['series_info']['name'], 'lipsticks':si_color['name']}
            return rs
        else:
            print("error!")
            return -1

    '''
    口红色号推荐
    输入：
    file_path: 图片路径
    suffix：图片格式
    isLocal：图片是否在本地
    ftype: 美妆类型 1（基础妆）、2（少女妆）、3（活力妆）、4（优雅妆）、5（魅惑妆）、6（梅子妆）
    输出：
    0, 0  : 图片中没有人脸
    -1,-1 : 图片中有多个人脸
    -2,-2 : 没有识别到该色号
    颜色RGB码、标签
    '''
    def Lipstick_color_recommend(self, file_path, suffix, isLocal, ftype):
        img = self.getImageUrl(file_path, suffix, isLocal)
        rs = self.DetecFace(img)
        if(0 == rs):
            return 0
        elif(1 == rs):
            img_make_up = self.Face_makeup(img, ftype)
            color, la = self.lip_color(img_make_up)
            si_color = self.tool.Get_similiar_color(color)
            if(si_color == -1):
                return -2
            rs = {'color':color, 'brands' : si_color['series_info']['brands']['name'], 'series': si_color['series_info']['name'], 'lipsticks':si_color['name']}
            return rs
        else:
            return -1

class GMysql:

    """
    查询所有的品牌名
    返回集合：
    b_id: 品牌id
    b_name: 品牌名
    """
    def select_brands(self):
        results = Brands.objects.all()
        rs = BrandsSerializer(results, many=True)
        return rs

    """
    查询某个品牌名下的所有系列
    输入：
    b_id: 品牌id
    返回集合：
    s_id: 系列id
    s_name: 系列名
    b_id: 品牌id
    """
    def select_series(self, b_id):
        results = Series.objects.filter(brands = b_id)
        rs = SeriesSerializer(results, many=True)
        return rs

    """
    查询某个品牌名下某个系列的所有色号
    输入：
    s_id: 系列id
    返回集合：
    l_id: 色号id
    color: 色号RGB
    id: 该色号id信息
    l_name: 该色号名字
    s_id: 系列id
    """
    def select_lipsticks(self, s_id):
        results = Lipsticks.objects.filter(series = s_id)
        rs = LipsticksSerializer(results, many=True)
        return rs

    """
    查询所有的用户收藏品牌名
    返回集合：
    b_id: 品牌id
    b_name: 品牌名
    """
    def select_user_brands(self):
        results = User_Brands.objects.all()
        rs = BrandsSerializer(results, many=True)
        return rs

    """
    查询某个用户收藏品牌名下的所有系列
    输入：
    b_id: 品牌id
    返回集合：
    s_id: 系列id
    s_name: 系列名
    b_id: 品牌id
    """
    def select_user_series(self, b_id):
        results = User_Series.objects.filter(brands = b_id)
        rs = SeriesSerializer(results, many=True)
        return rs

    """
    查询用户收藏某个品牌名下某个系列的所有色号
    输入：
    s_id: 系列id
    返回集合：
    l_id: 色号id
    color: 色号RGB
    id: 该色号id信息
    l_name: 该色号名字
    s_id: 系列id
    """
    def select_user_lipsticks(self, s_id):
        results = User_Lipsticks.objects.filter(series = s_id)
        rs = UserLipsticksSerializer(results, many=True)
        return rs

    """
    向用户收藏中添加数据
    输入：lid ：色号id
    """
    def Insert_user_lipsticks(self, lid):
        lips = Lipsticks.objects.filter(l_id = lid)
        lip = LipsticksSerializer(lips, many=True).data
        b_id, b_name, s_id, s_name = lip[0]['series_info']['brands']['b_id'], lip[0]['series_info']['brands']['name'], lip[0]['series_info']['s_id'], lip[0]['series_info']['name']
        ser = Series.objects.filter(s_id = s_id)
        bra = Brands.objects.filter(b_id = b_id)
        b = User_Brands.objects.create(b_id = b_id, name = b_name)
        s = User_Series.objects.create(s_id = s_id, name = s_name, brands = b)
        User_Lipsticks.objects.create(l_id = lip[0]['l_id'], color = lip[0]['color'], id = lip[0]['id'], name = lip[0]['name'], series = s)

    """
    删除用户收藏的某个数据
    """
    def Delete_user_lipsticks(self, bid, sid, lid):
        User_Lipsticks.objects.filter(l_id = lid).delete()
        User_Series.objects.filter(s_id = sid).delete()
        User_Brands.objects.filter(b_id = bid).delete()

    """
    查询用户收藏中是否有该色号
    输入：lid
    返回：
    1 存在
    0 不存在
    """
    def Query_user_lipsticks(self, lid):
        if(User_Lipsticks.objects.filter(l_id = lid)):
            return 1
        return 0
        

# Create your views here.
@api_view(['POST'])
def imgUpload(request):
    if( request.method == 'POST'):
        file_obj = request.FILES.get('image', None)
        name = time.strftime("%Y%m%d%H%M%S", time.localtime()) + ".jpg"
        file_path = os.path.join(settings.UPLOAD_FILE, name)
        f = open(file_path, 'wb')
        for i in file_obj.chunks():
            f.write(i)
        f.close()
        dict = {
            'msg': 'success',
            'img_path': name
        }
        return JsonResponse(dict)
    return Response(status=status.HTTP_400_BAD_REQUEST)

@api_view(['GET'])
def Recognize(request, filePath):
    cos = Cosmetics()
    if(request.method == 'GET'):
        fp = "upload/" + filePath + ".jpg"
        res = cos.Lipstick_color_recognize(file_path=fp, suffix='jpg', isLocal=True)
        if(isinstance(res, int)):
            return Response(status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        return Response(res)
    return Response(status=status.HTTP_400_BAD_REQUEST)

@api_view(['GET'])
def Recommend(request, filePath, ftype):
    cos = Cosmetics()
    if(request.method == 'GET'):
        fp = "upload/" + filePath + ".jpg"
        res = cos.Lipstick_color_recommend(file_path=fp, suffix='jpg', isLocal=True, ftype=ftype)
        if(isinstance(res, int)):
            return Response(status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        return Response(res)
    return Response(status=status.HTTP_400_BAD_REQUEST)

@api_view(['GET'])
def Brands_operation(request):
    Gmysql = GMysql()
    if(request.method == 'GET'):
        try:
            select_brands = Gmysql.select_brands().data
        except BaseException:
            return Response(status=status.HTTP_404_NOT_FOUND)
        return Response(select_brands)
    return Response(status=status.HTTP_400_BAD_REQUEST)

@api_view(['GET'])
def Series_operation(request, b_id):
    Gmysql = GMysql()
    if(request.method == 'GET'):
        try:
            select_series = Gmysql.select_series(b_id=b_id).data
        except BaseException:
            return Response(status=status.HTTP_404_NOT_FOUND)
        return Response(select_series)
    return Response(status=status.HTTP_400_BAD_REQUEST)

@api_view(['GET'])
def Lipsticks_operation(request, s_id):
    Gmysql = GMysql()
    if(request.method == 'GET'):
        try:
            select_lipsticks = Gmysql.select_lipsticks(s_id=s_id).data
        except BaseException:
            return Response(status=status.HTTP_404_NOT_FOUND)
        return Response(select_lipsticks)
    return Response(status=status.HTTP_400_BAD_REQUEST)

@api_view(['GET'])
def User_brands_operation(request):
    Gmysql = GMysql()
    if(request.method == 'GET'):
        try:
            select_user_brands = Gmysql.select_user_brands().data
        except BaseException:
            return Response(status=status.HTTP_404_NOT_FOUND)
        return Response(select_user_brands)
    return Response(status=status.HTTP_400_BAD_REQUEST)

@api_view(['GET'])
def User_series_operation(request, b_id):
    Gmysql = GMysql()
    if(request.method == 'GET'):
        try:
            select_user_series = Gmysql.select_user_series(b_id=b_id).data
        except BaseException:
            return Response(status=status.HTTP_404_NOT_FOUND)
        return Response(select_user_series)
    return Response(status=status.HTTP_400_BAD_REQUEST)

@api_view(['GET'])
def User_lipsticks_operation(request, s_id):
    Gmysql = GMysql()
    if(request.method == 'GET'):
        try:
            select_user_lipsticks = Gmysql.select_user_lipsticks(s_id=s_id).data
        except BaseException:
            return Response(status=status.HTTP_404_NOT_FOUND)
        return Response(select_user_lipsticks)
    return Response(status=status.HTTP_400_BAD_REQUEST)

@api_view(['POST'])
def User_insert(request, lid):
    Gmysql = GMysql()
    if(request.method == 'POST'):
        try:
            Gmysql.Insert_user_lipsticks(lid=lid)
        except BaseException:
            return Response(status=status.HTTP_404_NOT_FOUND)
        return Response(status=status.HTTP_200_OK)
    return Response(status=status.HTTP_400_BAD_REQUEST)

@api_view(['DELETE'])
def User_delete(request, bid, sid, lid):
    Gmysql = GMysql()
    if(request.method == 'DELETE'):
        try:
            Gmysql.Delete_user_lipsticks(bid=bid, sid=sid, lid=lid)
        except BaseException:
            return Response(status=status.HTTP_404_NOT_FOUND)
        return Response(status=status.HTTP_200_OK)
    return Response(status=status.HTTP_400_BAD_REQUEST)

@api_view(['GET'])
def User_comfirm(request, lid):
    Gmysql = GMysql()
    if(request.method == 'GET'):
        try:
            res = Gmysql.Query_user_lipsticks(lid=lid)
        except BaseException:
            return Response({'res':res}) 
        return Response(status=status.HTTP_200_OK)
    return Response(status=status.HTTP_400_BAD_REQUEST)

def test(request):
    print("test res")
    cos = Cosmetics()
    Gmysql = GMysql()
    tool = Tool()
    color1 = cos.Lipstick_color_recognize(file_path='D:/contest/ALBB/garden_code/garden/garden_python/image/2.jpg', suffix='jpg', isLocal=True)   #色号识别
    color2 = cos.Lipstick_color_recommend(file_path='D:/contest/ALBB/garden_code/garden/garden_python/image/2.jpg', suffix='jpg', isLocal=True, ftype=2)  #色号推荐
    select_brands = Gmysql.select_brands().data  #查询所有的品牌名
    select_series = Gmysql.select_series(b_id=1).data  #查询某个品牌名下的所有系列
    select_lipsticks = Gmysql.select_lipsticks(s_id=1).data #查询某个品牌名下某个系列的所有色号
    select_user_brands = Gmysql.select_user_brands().data  #查询所有的品牌名
    select_user_series = Gmysql.select_user_series(b_id=1).data  #查询某个品牌名下的所有系列
    select_user_lipsticks = Gmysql.select_user_lipsticks(s_id=1).data #查询某个品牌名下某个系列的所有色号
    color = tool.Get_similiar_color("A132E1")
    # Gmysql.Insert_user_lipsticks(1)
    Gmysql.Delete_user_lipsticks(1, 1, 1)
    rs = Gmysql.Query_user_lipsticks(2)
    data = {
        'msg' : 'success',
        'data': {
            'color1': color1,
            'color2': color2,
            'select_brands': select_brands,
            'select_series': select_series,
            'select_lipsticks': select_lipsticks,
            'select_user_brands': select_user_brands,
            'select_user_series': select_user_series,
            'select_user_lipsticks': select_user_lipsticks,
            'color': color,
            'rs': rs
        }
    }
    return JsonResponse(data)
