from django.db import models
from django.contrib.auth.models import User
from django.urls import reverse

class TwitterCat(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    category_name = models.CharField(max_length=30)

    def __unicode__(self):
        return self.name

    def get_absolute_url(self):
        return reverse('fyp_webapp:twittercat_edit', kwargs={'pk': self.pk})

class TwitterUser(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    twitter_username = models.CharField(max_length=30)

    def __unicode__(self):
        return self.name

    def get_absolute_url(self):
        return reverse('fyp_webapp:twitteruser_edit', kwargs={'pk': self.pk})

class NotificationTracked(models.Model):
    topic = models.CharField(max_length=30)
    keywords = models.TextField(null=True)

class NotificationLatest(models.Model):
    topic = models.CharField(max_length=30)
    keywords = models.TextField(null=True)

#myModel = MyModel()
#listIWantToStore = [1,2,3,4,5,'hello']
#myModel.myList = json.dumps(listIWantToStore)
#myModel.save()

#jsonDec = json.decoder.JSONDecoder()
#myPythonList = jsonDec.decode(myModel.myList)