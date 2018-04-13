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
def fyp(request):
    if 'job' in request.GET:
        job_id = request.GET['job']
        job = AsyncResult(job_id)
        data = job.result or job.state
        context = {
            'data': data,
            'task_id': job_id,
        }
        return render(request, "fyp/index.html", context)
    else:
        topic = cfg.twitter_credentials['topic']
        job = word_cloud.delay(request.user.id, topic)
        return HttpResponseRedirect(reverse('fyp_webapp:fyp') + '?job=' + job.id, {'nbar': 'index'})
        #  return render(request, "fyp/index.html", {'jsonData': job, 'category': job}, {'nbar': 'index'})

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
    print(data)
    json_data = json.dumps(data)
    return HttpResponse(json_data, content_type='application/json')


# @login_required(login_url='/login/')
# def fyp(request):
#    if request.POST:
#        return render_word_cloud(list(request.POST.dict().keys())[0])
#    cat = TwitterCat.objects.filter(user=request.user)
#    item = {}
#    category = []
#    for entry in cat:
#        entry = preprocessor.preprocess(entry.category_name)
#        entry = preprocessor.porter_stemming(entry)
#        entry = ''.join(c for c in entry if c not in '[]\'')
#        res = (elastic_utils.search_index(cfg.twitter_credentials['topic'], query='{"query":{"query_string":{"fields":["text"],"query":"%s*"}}}' % str(entry)))
#        total = res['hits']['total']
#        item[entry] = total
#        category.append(entry)


#    jsonData = json.dumps(item)
#    print (jsonData)

#   return render(request, "fyp/index.html", {'jsonData':jsonData, 'category':category}, {'nbar':'index'}) #TODO change to a template

def render_word_cloud(word):
    texts = []
    res = elastic_utils.iterate_search(index_name=cfg.twitter_credentials['topic'],
                                       query={"query": {"query_string": {"fields": ["text"], "query": "%s*" % word}}})
    for i in res:
        entry = i['_source']['text']
        entry = preprocessor.filter_multiple(entry, ats=True, hashtags=True, stopwords=True, urls=True, stemming=True)

        texts.append(str(entry))
    jsonData = count_words(35, texts)
    words = []
    items = {}
    for entry in jsonData:
        words.append(entry[0])
        items[entry[0]] = entry[1]
    jsonData = json.dumps(items)
    print(jsonData)
    return JsonResponse({'jsonData': jsonData, 'category': words})


def count_words(number_word_frequency_results, list_in_question):
    nltk.download('stopwords')
    #TODO change to our stopwords.
    punctuation = list(string.punctuation)
    stop = stopwords.words('english') + punctuation + ['rt', 'via', '…', 'I', '’', 'The', '!']
    count_word_frequency = Counter()
    for entry in list_in_question:
        terms_all = [term for term in preprocessor.preprocess(entry) if term not in stop]
        count_word_frequency.update(terms_all)
    return count_word_frequency.most_common(number_word_frequency_results)
