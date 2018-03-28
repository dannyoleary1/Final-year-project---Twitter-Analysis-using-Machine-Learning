from django.shortcuts import get_object_or_404, render, render_to_response, HttpResponseRedirect
from fyp_webapp.ElasticSearch import elastic_utils
from django.contrib.auth.decorators import login_required
from fyp_webapp import config as cfg

@login_required(login_url="/login/")
def timeline(request):
    res = elastic_utils.iterate_search("psn")
    data = {}
    for entry in res:
        temp_data = {}
        for hour in entry["_source"]["hour_breakdown"]:
            temp_data[int(hour)] = (entry["_source"]["hour_breakdown"][hour])
        data[entry["_source"]["date"]] = temp_data
    return render(request, "fyp/timeline/index.html", {"data": data})

