from django.conf.urls import url, include

from . import views
from .views.collect import collect
from .views.trainmodel import trainmodel
from .views.index import index
from .views.category import category



urlpatterns = [
    url(r'^$', index.fyp, name='fyp'),
    url(r'^collect', collect.tweetcollector, name='tweetcollector'),
    url(r'^latesttweets', collect.latesttweets, name="latesttweets"),
    url(r'^trainmodel', trainmodel.trainmodel, name="trainmodel"),
 #   url(r'^category', category.category, name="category"),
    url(r'^category', category.twittercat_list,name='twittercat_list'),
    url(r'^create-category', category.twittercat_create, name='twittercat_new'),
    url(r'^edit-category/(?P<pk>\d+)$', category.twittercat_update, name='twittercat_edit'),
    url(r'^delete-category/delete/(?P<pk>\d+)$', category.twittercat_delete, name='twittercat_delete'),

]
