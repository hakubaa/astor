from django.test import TestCase
from django.urls import resolve

from astoraccount.views import index_page
from astorcore.models import BasePage
import astorcore.decorators as decos


class AccountIndexPageTest(TestCase):

    def test_account_root_url_resolves_to_index_view(self):
        found = resolve("/account/")
        self.assertEqual(found.func, index_page)

    def test_uses_correct_template(self):
        response = self.client.get("/account/")
        self.assertTemplateUsed(response, "astoraccount/index.html")


class PageNewTest(TestCase):

    def test_renders_correct_template(self):
        response = self.client.get("/account/pages/new")
        self.assertTemplateUsed(response, "astoraccount/page_new.html")

    def test_shows_all_registered_types_of_pages(self):
        # Reset registry with pages
        decos.page_registry = []

        # Register few new type of pages
        @decos.register_page
        class EmptyPage(BasePage):
            verbose_name = "empty page"

        @decos.register_page
        class LinkPage(BasePage):
            verbose_name = "link page"

        response = self.client.get("/account/pages/new")
        content = response.content.decode().lower()

        self.assertIn(EmptyPage.verbose_name,content)
        self.assertIn(LinkPage.verbose_name, content) 
