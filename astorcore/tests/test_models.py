import unittest

from django.test import TestCase
from django.contrib.auth import get_user_model
from django.urls import reverse

from astorcore.models import RootPage, Page, IndexPage, ContentPage


User = get_user_model()


class PageModelTest(TestCase):

    def test_for_adding_children_to_the_page(self):
        page = Page.add_root()
        page.add_child(instance=IndexPage(title="Chapter 1"))
        page.add_child(instance=IndexPage(title="Chapter 2"))
        self.assertEqual(page.get_children_count(), 2)

    def test_get_proper_object_from_the_tree(self):
        root_page = Page.add_root()
        page1 = root_page.add_child(
            instance=IndexPage(title="Page 1", abstract="Test Page 1")
        )
        page2 = root_page.add_child(
            instance=ContentPage(title="Page 2", abstract="Contnet Page",
                                 body="Body of the page.")
        )
        pages = root_page.get_children()
        self.assertEqual(pages[0].specific.title, page1.title)
        self.assertEqual(pages[1].specific.body, page2.body)

    def test_for_setting_page_owner(self):
        user = User.objects.create(username="Test", password="test")
        page = RootPage.objects.first()
        self.assertEqual(page.owner, user)

    def test_get_root_owner_returns_owner_of_root_page(self):
        user = User.objects.create(username="Test", password="test")
        index = user.add_page(IndexPage(title="Index"))
        page = index.add_child(instance=ContentPage(title="Entry #1"))
        self.assertEqual(page.get_root_owner(), user)

    def test_get_absolute_url(self):
        user = User.objects.create(username="Test", password="test")
        page = user.add_page(instance=IndexPage(title="Test"))
        self.assertEqual(
            page.get_absolute_url(), 
            reverse("astormain:entry", kwargs={"username": user.slug,
                                               "page_id": page.id}))
