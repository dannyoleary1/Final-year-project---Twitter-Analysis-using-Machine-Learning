from django.shortcuts import get_object_or_404, render, render_to_response
from django.contrib.auth.decorators import login_required
from fyp_webapp.tasks import elastic_info
from celery.result import AsyncResult
from django.http import HttpResponse
from django.shortcuts import get_object_or_404, render, render_to_response, HttpResponseRedirect
from django.core.urlresolvers import reverse
import json

@login_required(login_url='/login/')
def elasticstats(request):
    print ("accessed.")
    if 'job' in request.GET:

        job_id = request.GET['job']
        job = AsyncResult(job_id)
        data = job.result or job.state
        print (job.state)
        context = {
            'data': data,
            'task_id': job_id,
        }
        return render(request, "fyp/elasticstats/index.html", context)
    else:
        job = elastic_info.delay()
        return HttpResponseRedirect(reverse('fyp_webapp:elasticstats') + '?job=' + job.id)