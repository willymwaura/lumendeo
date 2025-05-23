from django.urls import path
from.import views

urlpatterns = [
    path('',views.index,name='index'),
    path('index',views.index,name='index'),
    path('mpesa_checkout',views.mpesa_checkout,name='mpesa_checkout'),
    path('paymentProcessing',views.PaymentCallback,name='paymentProcessing'),
    path('movie', views.movie_view, name='movie'),
    path('checkpayments',views.checkpayment,name='checkpayments'),
    path('loading',views.loader,name='loader')
   
   
]
