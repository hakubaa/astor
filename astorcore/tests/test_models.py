import unittest

from django.test import TestCase
from django.contrib.auth import get_user_model

from astorcore.models import BasePage, IndexPage, ContentPage


User = get_user_model()


class PageModelTest(TestCase):

    def test_for_adding_children_to_the_page(self):
        page = BasePage.add_root()
        page.add_child(instance=IndexPage(title="Chapter 1"))
        page.add_child(instance=IndexPage(title="Chapter 2"))
        self.assertEqual(page.get_children_count(), 2)

    def test_get_proper_object_from_the_tree(self):
        root_page = BasePage.add_root()
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