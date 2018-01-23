from django.http import HttpResponse
from django.shortcuts import get_object_or_404, render, render_to_response, redirect
from fyp_webapp.ElasticSearch import elastic_utils
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from fyp_webapp.models import TwitterCat
from django.http import HttpResponse
from django.views.generic import TemplateView,ListView
from django.views.generic.edit import CreateView, UpdateView, DeleteView
from django.core.urlresolvers import reverse_lazy
from django.forms import ModelForm

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


def twittercat_list(request, template_name='fyp/Category/twittercat_list.html'):
    cat = TwitterCat.objects.all()
    data = {}
    data['object_list'] = cat
    return render(request, template_name, data)

def twittercat_create(request, template_name='fyp/Category/twittercat_form.html'):
    form = TwitterCatForm(request.POST or None)
    test = form.save(commit=False)
    test.user = request.user
    if form.is_valid():
        form.save()
        return redirect('fyp_webapp:twittercat_list')
    return render(request, template_name, {'form':form})

def twittercat_update(request, pk, template_name='fyp/Category/twittercat_form.html'):
    book= get_object_or_404(TwitterCat, pk=pk)
    form = TwitterCatForm(request.POST or None, instance=book)
    if form.is_valid():
        form.save()
        return redirect('fyp_webapp:twittercat_list')
    return render(request, template_name, {'form':form})

def twittercat_delete(request, pk, template_name='fyp/Category/twittercat_confirm_delete.html'):
    book= get_object_or_404(TwitterCat, pk=pk)
    if request.method=='POST':
        book.delete()
        return redirect('fyp_webapp:twittercat_list')
    return render(request, template_name, {'object':book})

class TwitterCatList(ListView):
    model = TwitterCat
    print (model)

class TwitterCatCreate(CreateView):
    model = TwitterCat
    fields = ['category_name']
    success_url = reverse_lazy('fyp_webapp:twittercat_list')

class TwitterCatUpdate(UpdateView):
    model = TwitterCat
    fields = ['category_name']
    success_url = reverse_lazy('fyp_webapp:twittercat_list')

class TwitterCatDelete(DeleteView):
    model = TwitterCat
    success_url = reverse_lazy('fyp_webapp:twittercat_list')