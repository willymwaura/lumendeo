from django.urls import path
from.import views




urlpatterns = [
    path('',views.index,name='index'),
    path('index',views.index,name='index'),
    path('mpesa_checkout',views.mpesa_checkout,name='mpesa_checkout'),
    path('paymentProcessing',views.PaymentCallback,name='paymentProcessing'),
    path('movie', views.movie_view, name='movie'),
    path('checkpayments',views.checkpayment,name='checkpayments'),
    path('loading',views.loader,name='loader'),
    path('dashboard',views.dashboard,name='dashboard'),
    path('api/start-upload/', views.create_multipart_upload, name='start_upload'),
path('api/presign-part/', views.generate_presigned_url, name='presign_part'),
path('api/complete-upload/', views.complete_multipart_upload, name='complete_upload'),

    path('upload-video/', views.upload_video, name='upload_video'),
        path('api/create-video/', views.create_video, name='create_video'),

]
   
   

