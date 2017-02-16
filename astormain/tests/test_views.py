import unittest

from django.test import TestCase
from django.urls import resolve, reverse
from django.contrib.auth import get_user_model

from astormain.views import home_page
from astorcore.models import ContentPage, Page


User = get_user_model()


class HomePageTest(TestCase):

    def test_account_root_url_resolves_to_index_view(self):
        found = resolve("/")
        self.assertEqual(found.func, home_page)

    def test_uses_correct_template(self):
        response = self.client.get("/")
        self.assertTemplateUsed(response, "astormain/home.html")

    def test_sets_proper_link_to_my_astor_for_logged_in_users(self):
        user = User.objects.create_user(username="spider", 
                                        password="spiderpass")
        self.client.login(username="spider", password="spiderpass")
        response = self.client.get("/")
        self.assertContains(response, "/account/")

    def test_sets_link_to_login_in_my_astor_if_anonymouse_user(self):
        response = self.client.get("/")
        self.assertContains(response, "/login")

    def test_displays_titles_of_the_latest_entries(self):
        user = User.objects.create(username="Test", password="test")
        page = user.add_page(instance=ContentPage(title="My First Entry"))
        pub_page = page.publish()
        self.client.login(username="Test", password="test")
        response = self.client.get(reverse("astormain:home"))
        self.assertContains(response, page.specific.title)

    def test_displays_only_published_pages(self):
        user = User.objects.create_user(username="Test", password="test")
        page1 = user.add_page(ContentPage(title="My First Entry"))
        page2 = user.add_page(ContentPage(title="My Second Entry"))
        pub_page = page2.publish()
        self.assertEqual(Page.objects.count(), 3)
        self.client.login(username="Test", password="test")
        response = self.client.get(reverse("astormain:home"))
        self.assertNotContains(response, page1.specific.title)
        self.assertContains(response, page2.specific.title)


class PagesTest(TestCase):

    def create_user_with_page(self, **kwargs):
        user = User.objects.create_user(
            username=kwargs.get("username", "Test"), 
            password=kwargs.get("password", "test")
        )
        page = user.add_page(
            ContentPage(**(kwargs or dict(title="My First Page")))
        )
        return user, page    

    def test_uses_correct_template(self):
        user, page = self.create_user_with_page()
        self.client.login(username="Test", password="test")
        response = self.client.get(page.get_absolute_url())
        self.assertTemplateUsed(response, page.specific.template_name)

    def test_for_passing_page_to_template(self):
        user, page = self.create_user_with_page()
        self.client.login(username="Test", password="test")
        response = self.client.get(page.get_absolute_url())
        self.assertEqual(response.context["page"], page.specific)

    def test_renders_fieds_of_content_page(self):
        user, page = self.create_user_with_page(
            title="Content Page 2305",
            abstract="Applications of content pages",
            body="Contnet pages are created mainly for"
        )
        self.client.login(username="Test", password="test")
        response = self.client.get(page.get_absolute_url())
        self.assertContains(response, page.specific.title)
        self.assertContains(response, page.specific.abstract)
        self.assertContains(response, page.specific.body)

    def test_for_passing_comment_form_to_page(self):
        user, page = self.create_user_with_page(
            title="Content Page 2131",
            abstract="Applications of content pages",
            body="Content pages are created mainly for"
        )
        self.client.login(username="Test", password="test")
        response = self.client.get(page.get_absolute_url())
        self.assertIsInstance(response.context["form"], CommentForm)

