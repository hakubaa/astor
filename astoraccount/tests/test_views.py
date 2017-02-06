from django.test import TestCase
from django.urls import resolve, reverse
from django.contrib.auth import get_user_model, get_user
from django.contrib.contenttypes.models import ContentType

from astoraccount.views import index_page
from astorcore.models import BasePage, ContentPage
from astoraccount.forms import ContentPageForm
import astorcore.decorators as decos

User = get_user_model()


class AstorTestCase(TestCase):

    def create_and_login_user(self, username="Test", password="test"):
        user = User.objects.create_user(username=username, password=password)
        self.client.login(username=username, password=password)
        return user


class AccountIndexPageTest(AstorTestCase):

    def test_account_root_url_resolves_to_index_view(self):
        self.create_and_login_user()
        found = resolve("/account/")
        self.assertEqual(found.func, index_page)

    def test_uses_correct_template(self):
        self.create_and_login_user()
        response = self.client.get("/account/")
        self.assertTemplateUsed(response, "astoraccount/index.html")


class PageNewTest(AstorTestCase):

    def test_renders_correct_template(self):
        self.create_and_login_user()
        response = self.client.get(reverse("astoraccount:page_new"))
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

        self.create_and_login_user()
        response = self.client.get(reverse("astoraccount:page_new"))
        content = response.content.decode().lower()

        self.assertIn(EmptyPage.verbose_name,content)
        self.assertIn(LinkPage.verbose_name, content) 


class PageCreateTest(AstorTestCase):

    def test_redirects_to_page_edit(self):
        user = self.create_and_login_user()
        response = self.client.get(reverse("astoraccount:page_create"),
                                   {"type": "astorcore:contentpage"})
        user = User.objects.filter(username="Test").first()
        page_id = user.pages.all()[0].id
        self.assertRedirects(
            response, 
            reverse("astoraccount:page_edit", kwargs={"page_id": page_id})
        )

    def test_creates_a_page_for_the_user(self):
        user = self.create_and_login_user()
        self.client.get(reverse("astoraccount:page_create"), 
                        {"type": "astorcore:contentpage"})
        self.assertEqual(BasePage.objects.count(), 1)
        user = User.objects.filter(username="Test").first()
        self.assertEqual(user.pages.count(), 1)

    def test_creates_content_page(self):
        user = self.create_and_login_user()
        self.client.get(reverse("astoraccount:page_create"), 
                       {"type": "astorcore:contentpage"})
        user = User.objects.filter(username="Test").first()
        page = user.pages.all()[0]
        self.assertIsInstance(page.specific, ContentPage)


class PageEditTest(AstorTestCase):

    def test_renders_correct_template(self):
        user = self.create_and_login_user()
        page = user.add_page(instance=ContentPage())
        response = self.client.get(reverse("astoraccount:page_edit", 
                                           kwargs={"page_id": page.id}),)
        self.assertTemplateUsed(response, "astoraccount/page_edit.html")

    def test_for_passing_correct_form_to_template(self):
        user = self.create_and_login_user()
        page = user.add_page(instance=ContentPage())
        response = self.client.get(reverse("astoraccount:page_edit", 
                                           kwargs={"page_id": page.id}),)
        self.assertIsInstance(response.context["form"], ContentPageForm)

    def test_for_saving_data_from_form(self):
        user = self.create_and_login_user()
        page = user.add_page(instance=ContentPage())
        self.client.post(reverse("astoraccount:page_edit", 
                                 kwargs={"page_id": page.id}),
                        {"title": "First Edit Ever", "abstract": "Simple Page",
                         "body": "Nice body"})
        page = BasePage.objects.get(id=page.id)
        self.assertEqual(page.specific.title, "First Edit Ever")
        self.assertEqual(page.specific.abstract, "Simple Page")
        self.assertEqual(page.specific.body, "Nice body")    


class AuthViewsTest(AstorTestCase):

    def test_for_logging_in_using_login_view(self):
        user = User.objects.create_user(username="Test", password="test")
        response = self.client.post(reverse("astoraccount:login"),
                                    {"username": "Test", "password": "test"})
        self.client.login(username="Test", password="test")
        user = get_user(self.client)
        self.assertTrue(user.is_authenticated)
