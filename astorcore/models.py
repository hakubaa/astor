from django.conf import settings
from django.db import models
from django.utils import timezone
from django.contrib.contenttypes.models import ContentType
from django.contrib.contenttypes.fields import GenericForeignKey    
from django.urls import reverse
from django.urls.exceptions import NoReverseMatch

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

    def get_root_owner(self):
        '''Returns the owner of the tree.'''
        if self.is_root():
            if isinstance(self.specific, RootPage):        
                return self.specific.owner
            else:
                return None
        else:
            return self.get_parent().get_root_owner()

    def get_absolute_url(self):
        '''Returns url to specific page or to user profile if root page.'''
        owner = self.get_root_owner()
        if not owner:
            raise NoReverseMatch("Undefined owner of the page.")
        if self.is_root():
            return reverse("astormain:profile",
                           kwargs={"username": owner.slug})
        return reverse("astormain:entry", 
                       kwargs={"username": owner.slug, "page_id": self.id})    


class RootPage(Page):
    verbose_name = "root page"


class SimplePage(Page):
    verbose_name = "page"
    template_name = "astormain/pages/simple.html"

    title = models.CharField(
        max_length=255
    )
    created_date = models.DateTimeField(default=timezone.now)
    published_date = models.DateTimeField(blank=True, null=True)  

    def publish(self):
        '''Publish the page.'''
        self.published_date = timezone.now()
        self.save() 


@register_page
class IndexPage(SimplePage):
    verbose_name = "index page"
    template_name = "astormain/pages/index.html"

    abstract = models.TextField(default="")    


@register_page
class ContentPage(SimplePage):
    verbose_name = "content page"
    template_name = "astormain/pages/content.html"

    abstract = models.TextField(default="") 
    body = models.TextField()