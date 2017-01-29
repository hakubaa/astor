from django.db import models
from django.contrib.auth.models import AbstractUser, BaseUserManager
from django.utils import timezone
from django.contrib.contenttypes.models import ContentType
from django.contrib.contenttypes.fields import GenericForeignKey

from astorcore.models import Page


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


class UserManager(BaseUserManager):

    def create_user(self, username, password=None, root_page=None):
        user = self.model(username=username, root_page=root_page)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, username, password):
        user = self.create_user(username=username, password=password)
        user.is_admin = True
        user.save(using=self._db)
        return user


class User(AbstractUser):
    objects = UserManager()

    root_page = models.ForeignKey(
        Page, null=True, blank=True,
        on_delete=models.SET_NULL, related_name="owners",
        unique=False
    )

    def __init__(self, *args, root_page=None, **kwargs):
        super(AbstractUser, self).__init__(*args, **kwargs)
        self.external_root = root_page

    def save(self, *args, **kwargs):
        '''
        Saves object to db. Creates new root page for the user or adds user
        to owners of other page if root_page passed in the consturctor.
        '''
        first_save = self.pk is None
        super(AbstractUser, self).save(*args, **kwargs)
        if first_save:
            root4save = self.external_root or Page.add_root()
            root4save.owners.add(self)

    def set_root_page(self, page, remove_current_root=False):
        '''
        Change root page. Many users can share the same root page.
        '''
        current_root = self.root_page
        page.owners.add(self)
        if remove_current_root and current_root.owners.count() == 0:
            Page.delete(current_root)
        
    def add_page(self, instance):
        self.root_page.add_child(instance=instance)

    def add_activity(self, *args, instance=None, **kwargs):
        if not instance:
            instance = Activity(*args, **kwargs)
            instance.save()
        self.activities.add(instance)
        return instance