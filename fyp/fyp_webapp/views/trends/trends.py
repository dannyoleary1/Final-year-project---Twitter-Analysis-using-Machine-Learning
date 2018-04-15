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

@login_required(login_url="/login/")
def trends(request):
    return render(request, "fyp/trends/index.html",
                  {'nbar': 'trends'})  # TODO change to a template