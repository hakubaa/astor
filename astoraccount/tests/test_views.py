from django.test import TestCase
from django.urls import resolve
from django.contrib.auth import get_user_model
from django.contrib.contenttypes.models import ContentType

from astoraccount.views import index_page
from astorcore.models import Page, ContentPage
from astoraccount.forms import ContentPageForm
import astorcore.decorators as decos

User = get_user_model()


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
        class EmptyPage(Page):
            verbose_name = "empty page"

        @decos.register_page
        class LinkPage(Page):
            verbose_name = "link page"

        response = self.client.get("/account/pages/new")
        content = response.content.decode().lower()

        self.assertIn(EmptyPage.verbose_name,content)
        self.assertIn(LinkPage.verbose_name, content) 


class PageCreateTest(TestCase):

    def create_and_login_user(self, username="Test", password="test"):
        user = User.objects.create_user(username=username, password=password)
        self.client.login(username=username, password=password)
        return user

    def test_redirects_to_page_edit(self):
        user = self.create_and_login_user()
        response = self.client.get("/account/pages/create",
                                   {"type": "astorcore:contentpage"})
        user = User.objects.filter(username="Test").first()
        page_id = user.root_page.get_children()[0].id
        self.assertRedirects(response, "/account/pages/%d" % (page_id))

    def test_creates_a_page_for_the_user(self):
        user = self.create_and_login_user()
        self.client.get("/account/pages/create", 
                        {"type": "astorcore:contentpage"})
        self.assertEqual(Page.objects.count(), 2)
        user = User.objects.filter(username="Test").first()
        self.assertEqual(user.root_page.get_children_count(), 1)

    def test_creates_content_page(self):
        user = self.create_and_login_user()
        self.client.get("/account/pages/create", 
                       {"type": "astorcore:contentpage"})
        user = User.objects.filter(username="Test").first()
        page = user.root_page.get_children()[0]
        self.assertIsInstance(page.specific, ContentPage)


class PageEditTest(TestCase):

    def create_and_login_user(self, username="Test", password="test"):
        user = User.objects.create_user(username=username, password=password)
        self.client.login(username=username, password=password)
        return user

    def test_renders_correct_template(self):
        user = self.create_and_login_user()
        page = user.root_page.add_child(instance=ContentPage())
        response = self.client.get("/account/pages/%d" % page.id)
        self.assertTemplateUsed(response, "astoraccount/page_edit.html")

    def test_for_passing_correct_form_to_template(self):
        user = self.create_and_login_user()
        page = user.root_page.add_child(instance=ContentPage())
        response = self.client.get("/account/pages/%d" % page.id)
        self.assertIsInstance(response.context["form"], ContentPageForm)

    def test_for_saving_data_from_form(self):
        user = self.create_and_login_user()
        page = user.root_page.add_child(instance=ContentPage())
        self.client.post("/account/pages/%d" % page.id,
                        {"title": "First Edit Ever", "abstract": "Simple Page",
                         "body": "Nice body"})
        page = Page.objects.get(id=page.id)
        self.assertEqual(page.specific.title, "First Edit Ever")
        self.assertEqual(page.specific.abstract, "Simple Page")
        self.assertEqual(page.specific.body, "Nice body")

