from copy import deepcopy

from django.conf import settings
from django.db import models
from django.utils import timezone
from django.contrib.contenttypes.models import ContentType
from django.contrib.contenttypes.fields import GenericForeignKey    
from django.urls import reverse
from django.urls.exceptions import NoReverseMatch

from treebeard.al_tree import AL_Node

from astorcore.decorators import register_page



class Page(AL_Node):
    verbose_name = "base page"

    class Meta:
        abstract = True

    # Fields requried by AL_Node
    parent = models.ForeignKey(
        "self", related_name='children_set', 
        null=True, db_index=True
    )
    node_order_by = ["pk"]
    # sib_order = models.PositiveIntegerField()

    # Required for creating hierarchy composed of different Pages
    content_type = models.ForeignKey(
        ContentType, related_name="%(app_label)s_%(class)s_pages", null=True,
        on_delete=models.SET_NULL
    )

    def __init__(self, *args, **kwargs):
        super(Page, self).__init__(*args, **kwargs)
        # Set content type only once
        if not self.id and not self.content_type_id:
            self.content_type = ContentType.objects.get_for_model(self)

    def add_child(self, **kwargs):
        '''
        Overrides add_child from AL_Node. Accepts already saved page which
        are added with move method.
        '''
        if "instance" in kwargs:
            obj = kwargs["instance"]
            if obj.pk is not None:
                obj.move(self, "sorted-child")
                return obj
        return super(Page, self).add_child(**kwargs)

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


class BasePage(RootPage):
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
        "BasePage", related_name="base_page",
        blank=True, null=True,
        on_delete=models.CASCADE
    )

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

    def delete(self, *args, **kwargs):
        '''Deletes the page and published page if required.'''
        if self.published_page:
            self.published_page.delete()
        super(BasePage, self).delete(*args, **kwargs)

    def publish(self):
        '''Publish the page.'''
        if not self.published_page:
            self.first_published_date = timezone.now()

        if type(self) == BasePage:
            new_page = deepcopy(self)
            new_page.pk = None
            new_page.id = None
            new_page.parent = None
        else:
            # Multi Table-Inheritance - copy base model
            new_base = deepcopy(self.basepage_ptr)
            new_base.pk = None
            new_base.id = None
            new_base.parent = None
            new_base.save()

            # Create new instance of the self's class
            new_page = self.content_type.model_class()(basepage_ptr=new_base)
            new_page.save()

            new_page.__dict__.update(
                dict(item for item in self.__dict__.items() 
                          if item[0] not in ("basepage_ptr", "id", "pk", "parent"))
            )

        new_page.published_page = None
        new_page.editable = False
        new_page.live = True
        new_page.save()

        if self.published_page:
            self.published_page.delete()

        self.has_unpublished_changes = False
        self.published_page = new_page
        self.save() 

        return new_page

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

    abstract = models.TextField(default="")    


@register_page
class ContentPage(BasePage):
    verbose_name = "content page"
    template_name = "astormain/pages/content.html"

    abstract = models.TextField(default="") 
    body = models.TextField()