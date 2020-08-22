import os
import time

from garden import settings
from django.http import JsonResponse
from rest_framework.response import Response
from rest_framework.decorators import api_view
from rest_framework import status
from garden_python.cosmetics import Cosmetics
from garden_python.mysql import GMysql

# Create your views here.
def imgUpload(request):
    if( request.method == 'POST'):
        file_obj = request.FILES.get('img', None)
        name = time.strftime("%Y%m%d%H%M%S", time.localtime()) + file_obj.name
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

@api_view(['GET'])
def Cosmetics_Search(request, search):
    print(search)
    return Response(status=status.HTTP_200_OK)

def test(request):
    print("test res")
    Lipstick_color_D = Cosmetics().Lipstick_color_D()   #色号识别
    Lipstick_color_recommend = Cosmetics().Lipstick_color_recommend()  #色号推荐
    select_brands = GMysql().select_brands()  #查询所有的品牌名
    select_series = GMysql().select_series()  #查询某个品牌名下的所有系列
    select_lipsticks = GMysql().select_lipsticks() #查询某个品牌名下某个系列的所有色号
    data = {
        'msg' : 'success',
        'data': {
            'Lipstick_color_D': Lipstick_color_D,
            'Lipstick_color_recommend': Lipstick_color_recommend,
            'select_brands': select_brands,
            'select_series': select_series,
            'select_lipsticks': select_lipsticks
        }
    }
    return JsonResponse(data)
