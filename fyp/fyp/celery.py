from __future__ import absolute_import
import os
from celery import Celery
from django.conf import settings
from fyp import settings
from django.apps import apps
import django
from celery.schedules import crontab


# set the default Django settings module for the 'celery' program.
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'fyp.settings')
django.setup()
app = Celery('fyp_webapp')

# Using a string here means the worker will not have to
# pickle the object when using Windows.
app.config_from_object('django.conf:settings')


# Load task modules from all registered Django app configs.
app.autodiscover_tasks(force=True)

app.conf.beat_schedule = {
    'check_index': {
        'task': 'fyp_webapp.tasks.check_index',
        'schedule': 300.0,
        'options': {'queue' : 'misc'}
    },
    'clean-indexes': {
        'task': 'fyp_webapp.tasks.clean_indexes',
        'schedule': crontab(minute=21, hour=0),
        'options': {'queue': 'misc'}
    }
}
app.conf.timezone = 'UTC'


@app.task(bind=True)
def debug_task(self):
    print('Request: {0!r}'.format(self.request))