from django.http import HttpResponse
from django.shortcuts import get_object_or_404, render




def fyp(request):
    return HttpResponse("Hello, world. You're at the index.")

def tweetcollector(request):
    if (request.GET.get('collect_tweets')):
        print ("it be here")
    return render(request, 'fyp/CollectTweets/index.html')