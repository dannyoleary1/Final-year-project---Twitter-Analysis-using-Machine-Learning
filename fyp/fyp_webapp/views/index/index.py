from django.http import HttpResponse
from django.shortcuts import get_object_or_404, render, render_to_response, HttpResponseRedirect
from fyp_webapp.ElasticSearch import elastic_utils
from django.contrib.auth.decorators import login_required
import json
from fyp_webapp.models import TwitterCat
from fyp_webapp import config as cfg
from fyp_webapp.TwitterProcessing import preprocessor
import string
import nltk
from nltk.corpus import stopwords
from collections import Counter
from fyp_webapp.TwitterProcessing import preprocessor
from django.http import JsonResponse
from celery.result import AsyncResult
from fyp_webapp.tasks import word_cloud
from django.urls import reverse
from fyp_webapp import models

@login_required(login_url="/login/")
def fyp(request):
        topics = models.TwitterCat.objects.all()
        tracked = models.NotificationTracked.objects.all()
        if models.NotificationTracked.objects.count() > 0:
            latest_detection_date = (models.NotificationTracked.objects.all()[models.NotificationTracked.objects.count()-1]).date
        else:
            latest_detection_date = "N/A"
        latest_tracked = models.NotificationTracked.objects.all().order_by('-pk')[:5]
        tweet_total = 0
        for cat in topics:
            tweet_total += elastic_utils.count_entries(cat.category_name+"-latest")["count"]
        return render(request, "fyp/index/index.html", {"topics": len(topics), "tracked": len(tracked), "tweet_total": tweet_total, "latest_detection_date": latest_detection_date,
                                                        "latest_tracked": latest_tracked})


