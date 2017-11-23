from django.conf.urls import url

from . import views

urlpatterns = [
    url(r'^$', views.fyp, name='fyp'),
    url(r'^collect', views.tweetcollector, name='tweetcollector'),
]
