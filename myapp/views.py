
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
from django.db.models import Sum
def dashboard(request):
    total_users = Payment.objects.values('phone').distinct().count()
    total_content_items = MonthlyVideo.objects.count()
    total_revenue = Payment.objects.filter(status=True).aggregate(Sum('amount'))['amount__sum'] or 0

    # Get the latest uploaded movie
    latest_movie = MonthlyVideo.objects.order_by('-date_uploaded').first()

    # Count unique users who paid for the latest movie
    active_sessions = 0
    if latest_movie:
        active_sessions = Payment.objects.filter(status=True, movie=latest_movie).values('phone').distinct().count()

    recent_activity = Payment.objects.select_related('movie').order_by('-timestamp')[:5]

    context = {
        'total_users': total_users,
        'total_content_items': total_content_items,
        'active_sessions': active_sessions,
        'total_revenue': total_revenue,
        'recent_activity': recent_activity,
    }
    return render(request,"dashboard.html",context)


from django.http import JsonResponse
@csrf_exempt
def create_video(request):
    try:
        # Extract fields from request
        video_url = request.POST.get("video")
        trailer_url = request.POST.get("trailer")
        title = request.POST.get("title")
        thumbnail = request.FILES.get("thumbnail")
        year_published = request.POST.get("year_published")
        introduction = request.POST.get("introduction")
        expire_date = request.POST.get("expire_date")
        cast = request.POST.get("cast")
        theme = request.POST.get("theme")
        length = request.POST.get("length", "2.0")
        movie_type = request.POST.get("movie_type", "drama")

        # Validate required fields
        if not all([video_url, trailer_url, title, thumbnail]):
            return JsonResponse({"error": "Missing required fields."})

        # Create MonthlyVideo instance
        video = MonthlyVideo.objects.create(
            title=title,
            video=video_url,
            trailer=trailer_url,
            thumbnail=thumbnail,
            year_published=year_published,
            introduction=introduction,
            expire_date=expire_date,
            cast=cast,
            theme=theme,
            length=length,
            movie_type=movie_type
        )

        # Return success response
        return JsonResponse({"success": True, "id": video.id})

    except Exception as e:
        # Return error response on exception
        return JsonResponse({"error": str(e)})



import boto3
import uuid
import json
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.conf import settings
from django.views.decorators.http import require_POST

# Initialize S3 client
s3_client = boto3.client(
    's3',
    aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
    aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY,
    region_name=settings.AWS_REGION
)

@csrf_exempt
@require_POST
def create_multipart_upload(request):
    body = json.loads(request.body)
    file_name = body.get('file_name')
    content_type = body.get('content_type')

    print("⏳ Starting multipart upload...")
    print(f"📁 Received file name: {file_name}")
    print(f"📦 Content type: {content_type}")

    if not file_name or not content_type:
        print("❌ Missing parameters.")
        return JsonResponse({'error': 'Missing parameters'}, status=400)

    key = f"uploads/{uuid.uuid4()}_{file_name}"
    print(f"🔑 Generated S3 key: {key}")

    response = s3_client.create_multipart_upload(
        Bucket=settings.AWS_STORAGE_BUCKET_NAME,
        Key=key,
        ContentType=content_type
    )

    print("✅ Multipart upload initiated.")
    print(f"🆔 Upload ID: {response['UploadId']}")

    return JsonResponse({
        'upload_id': response['UploadId'],
        'key': key
    })


@csrf_exempt
@require_POST
def generate_presigned_url(request):
    body = json.loads(request.body)
    upload_id = body.get('upload_id')
    key = body.get('key')
    part_number = body.get('part_number')

    print("🔗 Generating presigned URL...")
    print(f"🆔 Upload ID: {upload_id}")
    print(f"🔑 Key: {key}")
    print(f"🔢 Part number: {part_number}")

    if not upload_id or not key or not part_number:
        print("❌ Missing parameters.")
        return JsonResponse({'error': 'Missing parameters'}, status=400)

    url = s3_client.generate_presigned_url(
        'upload_part',
        Params={
            'Bucket': settings.AWS_STORAGE_BUCKET_NAME,
            'Key': key,
            'UploadId': upload_id,
            'PartNumber': int(part_number)
        },
        ExpiresIn=3600
    )

    print("✅ Presigned URL generated.")
    return JsonResponse({'url': url})


@csrf_exempt
@require_POST
def complete_multipart_upload(request):
    body = json.loads(request.body)
    upload_id = body.get('upload_id')
    key = body.get('key')
    parts = body.get('parts')

    print("🧩 Completing multipart upload...")
    print(f"🆔 Upload ID: {upload_id}")
    print(f"🔑 Key: {key}")
    print(f"📚 Parts received: {parts}")

    if not upload_id or not key or not parts:
        print("❌ Missing parameters.")
        return JsonResponse({'error': 'Missing parameters'}, status=400)

    response = s3_client.complete_multipart_upload(
        Bucket=settings.AWS_STORAGE_BUCKET_NAME,
        Key=key,
        UploadId=upload_id,
        MultipartUpload={
            'Parts': parts
        }
    )

    print("✅ Multipart upload completed.")
    print(f"📂 Final S3 URL: {response['Location']}")

    return JsonResponse({'file_url': response['Location']})



def upload_video(request):
    return render(request,"newvideo.html")
