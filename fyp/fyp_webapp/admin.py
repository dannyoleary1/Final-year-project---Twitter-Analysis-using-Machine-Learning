from django.contrib import admin

# Register your models here.
from .models import KMeansModel, TF_IDFModel

admin.site.register(KMeansModel)
admin.site.register(TF_IDFModel)
