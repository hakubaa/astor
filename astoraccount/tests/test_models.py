from django.test import TestCase
from django.contrib.auth import get_user_model

from astorcore.models import RootPage, Page

User = get_user_model()


class UserTest(TestCase):

    def test_init_root_page_for_new_users(self):
        user = User.objects.create_user(username="Test", password="test")
        self.assertEqual(RootPage.objects.count(), 1)
        page = RootPage.objects.first()
        self.assertEqual(page.owner, user)

    def test_add_page_adds_page_to_user_pages_hierarchy(self):
        user = User.objects.create_user(username="Test", password="test")
        page = Page(title="My First Page")
        user.add_page(page)
        self.assertEqual(user.root_page.get_children().count(), 1)
