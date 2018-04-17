from django.shortcuts import get_object_or_404, render, render_to_response, HttpResponseRedirect
from fyp_webapp.ElasticSearch import elastic_utils
from django.contrib.auth.decorators import login_required
from fyp_webapp import config as cfg
from fyp_webapp.models import TwitterCat
from fyp_webapp.tasks import setup_charts
from django.shortcuts import get_object_or_404, render, render_to_response
from django.contrib.auth.decorators import login_required
from fyp_webapp.tasks import elastic_info
from celery.result import AsyncResult
from django.http import HttpResponse
from django.shortcuts import get_object_or_404, render, render_to_response, HttpResponseRedirect
from django.urls import reverse
import json
from fyp_webapp.ElasticSearch import elastic_utils
import json
import ast
from fyp_webapp.TwitterProcessing import termsfrequency
from collections import Counter

@login_required(login_url="/login/")
def charts(request):
    cat = TwitterCat.objects.filter(user=request.user)
    if 'job' in request.GET:
        print ("in job")
        job_id = request.GET['job']
        job = AsyncResult(job_id)
        data = job.result or job.state
        context = {
            'data': data,
            'task_id': job_id,
            'total': range(len(cat))
        }
        return render(request, "fyp/charts/index.html", context)
    else:
        topic_list = []
        for mod in cat:
            topic_list.append(mod.category_name)
        job = setup_charts.delay(topic_list)
        print (job)
        data = {}
        return HttpResponseRedirect(reverse('fyp_webapp:charts') + '?job=' + job.id)

def poll_state(request):
    """ A view to report the progress to the user """
    data = 'Fail'
    if request.is_ajax():
        if 'task_id' in request.POST.keys() and request.POST['task_id']:
            task_id = request.POST['task_id']
            task = AsyncResult(task_id)
            data = task.result or task.state
        else:
            data = 'No task_id in the request'
    else:
        data = 'This is not an ajax request'
    json_data = json.dumps(data)
    return HttpResponse(json_data, content_type='application/json')