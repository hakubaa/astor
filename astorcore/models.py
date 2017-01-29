from django.conf import settings
from django.db import models
from django.utils import timezone
from django.contrib.contenttypes.models import ContentType
from django.contrib.contenttypes.fields import GenericForeignKey    

from treebeard.mp_tree import MP_Node

from astorcore.decorators import register_page



class Page(MP_Node):
    verbose_name = "base page"

    # Required for creating hierarchy composed of different Pages
    content_type = models.ForeignKey(
        ContentType, related_name="pages", null=True,
        on_delete=models.SET_NULL
    )

    def __init__(self, *args, **kwargs):
        super(Page, self).__init__(*args, **kwargs)
        # Set content type only once
        if not self.id and not self.content_type_id:
            self.content_type = ContentType.objects.get_for_model(self)

    @property
    def specific(self):
        '''Casts Page to specific type stored in content_type.''' 
        content_type = ContentType.objects.get_for_id(self.content_type_id)
        model_class = content_type.model_class()
        if model_class is None or isinstance(self, model_class):
            return self
        return content_type.get_object_for_this_type(id=self.id)
        

@register_page
class IndexPage(Page):
    verbose_name = "index page"

    title = models.CharField(
        max_length=255
    )
    abstract = models.TextField(default="")    
    created_date = models.DateTimeField(default=timezone.now)
    published_date = models.DateTimeField(blank=True, null=True)

    def publish(self):
        '''Publish the page.'''
        self.published_date = timezone.now()
        self.save() 


@register_page
class ContentPage(IndexPage):
    verbose_name = "content page"

    body = models.TextField()