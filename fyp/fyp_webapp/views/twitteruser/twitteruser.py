from django.http import HttpResponse
from django.shortcuts import get_object_or_404, render, render_to_response, redirect
from fyp_webapp.ElasticSearch import elastic_utils
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from fyp_webapp.models import TwitterUser
from django.http import HttpResponse
from django.views.generic import TemplateView,ListView
from django.views.generic.edit import CreateView, UpdateView, DeleteView
from django.urls import reverse_lazy
from django.forms import ModelForm
from fyp_webapp.TwitterProcessing import collect_user_tweets
from fyp_webapp.TwitterProcessing import preprocessor
from fyp_webapp.TwitterProcessing import termsfrequency
from collections import Counter
from fyp_webapp.models import TwitterCat
from fyp_webapp.tasks import collect_old_tweets
from fyp_webapp.ElasticSearch import elastic_utils
import tweepy
from fyp_webapp import config as cfg

class TwitterUserForm(ModelForm):
    class Meta:
        model = TwitterUser
        fields = ['user', 'twitter_username', 'image', 'username', 'description']
        exclude = ['user', 'image', 'username', 'description']

@login_required(login_url='/login/')
def twitteruser_list(request, template_name='fyp/twitteruser/twitteruser_list.html'):
    cat = TwitterUser.objects.filter(user=request.user)
    data = {}
    data['object_list'] = cat
    return render(request, template_name, data)

@login_required(login_url='/login/')
def twitteruser_create(request, template_name='fyp/twitteruser/twitteruser_form.html'):
    form = TwitterUserForm(request.POST or None)
    test = form.save(commit=False)
    test.user = request.user
    if form.is_valid():
        username = form.cleaned_data['twitter_username']
        auth = tweepy.OAuthHandler(cfg.twitter_credentials["consumer_key"], cfg.twitter_credentials['consumer_secret'])
        auth.set_access_token(cfg.twitter_credentials['access_token'], cfg.twitter_credentials['access_token_secret'])
        api = tweepy.API(auth)
        user = api.get_user(username)
        test.image = user.profile_image_url
        test.username = user.screen_name
        test.description = user.description
        form.save()
        return redirect('fyp_webapp:twitteruser_list')
    return render(request, template_name, {'form':form})

@login_required(login_url='/login/')
def twitteruser_update(request, pk, template_name='fyp/twitteruser/twitteruser_form.html'):
    book= get_object_or_404(TwitterUser, pk=pk)
    form = TwitterUserForm(request.POST or None, instance=book)
    if form.is_valid():
        form.save()
        return redirect('fyp_webapp:twitteruser_list')
    return render(request, template_name, {'form':form})

@login_required(login_url='/login/')
def twitteruser_delete(request, pk, template_name='fyp/twitteruser/twitteruser_confirm_delete.html'):
    book= get_object_or_404(TwitterUser, pk=pk)
    if request.method=='POST':
        book.delete()
        return redirect('fyp_webapp:twitteruser_list')
    return render(request, template_name, {'object':book})

@login_required(login_url='/login/')
def twitteruser_suggest(request, template_name='fyp/twitteruser/twitteruser_suggest.html'):
    if request.method == 'POST':
        if 'twitteruser-form' in request.POST:
            all_tweets = []
            all_text = []
            user_list = request.POST.getlist('suggest-user')
            for user in user_list:
                all_tweets.extend(collect_user_tweets.get_all_users_tweets(user))
            count_word_frequency = Counter()
            for tweet in all_tweets:
                text = preprocessor.preprocess(str(tweet.text))
                text = preprocessor.remove_stop_words(text)
                text = preprocessor.remove_ats(text)
                text = preprocessor.remove_hashtags(text)
                text = preprocessor.remove_urls(text)
                text = [i for i in text if len(i) > 2]
                all_text.extend(text)
                terms_all = [term for term in text]
                count_word_frequency.update(terms_all)
            suggestions = count_word_frequency.most_common(25)
            print (suggestions)
            cat = TwitterUser.objects.filter(user=request.user)
            data = {}
            data['object_list'] = cat
            return render(request, template_name, {'suggestions':suggestions, 'object_list':data['object_list']})
        if 'suggestcat-form' in request.POST:
            print (request.POST)
            category_list = request.POST.getlist('suggest-category')
            for category in category_list:
                category = ''.join(c for c in category if c not in '()\',')
                entry = TwitterCat(user=request.user, category_name=category)
                entry.save()
                elastic_utils.create_index(category)
                collect_old_tweets.delay(category, 30)

    cat = TwitterUser.objects.filter(user=request.user)
    data = {}
    data['object_list'] = cat
    return render(request, template_name, data)