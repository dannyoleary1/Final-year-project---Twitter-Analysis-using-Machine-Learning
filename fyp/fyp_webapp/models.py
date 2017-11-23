from django.db import models
from sklearn.feature_extraction.text import TfidfVectorizer
from fyp_webapp.ElasticSearch import elastic_utils

# Create your models here.
class KMeansModel(models.Model):
    name = models.TextField()
    clusters = models.IntegerField()
    init = models.TextField(blank=True, default='kmeans++')
    number_iterations = models.IntegerField()
    verbose = models.IntegerField()

class TF_IDFModel(models.Model):
    batch_size = models.IntegerField()
    max_features = models.IntegerField()
    max_df = models.FloatField(default = 0.95)
    min_df = models.FloatField(default = 2)
    stopwords = models.TextField(default = 'english')
    elasticsearch_category = models.TextField(default = 'security')

