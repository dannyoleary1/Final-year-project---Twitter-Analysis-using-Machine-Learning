from django.shortcuts import get_object_or_404, render, render_to_response, HttpResponseRedirect
from fyp_webapp.ElasticSearch import elastic_utils
from django.contrib.auth.decorators import login_required
from fyp_webapp import config as cfg
from fyp_webapp.models import TwitterCat

@login_required(login_url="/login/")
def timeline(request):
    if request.POST:
        print (request.POST)
        answer = request.POST['dropdown']
        cat = TwitterCat.objects.filter(category_name=answer)
        name =""
        for mod in cat:
            res = elastic_utils.iterate_search(index_name=mod.category_name, query={
                        "query":
                            {
                                "match_all": {}
                            },
                        "sort": [
                            {
                                "last_time": {
                                    "order": "desc"
                                }
                            }
                        ],
                        "size":20,
                    })
            med = elastic_utils.search_index(index_name=mod.category_name+"-median")
            name = mod.category_name
            break
    else:
        cat = TwitterCat.objects.filter(user=request.user)
        name = ""
        for mod in cat:
            res = elastic_utils.iterate_search(index_name=mod.category_name, query={
                        "query":
                            {
                                "match_all": {}
                            },
                        "sort": [
                            {
                                "last_time": {
                                    "order": "desc"
                                }
                            }
                        ],
                        "size":20,
                    })
            med = elastic_utils.search_index(index_name=mod.category_name+"-median")
            name = mod.category_name
            break

    cat = TwitterCat.objects.filter(user=request.user)
    data = {}
    for entry in res:
        temp_data = {}
        for hour in entry["_source"]["hour_breakdown"]:
            temp_data[int(hour)] = (entry["_source"]["hour_breakdown"][hour])
        data[entry["_source"]["date"]] = temp_data

    day_median = med["hits"]["hits"][0]["_source"]["day_median"]
    hour_median = med["hits"]["hits"][0]["_source"]["hour_median"]
    minute_median = med["hits"]["hits"][0]["_source"]["minute_median"]
    hour_med_tresh = hour_median*2
    minute_med_tresh = minute_median*2
    day_med_tresh = day_median*1.5

    print (hour_med_tresh)
    #for entry in res:
    #    temp_data = {}
    #    for hour in entry["_source"]["hour_breakdown"]:
    #        temp_data[int(hour)] = (entry["_source"]["hour_breakdown"][hour])
    #    data[entry["_source"]["date"]] = temp_data
    return render(request, "fyp/timeline/index.html", {"data": data, "name":name, "cats":cat, "hour_med_tresh":hour_med_tresh, "minute_med_tresh":minute_med_tresh, "day_med_tresh":day_med_tresh})

