from django.http import HttpResponse
from django.shortcuts import get_object_or_404, render, render_to_response, redirect
from fyp_webapp.ElasticSearch import elastic_utils
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from fyp_webapp.models import TwitterUser
from django.http import HttpResponse
from django.views.generic import TemplateView,ListView
from django.views.generic.edit import CreateView, UpdateView, DeleteView
from django.core.urlresolvers import reverse_lazy
from django.forms import ModelForm

class TwitterUserForm(ModelForm):
    class Meta:
        model = TwitterUser
        fields = ['user', 'twitter_username']
        exclude = ['user']

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
            print(request.POST.getlist('suggest-user'))

    cat = TwitterUser.objects.filter(user=request.user)
    data = {}
    data['object_list'] = cat
    return render(request, template_name, data)