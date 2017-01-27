from django.conf import settings
from django.db import models
from django.utils import timezone

from treebeard.mp_tree import MP_Node


class AbstractPage(MP_Node):
    class Meta:
        abstract = True


class RootPage(AbstractPage):
    '''Root page. Provides grounds for creating hierarchy of pages.'''
    owner = models.OneToOneField(settings.AUTH_USER_MODEL, null=True, blank=True,
                                 on_delete=models.SET_NULL,
                                 related_name="root_page")


class Page(AbstractPage):
    title = models.CharField(
        max_length=255,
        null=False, blank=False
    )
    abstract = models.TextField(default="")    
    created_date = models.DateTimeField(default=timezone.now)
    published_date = models.DateTimeField(blank=True, null=True)

    def publish(self):
        '''Publish the page.'''
        self.published_date = timezone.now()
        self.save() 


class ContentPage(Page):
    body = models.TextField()