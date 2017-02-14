from django.conf import settings
from django.db import models
from django.conf import settings
from django.utils import timezone
from django.contrib.contenttypes.models import ContentType
from django.contrib.contenttypes.fields import GenericForeignKey    
from django.urls import reverse
from django.urls.exceptions import NoReverseMatch

from taggit.managers import TaggableManager

from astorcore.decorators import register_page
from astorcore.utils import clone_page


class Page(models.Model):
    verbose_name = "page"

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, 
        on_delete=models.SET_NULL, blank=True, null=True,
        related_name="pages"
    )

    # Required for storing different Pages.
    content_type = models.ForeignKey(
        ContentType, related_name="pages", null=True,
        on_delete=models.SET_NULL
    )

    def __init__(self, *args, **kwargs):
        # Set content type only once
        super(Page, self).__init__(*args, **kwargs)
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

    def get_absolute_url(self):
        '''Returns url to specific page.'''
        if not self.user:
            raise NoReverseMatch("Undefined owner of the page.")
        return reverse("astormain:page", 
                       kwargs={"username": self.user.slug, "page_id": self.id})    


class BasePage(Page):
    '''BasePage for creating other pages.'''
    verbose_name = "page"
    template_name = "astormain/pages/simple.html"

    title = models.CharField(
        max_length=255
    )
    created_date = models.DateTimeField(default=timezone.now)

    first_published_date = models.DateTimeField(
        null=True, editable=False, db_index=True
    )
    published_page = models.OneToOneField(
        "self", related_name="base_page",
        blank=True, null=True,
        on_delete=models.SET_NULL
    )

    tags = TaggableManager(blank=True)

    # Distinction between drafts and published pages
    editable = models.BooleanField(default=True, editable=False)
    live = models.BooleanField(default=False, editable=False)

    has_unpublished_changes = models.BooleanField(
        default=False,
        editable=False
    )
    latest_changes_date = models.DateTimeField(
        null=True,
        editable=False
    )

    def save(self, *args, **kwargs):
        '''Saves the page. Sets unpublished changes to True.'''
        self.has_unpublished_changes = True
        self.latest_changes_date = timezone.now()
        super(BasePage, self).save(*args, **kwargs)

    '''Add more informative name for save.'''
    save_draft = save

    def publish(self):
        '''Publish the page.'''
        if not self.published_page:
            self.first_published_date = timezone.now()
        else:
            self.published_page.delete()
            self.published_page = None

        pub_page = clone_page(self)
        pub_page.live = True
        pub_page.editable = False
        pub_page.save()

        self.published_page = pub_page
        self.has_unpublished_changes = False
        self.save()

        return pub_page


    def unpublish(self):
        '''Unpublish the page.'''
        if self.published_page:
            self.published_page.delete()
            self.published_page = None
            self.save()


@register_page
class IndexPage(BasePage):
    verbose_name = "index page"
    template_name = "astormain/pages/index.html"
    help_text = "Index Page. No one wants me anymore."

    abstract = models.TextField(default="", blank=True)    


@register_page
class ContentPage(BasePage):
    verbose_name = "content page"
    template_name = "astormain/pages/content.html"
    help_text = "Provide some content and I will be hapy."

    abstract = models.TextField(default="", blank=True) 
    body = models.TextField(blank=True)