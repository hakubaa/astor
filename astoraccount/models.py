from django.db import models
from django.contrib.auth.models import AbstractUser, BaseUserManager

from astorcore.models import BasePage


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
        BasePage, null=True, blank=True,
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
            root4save = self.external_root or BasePage.add_root()
            root4save.owners.add(self)

    def set_root_page(self, page, remove_current_root=False):
        '''
        Change root page. Many users can share the same root page.
        '''
        current_root = self.root_page
        page.owners.add(self)
        if remove_current_root and current_root.owners.count() == 0:
            BasePage.delete(current_root)
        
    def add_page(self, instance):
        self.root_page.add_child(instance=instance)