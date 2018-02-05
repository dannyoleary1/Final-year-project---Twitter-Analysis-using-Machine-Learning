from django.conf.urls import url, include

from . import views
from .views.collect import collect
from .views.trainmodel import trainmodel
from .views.index import index
from .views.category import category
from .views.twitteruser import twitteruser
from .views.taskprogress import taskprogress


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

    url(r'^twitteruser', twitteruser.twitteruser_list, name='twitteruser_list'),
    url(r'^create-twitteruser', twitteruser.twitteruser_create, name='twitteruser_new'),
    url(r'^edit-twitteruser/(?P<pk>\d+)$', twitteruser.twitteruser_update, name='twitteruser_edit'),
    url(r'^delete-twitteruser/delete/(?P<pk>\d+)$', twitteruser.twitteruser_delete, name='twitteruser_delete'),
    url(r'^suggestcategory-twitteruser', twitteruser.twitteruser_suggest, name='twitteruser_suggest'),

    url(r'^taskprogress$', taskprogress.taskprogress, name='taskprogress'),
    url(r'^poll_state$', taskprogress.poll_state,name='poll_state'),


]
