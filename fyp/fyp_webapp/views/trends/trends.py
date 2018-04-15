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
from fyp_webapp.models import NotificationTracked
from django.shortcuts import get_object_or_404, render, render_to_response, redirect

@login_required(login_url="/login/")
def trends(request):
    print ("in here")
    mod = NotificationTracked.objects.all()
    for entry in mod:
        print ("_________")
        print (entry.topic)
        print (entry.keywords)
    return render(request, "fyp/trends/trends_list.html", {"entries":mod},
                  {'nbar': 'trends'})  # TODO change to a template

@login_required(login_url='/login/')
def trends_delete(request, pk, template_name='fyp/trends/trends_confirm_delete.html'):
    print ("IN TREND DELETE")
    book= get_object_or_404(NotificationTracked, pk=pk)
    print (book)
    if request.method=='POST':
        book.delete()
        return redirect('fyp_webapp:trends')
    return render(request, template_name, {'object':book})