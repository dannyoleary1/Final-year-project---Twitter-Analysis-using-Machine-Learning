from django.db import models
from django.contrib.auth.models import User
from django.core.urlresolvers import reverse

class TwitterCat(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    category_name = models.CharField(max_length=30)

    def __unicode__(self):
        return self.name

    def get_absolute_url(self):
        return reverse('fyp_webapp:twittercat_edit', kwargs={'pk': self.pk})

