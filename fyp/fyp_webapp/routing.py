from fyp_webapp import consumers
from django.conf.urls import url


websocket_urlpatterns = [
    url(r'^fyp', consumers.NotificationConsumer),
]