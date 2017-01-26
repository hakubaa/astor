from django.test import TestCase
from django.contrib.auth import get_user_model

from astorcore.models import Page


User = get_user_model()


class PageModelTest(TestCase):

    def test_for_adding_children_to_the_page(self):
        page = Page.add_root(title="My First Page")
        ch1 = page.add_child(title="Chapter 1")
        ch2 = page.add_child(title="Chapter 2")
        self.assertEqual(page.get_children_count(), 2)
        self.assertListEqual(list(page.get_children()), [ch1, ch2])
        
    def test_for_setting_the_owner_of_the_page(self):
        page = Page.add_root(title="Main Page")
        user = User.objects.create(username="Test", password="test")
        page.set_owner(user)
        self.assertEqual(page.owner, user)

    def test_publish_sets_published_date(self):
        pass

        



class UserModelTest(TestCase):

    def create_user(self):
        pass

