import os
import time

from garden import settings
from django.http import JsonResponse
from rest_framework.response import Response
from rest_framework.decorators import api_view
from rest_framework import status

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
    return JsonResponse({'status': 'OK'})
