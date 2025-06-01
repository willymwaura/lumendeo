from django.urls import path
from.import views
from .views import get_presigned_url

urlpatterns = [
    path('',views.index,name='index'),
    path('index',views.index,name='index'),
    path('mpesa_checkout',views.mpesa_checkout,name='mpesa_checkout'),
    path('paymentProcessing',views.PaymentCallback,name='paymentProcessing'),
    path('movie', views.movie_view, name='movie'),
    path('checkpayments',views.checkpayment,name='checkpayments'),
    path('loading',views.loader,name='loader'),
    path('dashboard',views.dashboard,name='dashboard'),
    path('api/upload-url/', get_presigned_url, name='get_presigned_url'),
   
   
]
