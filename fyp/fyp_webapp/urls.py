from django.conf.urls import url

from . import views
from .views.collect import collect
from .views.trainmodel import trainmodel
from .views.index import index

urlpatterns = [
    url(r'^$', index.fyp, name='fyp'),
    url(r'^collect', collect.tweetcollector, name='tweetcollector'),
    url(r'^latesttweets', collect.latesttweets, name="latesttweets"),
    url(r'^trainmodel', trainmodel.trainmodel, name="trainmodel"),
    url(r'^trainedmodel', trainmodel.trainedmodel, name="trainedmodel")
]
