import unittest
import random
import string
import io
import operator
from unittest.mock import Mock, patch
from functools import partial

from django.test import TestCase
from django.urls import resolve, reverse
from django.contrib.auth import get_user_model, get_user
from django.contrib.contenttypes.models import ContentType
from django.core.files.uploadedfile import SimpleUploadedFile

from astorcore.models import (
    ContentPage, Page, HTMLUploadPage
)
from astoraccount.forms import (
    ContentPageForm, HTMLUploadPageForm
)
import astorcore.decorators as decos

User = get_user_model()


class AstorTestCase(TestCase):

    def create_and_login_user(self, username="Test", password="test"):
        user = User.objects.create_user(username=username, password=password)
        self.client.login(username=username, password=password)
        return user


class AccountIndexPageTest(AstorTestCase):

    def test_uses_correct_template(self):
        self.create_and_login_user()
        response = self.client.get(reverse("astoraccount:index"))
        self.assertTemplateUsed(response, "astoraccount/index.html")

    def test_passes_recent_edits_to_template(self):
        user = self.create_and_login_user()
        page = user.add_page(instance=ContentPage(title="My First Page"))
        response = self.client.get(reverse("astoraccount:index"))
        self.assertEqual(response.context["recent_edits"][0], page)


class PageNewTest(AstorTestCase):

    def test_renders_correct_template(self):
        self.create_and_login_user()
        response = self.client.get(reverse("astoraccount:page_new"))
        self.assertTemplateUsed(response, "astoraccount/page_new.html")

    @unittest.skip
    def test_shows_all_registered_types_of_pages(self):
        # Reset registry with pages
        decos.page_registry = []

        # Register few new type of pages
        @decos.register_page
        class EmptyPage(ContentPage):
            verbose_name = "empty page"

        @decos.register_page
        class LinkPage(ContentPage):
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
        page = user.pages.all()[0]
        self.assertRedirects(
            response, 
            reverse("astoraccount:page_edit", kwargs={"pk": page.pk})
        )

    def test_creates_a_page_for_the_user(self):
        user = self.create_and_login_user()
        self.client.get(reverse("astoraccount:page_create"), 
                        {"type": "astorcore:contentpage"})
        self.assertEqual(ContentPage.objects.count(), 1)
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
                                           kwargs={"pk": page.pk}))
        self.assertTemplateUsed(response, "astoraccount/page_edit.html")

    def test_redirects_to_404_when_invalid_page_number(self):
        user = self.create_and_login_user()
        page = user.add_page(instance=ContentPage())
        response = self.client.get(reverse("astoraccount:page_edit", 
                                           kwargs={"pk": page.pk+2}))        
        self.assertRedirects(response, reverse("astoraccount:404"))

    def test_for_passing_correct_form_to_template(self):
        user = self.create_and_login_user()
        page = user.add_page(instance=ContentPage())
        response = self.client.get(reverse("astoraccount:page_edit", 
                                           args=(page.id,)))
        self.assertEqual(type(response.context["form"]), ContentPageForm)

    def test_for_passing_correct_form_to_tempalte2(self):
        user = self.create_and_login_user()
        page = user.add_page(instance=ContentPage())
        response = self.client.get(reverse("astoraccount:page_edit", 
                                           args=(page.id,)))
        self.assertEqual(type(response.context["form"]), ContentPageForm)        

    def test_for_saving_data_from_form(self):
        user = self.create_and_login_user()
        page = user.add_page(instance=ContentPage())
        self.client.post(reverse("astoraccount:page_edit", 
                                 kwargs={"pk": page.pk}),
                        {"title": "First Edit Ever", "abstract": "Simple Page",
                         "body": "Nice body"})
        page = ContentPage.objects.get(id=page.id)
        self.assertEqual(page.specific.title, "First Edit Ever")
        self.assertEqual(page.specific.abstract, "Simple Page")
        self.assertEqual(page.specific.body, "Nice body")

    def test_for_saving_draft(self):
        user = self.create_and_login_user()
        page = user.add_page(instance=ContentPage())
        self.client.post(reverse("astoraccount:page_edit", 
                                 kwargs={"pk": page.pk}),
                        {"title": "First Edit Ever", "abstract": "Simple Page",
                         "body": "Nice body", "action_type": "save_draft"})
        page.refresh_from_db()
        self.assertEqual(Page.objects.count(), 1)
        self.assertIsNone(page.published_page)

    def test_for_publishing_page(self):
        user = self.create_and_login_user()
        page = user.add_page(instance=ContentPage())
        self.client.post(reverse("astoraccount:page_edit", 
                                 kwargs={"pk": page.pk}),
                        {"title": "First Edit Ever", "abstract": "Simple Page",
                         "body": "Nice body", "action_type": "publish"})       
        self.assertEqual(Page.objects.count(), 2)
        page.refresh_from_db()
        self.assertIsNotNone(page.published_page)

    def test_use_tags_names_when_populating_form(self):
        user = self.create_and_login_user()
        page = user.add_page(instance=ContentPage(title="It's time!!!"))
        page.tags.add("one", "two", "three")
        response =  self.client.get(
            reverse("astoraccount:page_edit", kwargs={"pk": page.pk})
        ) 
        self.assertCountEqual(
            list(map(
                lambda x: x.strip(), 
                response.context["form"]["tags"].value().split(",")
            )),
            ["one", "two", "three"]
        )


class UploadPageTest(AstorTestCase):

    def test_for_handling_post_request(self):
        user = self.create_and_login_user()
        page = user.add_page(instance=HTMLUploadPage())

        html_page = SimpleUploadedFile(
            "test.html", b"<html></html>", content_type="text/html"
        )
    
        response = self.client.post(
            reverse("astoraccount:page_edit", kwargs={"pk": page.pk}),
            {"title": "My First File", "file": html_page,
             "action_type": "save_draft"}
        )

        self.assertEqual(response.status_code, 200)


class AuthViewsTest(AstorTestCase):

    def test_for_logging_in_using_login_view(self):
        user = User.objects.create_user(username="Test", password="test")
        response = self.client.post(reverse("astoraccount:login"),
                                    {"username": "Test", "password": "test"})
        self.client.login(username="Test", password="test")
        user = get_user(self.client)
        self.assertTrue(user.is_authenticated)


class AnalysesPageTest(AstorTestCase):

    def generate_pages_for_user(self, user, n=10):
        titles = [ ''.join(random.choice(string.ascii_uppercase + 
                                         string.digits) for _ in range(20))
                   for _ in range(n) ]
        pages = [ user.add_page(instance=ContentPage(title=title)) 
                  for title in titles ]
        return pages

    def test_renders_correct_template(self):
        user = self.create_and_login_user()
        response = self.client.get(reverse("astoraccount:analyses")) 
        self.assertTemplateUsed(response, "astoraccount/analyses.html")

    def test_for_passing_analyses_to_template(self):
        user = self.create_and_login_user()
        pages = self.generate_pages_for_user(user, 5)
        response = self.client.get(reverse("astoraccount:analyses"))
        self.assertEqual(len(response.context["analyses"]), len(pages))
        self.assertTrue(all(page in response.context["analyses"] for page in pages))

    def test_renders_titles_of_analyses(self):
        user = self.create_and_login_user()
        pages = self.generate_pages_for_user(user, 7)
        response = self.client.get(reverse("astoraccount:analyses"))
        content = response.content.decode("utf-8")
        self.assertTrue(all(page.specific.title in content for page in pages))

    def test_renders_only_10_analyses(self):
        user = self.create_and_login_user()
        pages = self.generate_pages_for_user(user, 20)
        response = self.client.get(reverse("astoraccount:analyses"))
        self.assertEqual(len(response.context["analyses"]), 10)

    def test_do_not_show_published_analyses(self):
        user = self.create_and_login_user()
        pages = self.generate_pages_for_user(user, 2)
        for page in pages:
            page.publish()
        response = self.client.get(reverse("astoraccount:analyses"))
        self.assertEqual(len(response.context["analyses"]), 2)
