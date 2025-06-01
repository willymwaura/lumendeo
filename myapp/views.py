
from django.http import response
from django.shortcuts import render

from .models import Payment,MonthlyVideo
from django.shortcuts import render,redirect
from django.http import HttpResponse,JsonResponse
import os
from intasend import APIService
import json
from django.shortcuts import render, redirect
from .models import Payment, MonthlyVideo
   
from django.views.decorators.csrf import csrf_exempt


# Create your views here.

def index(request):
    latest_video = MonthlyVideo.objects.order_by('-id').first()
    context = {  
    'latest_video': latest_video,  # Send only the latest video
    }

    return render(request, 'newindex.html',context)
def movie_view(request):
    movie= MonthlyVideo.objects.order_by('-id').first()
    
    if not movie:
        return render(request, "index.html", {"error": "No movie found."})
    return render(request, "movies.html", {"movie": movie})


def mpesa_checkout(request):
    phone = request.POST.get('phone')
    amount = request.POST.get('amount')
    name= request.POST.get('name') or 'user'
    print("movie amount is ",amount)
    #phone='254112100378'
    # Remove any spaces or dashes just in case
    cleaned_phone = phone.strip().replace(" ", "").replace("-", "")

    # Convert to international format
    if cleaned_phone.startswith("0"):
        phone = "254" + cleaned_phone[1:]
    else:
        phone = cleaned_phone
    if not phone:
        return redirect('index')  # or handle error gracefully

    latest_movie = MonthlyVideo.objects.order_by('-id').first()
    if not latest_movie:
        return render(request, "index.html", {"error": "No movie available."})

    

    # Check for recent successful payment
    existing_payment = Payment.objects.filter(
        phone=phone,
        movie=latest_movie,
        status=True
    ).order_by('-timestamp').first()

    if existing_payment:
        return redirect('movie')  # to the movie page

    # No valid payment — initiate payment
    payment = Payment.objects.create(
        phone=phone,
        amount=amount,
        movie=latest_movie,
        name=name
    )

    try:
        token = "ISSecretKey_test_70b2ae8a-1268-40b8-b2b6-c77972dd202c"
        pub = "ISPubKey_test_2331371f-6916-4d83-847f-75fa8db0b2cd"
        service = APIService(token=token, publishable_key=pub, test=True)

        response = service.collect.mpesa_stk_push(
            phone_number=phone,
            narrative="Movie Payment",
            amount=amount,
            api_ref="movie-payment"
        )

        print(response)
        return render(request, "loading.html")

    except Exception as e:
        print("Payment error:", e)
        return render(request, "index.html", {"error": "Payment failed. Try again later."})



@csrf_exempt  
def PaymentCallback(request):
    try:
        data = json.loads(request.body)
    except json.JSONDecodeError:
        return JsonResponse({"error": "Invalid JSON data in the request."}, status=400)
    print(data)
    

        # Check if transaction state is complete
    if data["state"] == "COMPLETE"  and data["api_ref"] =="movie-payment":
        print("json gottens is ",data)
        account = data["account"]  # Get the account information from data

        # Initialize phone and email variables with None
        phone = None
        email = None

        try:
            int_account = int(account)  # Try converting account to an integer
            phone = (int_account)    # Convert the integer to a character (assuming this is intended for phone number processing)
            print(phone)
        except ValueError:
            # If account is not an integer, treat it as an email
            email = account
            print(email)

        if phone is not None:
            # Process payments based on phone number
            try:
                payment_instance = Payment.objects.filter(phone=phone).latest('id')
                payment_instance.status = 'True'
                payment_instance.save()
                return JsonResponse({"message": "Payment processed successfully."})

                
                
                

            except Payment.DoesNotExist:
                return JsonResponse({"message": "No payment found for this phone number."})
            
        else:
            return JsonResponse({"message": "No  phone number in the callback."})
    else:
        return JsonResponse({"message": "Payment not complete ."})


        
def checkpayment(request):
    return render(request,"payment.html")

def loader(request):

    return render(request,"loading.html")

def dashboard(request):
    return render(request,"dashboard.html")



import uuid
import boto3
from django.conf import settings
from django.http import JsonResponse
import mimetypes

def get_presigned_url(request):
    file_type = request.GET.get('content_type', 'video/mp4')
    s3 = boto3.client(
        's3',
        aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
        aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY,
        region_name=settings.AWS_S3_REGION_NAME
    )

    ext = mimetypes.guess_extension(file_type)
    filename = f"videos/{uuid.uuid4()}{ext or '.mp4'}"

    presigned_post = s3.generate_presigned_post(
        Bucket=settings.AWS_STORAGE_BUCKET_NAME,
        Key=filename,
        Fields={"Content-Type": file_type},
        Conditions=[{"Content-Type": file_type}],
        ExpiresIn=3600
    )

    return JsonResponse({
        'url': presigned_post['url'],
        'fields': presigned_post['fields'],
        'final_url': f"https://{settings.AWS_STORAGE_BUCKET_NAME}.s3.amazonaws.com/{filename}"
    })

