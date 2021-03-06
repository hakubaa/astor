from django.db import models
from django.contrib.auth.models import AbstractUser, BaseUserManager
from django.utils import timezone
from django.contrib.contenttypes.models import ContentType
from django.contrib.contenttypes.fields import GenericForeignKey
from django.template.defaultfilters import slugify


class Activity(models.Model):
    timestamp = models.DateTimeField(default=timezone.now)
    message = models.TextField(default="")
    number = models.PositiveIntegerField(null=True, blank=True)
    user = models.ForeignKey("astoraccount.User", on_delete=models.CASCADE, 
                             related_name="activities", null=True, blank=True)
    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE,
                                     null=True, blank=True)
    object_id = models.PositiveIntegerField(null=True, blank=True)
    content_object = GenericForeignKey("content_type", "object_id")

    # Dictionary of activities
    NEW_USER = 10
    UPDATE_USER = 11
    NEW_PAGE = 20
    UPDATE_PAGE = 21
    PUBLISH_PAGE = 22
    DELETE_PAGE = 23


class User(AbstractUser):

    slug = models.SlugField(unique=True)

    @property
    def url_slug(self):
        return slugify(self.username)

    def __init__(self, *args, **kwargs):
        super(AbstractUser, self).__init__(*args, **kwargs)

    def save(self, *args, **kwargs):
        self.slug = slugify(self.username)
        super(AbstractUser, self).save(*args, **kwargs)

    def add_page(self, instance):
        '''Adds page to pages.'''
        if instance.pk is None:
            instance.save()
        self.pages.add(instance)
        return instance

    def add_activity(self, *args, instance=None, **kwargs):
        '''Registers new activity for the user.'''
        if not instance:
            instance = Activity(*args, **kwargs)
            instance.save()
        self.activities.add(instance)
        return instance