from django.conf import settings
from django.db import models
from django.utils import timezone
from django.contrib.auth.models import User

from treebeard.mp_tree import MP_Node


class Page(MP_Node):
    title = models.CharField(
        max_length=255,
        null=False, blank=False
    )
    body = models.TextField()
    created_date = models.DateTimeField(default=timezone.now)
    published_date = models.DateTimeField(blank=True, null=True)

    owner = models.ForeignKey(settings.AUTH_USER_MODEL, null=True, blank=True,
                              on_delete=models.SET_NULL,
                              related_name="owned_pages")

    def set_owner(self, user):
        '''
        Set owner of the page. 
        '''
        self.owner = user
        self.save()

    def publish(self):
        '''
        Publish the page. 
        '''
        self.published_date = timezone.now()
        self.save()

    def get_absolute_url(self):
        pass