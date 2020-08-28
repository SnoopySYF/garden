from django.urls import path
from . import views
from django.views.static import serve

app_name='Cosmetics'
urlpatterns = [
    path('imgurl/upload/', views.imgUpload),
    path('<str:search>', views.Cosmetics_Search),
    path('test/', views.test, name='test')
]