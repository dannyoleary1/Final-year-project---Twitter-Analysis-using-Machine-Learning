from django.db import models
from django.contrib.auth.models import User

class TwitterCat(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    category_name = models.CharField(max_length=30)

