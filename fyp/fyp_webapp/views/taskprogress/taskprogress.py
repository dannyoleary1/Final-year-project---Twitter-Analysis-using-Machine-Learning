from celery.result import AsyncResult
from django.http import HttpResponse, HttpResponseRedirect
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
    json_data = json.dumps(data)
    return HttpResponse(json_data, content_type='application/json')


#@login_required(login_url='/login/')
#def taskprogress(request):
#    job = fft_random.delay(int(200))
#    print (job)
#    return render(request, 'fyp/taskprogress/index.html')
