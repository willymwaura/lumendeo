
from django.contrib import admin
from .models import MonthlyVideo,Payment


# Register your models here.

from django.contrib import admin
from django import forms
from .models import MonthlyVideo


from .widgets import S3UploadWidget

class MonthlyVideoForm(forms.ModelForm):
    class Meta:
        model = MonthlyVideo
        fields = '__all__'
        widgets = {
            'video': S3UploadWidget(),
            'trailer': S3UploadWidget(),
        }

@admin.register(MonthlyVideo)
class MonthlyVideoAdmin(admin.ModelAdmin):
    form = MonthlyVideoForm
admin.site.register(Payment)
