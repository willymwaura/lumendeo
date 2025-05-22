
from django.db import models
from django.utils.timezone import now

from django.db import models
from datetime import timedelta
from django.utils import timezone

def default_expire_date():
    return timezone.now() + timedelta(days=30)

class MonthlyVideo(models.Model):
    title = models.CharField(max_length=255)
    video_url = models.URLField()
    trailer_url = models.URLField()
    thumbnail = models.ImageField(upload_to='thumbnails/')
    year_published = models.PositiveIntegerField()
    introduction = models.TextField()
    date_uploaded = models.DateTimeField(auto_now_add=True)
    expire_date = models.DateTimeField(default=default_expire_date)
    cast = models.CharField(max_length=150)
    theme = models.CharField(max_length=150)
    length = models.CharField(max_length=150, default='2.0')
    movie_type = models.CharField(max_length=150, default='drama')

    def is_expired(self):
        return timezone.now() > self.expire_date

    def __str__(self):
        return self.title

# models.py


from myapp.models import MonthlyVideo  # adjust this import based on your app name

class Payment(models.Model):
    phone = models.CharField(max_length=15)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    movie = models.ForeignKey(MonthlyVideo, on_delete=models.CASCADE)
    status = models.BooleanField(default=False)
    timestamp = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return f"{self.phone} - {self.movie.title} - {'Paid' if self.status else 'Pending'}"




