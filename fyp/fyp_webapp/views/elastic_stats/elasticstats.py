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
        print (context)
        return render(request, "fyp/elasticstats/index.html", context)
    else:
        job = elastic_info.delay()
        return HttpResponseRedirect(reverse('fyp_webapp:elasticstats') + '?job=' + job.id)

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
    print(data)
    json_data = json.dumps(data)
    return HttpResponse(json_data, content_type='application/json')