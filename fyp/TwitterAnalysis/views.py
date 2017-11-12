from django.http import HttpResponse


def index(request):
    return HttpResponse("This is where the index page will go.")