from django.http import HttpResponse
from django.shortcuts import get_object_or_404, render, render_to_response, redirect
from fyp_webapp.ElasticSearch import elastic_utils
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from fyp_webapp.models import TwitterCat
from django.http import HttpResponse
from django.views.generic import TemplateView,ListView
from django.views.generic.edit import CreateView, UpdateView, DeleteView
from django.urls import reverse_lazy
from django.forms import ModelForm
from fyp_webapp.ElasticSearch import elastic_utils
from fyp_webapp.tasks import collect_old_tweets
from fyp_webapp.models import NotificationTracked

@login_required(login_url='/login/')
def category(request):
    if request.user.is_authenticated():
        current_user = request.user
        entries = TwitterCat.objects.filter(user=current_user)
    return render(request, "fyp/Category/index.html", {'entries':entries}, {'nbar':'category'}) #TODO change to a template


class TwitterCatForm(ModelForm):
    class Meta:
        model = TwitterCat
        fields = ['user', 'category_name']
        exclude = ['user']

@login_required(login_url='/login/')
def twittercat_list(request, template_name='fyp/Category/twittercat_list.html'):
    cat = TwitterCat.objects.filter(user=request.user)
    data = {}
    for entry in cat:
        tracked = NotificationTracked.objects.filter(topic=entry.category_name)
        if "whois" in entry.category_name:
            tracked.delete()
        if "story" in entry.category_name:
            tracked.delete()
        elastic_utils.create_index(entry.category_name)
        elastic_utils.create_index(entry.category_name+"-latest")
        count = elastic_utils.count_entries(entry.category_name+"-latest")["count"]
        entry.count = count
        entry.tracked = len(tracked)
    data['object_list'] = cat
    return render(request, template_name, data)

@login_required(login_url='/login/')
def twittercat_create(request, template_name='fyp/Category/twittercat_form.html'):
    if 'job' in request.POST:
        form = TwitterCatForm(request.POST or None)
        test = form.save(commit=False)
        test.user = request.user
        if form.is_valid():
            form.save()
            return redirect('fyp_webapp:twittercat_list')
    form = TwitterCatForm(request.POST or None)
    test = form.save(commit=False)
    test.user = request.user
    if form.is_valid():
        print ("in here?")
        form.save()
        topic = form.cleaned_data['category_name'] + "-latest"
        elastic_utils.create_index(topic)
        elastic_utils.create_index(form.cleaned_data['category_name'])
       # collect_old_tweets.delay(form.cleaned_data['category_name'], 30)
        return redirect('fyp_webapp:twittercat_list')
    return render(request, template_name, {'form':form})

@login_required(login_url='/login/')
def twittercat_update(request, pk, template_name='fyp/Category/twittercat_form.html'):
    book= get_object_or_404(TwitterCat, pk=pk)
    form = TwitterCatForm(request.POST or None, instance=book)
    if form.is_valid():
        form.save()
        return redirect('fyp_webapp:twittercat_list')
    return render(request, template_name, {'form':form})

@login_required(login_url='/login/')
def twittercat_delete(request, pk, template_name='fyp/Category/twittercat_confirm_delete.html'):
    book= get_object_or_404(TwitterCat, pk=pk)
    if request.method=='POST':
        topic = book.category_name + "-latest"
        book.delete()
        elastic_utils.delete_index(topic)
        return redirect('fyp_webapp:twittercat_list')
    return render(request, template_name, {'object':book})
