from django.http import HttpResponse
from django.shortcuts import get_object_or_404, render, render_to_response

def fyp(request):

    return render(request, "fyp/index.html", {'nbar':'index'}) #TODO change to a template