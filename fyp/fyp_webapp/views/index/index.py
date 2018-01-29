from django.http import HttpResponse
from django.shortcuts import get_object_or_404, render, render_to_response
from fyp_webapp.ElasticSearch import elastic_utils
from django.contrib.auth.decorators import login_required
import json
from fyp_webapp.models import TwitterCat
from fyp_webapp import config as cfg
from fyp_webapp.TwitterProcessing import preprocessor



@login_required(login_url='/login/')
def fyp(request):
    test = {'I':2,'a':4}
    test = json.dumps(test)
    print (test)
    cat = TwitterCat.objects.filter(user=request.user)
    item = {}
    category = []
    for entry in cat:

        entry = preprocessor.preprocess(entry.category_name)
        entry = preprocessor.porter_stemming(entry)
        entry = ''.join(c for c in entry if c not in '[]\'')
        res = (elastic_utils.search_index(cfg.twitter_credentials['topic'], query='{"query":{"query_string":{"fields":["text"],"query":"%s*"}}}' % str(entry)))
        total = res['hits']['total']
        item[entry] = total
        category.append(entry)


    jsonData = json.dumps(item)
    print (jsonData)

    return render(request, "fyp/index.html", {'jsonData':jsonData, 'category':category}, {'nbar':'index'}) #TODO change to a template