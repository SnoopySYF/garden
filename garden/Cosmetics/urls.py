from django.urls import path
from . import views
from django.views.static import serve

app_name='Cosmetics'
urlpatterns = [
    path('imgurl/walfare/', views.imgUpload),
    path('test/', views.test, name='test'),
    path('recognize/<str:filePath>/', views.Recognize),
    path('recommend/<str:filePath>/<str:ftype>', views.Recommend),
    path('brands/', views.Brands_operation),
    path('series/<int:b_id>/', views.Series_operation),
    path('lipsticks/<int:s_id>/', views.Lipsticks_operation),
    path('userbrands/', views.User_brands_operation),
    path('user_series/<int:b_id>/', views.User_series_operation),
    path('user_lipsticks/<int:s_id>/', views.User_lipsticks_operation),
    path('user_insert/<int:lid>/', views.User_insert),
    path('user_delete/bid/<int:bid>/sid/<int:sid>/lid/<int:lid>/', views.User_delete),
    path('user_comfirm/<int:lid>/', views.User_comfirm)
]