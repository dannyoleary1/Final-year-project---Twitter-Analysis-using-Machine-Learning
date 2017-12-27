from django.conf.urls import url

from . import views

urlpatterns = [
    url(r'^$', views.fyp, name='fyp'),
    url(r'^collect', views.tweetcollector, name='tweetcollector'),
    url(r'^latesttweets', views.latesttweets, name="latesttweets"),
    url(r'^trainmodel', views.trainmodel, name="trainmodel"),
    url(r'^trainedmodel', views.trainedmodel, name="trainedmodel"),
    url(r'^testlda', views.testlda, name="testlda")
]
