from django.db import models
from django.contrib.auth.models import AbstractUser

from astorcore.models import RootPage


class User(AbstractUser):

    def save(self, *args, **kwargs):
        '''Saves object to db. Creates root page for the user.'''
        super(AbstractUser, self).save(*args, **kwargs)
        root_page = RootPage.add_root(owner=self)

    def add_page(self, instance):
        self.root_page.add_child(instance=instance)
