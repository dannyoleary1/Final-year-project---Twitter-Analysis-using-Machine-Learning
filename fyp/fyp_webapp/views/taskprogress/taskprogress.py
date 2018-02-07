from django.shortcuts import get_object_or_404, render, render_to_response, HttpResponse
from django.contrib.auth.decorators import login_required
from fyp_webapp.tasks import fft_random
from celery.result import AsyncResult
import json
from django.shortcuts import render
from django.http import HttpResponse, HttpResponseRedirect
from django.core.urlresolvers import reverse
from django.template import loader
from fyp_webapp.forms import LDAForm
from fyp_webapp.tasks import add,fft_random
import json

# Create your views here.
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
    print (data)
    json_data = json.dumps(data)
    return HttpResponse(json_data, content_type='application/json')

@login_required(login_url='/login/')
def taskprogress(request):
    if 'job' in request.GET:
        job_id = request.GET['job']
        job = AsyncResult(job_id)
        data = job.result or job.state
        print("----------")
        print(data)
        print("----------")
        context = {
            'data':data,
            'task_id':job_id,
        }
        return render(request,"fyp/taskprogress/show_t.html",context)
    elif 'samples' in request.GET:
        n = request.GET['samples']
        job = fft_random.delay(int(n))
        return HttpResponseRedirect(reverse('fyp_webapp:taskprogress') + '?job=' + job.id)
    else:
        form = LDAForm()
        context = {
            'form':form,
        }
        return render(request,"fyp/taskprogress/post_form.html",context)

#@login_required(login_url='/login/')
#def taskprogress(request):
#    job = fft_random.delay(int(200))
#    print (job)
#    return render(request, 'fyp/taskprogress/index.html')
