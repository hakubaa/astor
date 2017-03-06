import unittest

from django.test import TestCase, RequestFactory
from django.urls import resolve, reverse
from django.contrib.auth import get_user_model

from astorcore.models import (
    ContentPage, Page, Comment, HTMLUploadPage, PageVisit, BasePage
)
from astormain.forms import CommentForm, ReplyForm
import astormain.views as views


User = get_user_model()


class HomePageTest(TestCase):

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

    def test_displays_titles_of_the_latest_analyses(self):
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


class UserProfileTest(TestCase):

    def create_user_with_analyses(self, n=5):
        user = User.objects.create_user(username="Test", password="test123")
        for i in range(n):
            user.add_page(ContentPage(
                title="Test Title #{:d}".format(i),
                abstract="Test Abstract #{:d}".format(i)
            ))
        return user

    def test_for_rendering_correct_template(self):
        user = self.create_user_with_analyses(n=0)
        response = self.client.get(
            reverse("astormain:profile", kwargs={"slug": user.slug})
        )
        self.assertTemplateUsed(response, "astormain/profile.html")

    def test_for_passing_analyses_to_template(self):
        user = self.create_user_with_analyses(n=1)
        response = self.client.get(
            reverse("astormain:profile", kwargs={"slug": user.slug})
        )
        analyses = response.context["analyses"]
        self.assertIsNotNone(analyses)

    def test_for_listing_analyses_with_title_and_abstract(self):
        user = self.create_user_with_analyses(n=2)
        page1, page2 = list(user.pages.all())
        page1.specific.publish()
        page2.specific.publish()
        response = self.client.get(
            reverse("astormain:profile", kwargs={"slug": user.slug})
        )
        content = response.content.decode()
        self.assertIn(page1.specific.title, content)
        self.assertIn(page2.specific.title, content)
        self.assertIn(page1.specific.abstract, content)
        self.assertIn(page2.specific.abstract, content)

    def test_for_listing_only_published_analyses(self):
        user = self.create_user_with_analyses(n=2)
        page1, page2 = list(user.pages.all())
        page1.specific.publish()
        response = self.client.get(
            reverse("astormain:profile", kwargs={"slug": user.slug})
        )
        content = response.content.decode()
        self.assertIn(page1.specific.title, content)
        self.assertNotIn(page2.specific.title, content)
        self.assertIn(page1.specific.abstract, content)
        self.assertNotIn(page2.specific.abstract, content)        


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

    @unittest.skip
    def test_for_passing_reply_form_to_page(self):
        user, page = self.create_user_with_page(
            title="Content Page 2131",
            abstract="Applications of content pages",
            body="Content pages are created mainly for"
        )
        self.client.login(username="Test", password="test")
        response = self.client.get(page.get_absolute_url())
        self.assertIsInstance(response.context["reply_form"], ReplyForm)        

    def test_post_request_creates_new_comment(self):
        user, page = self.create_user_with_page(
            title="Content Page 2131",
            abstract="Applications of content pages",
            body="Content pages are created mainly for"
        )
        self.client.login(username="Test", password="test")
        response = self.client.post(
            page.get_absolute_url(),
            {"body": "Nice page!"}
        )
        self.assertEqual(Comment.objects.count(), 1)
        comment = Comment.objects.first()
        self.assertEqual(comment.body, "Nice page!")
        self.assertEqual(comment.page.specific, page)
        self.assertEqual(page.comments.count(), 1)


class RegisterVisitTest(TestCase):

    def create_user_with_page(self, **kwargs):
        user = User.objects.create_user(
            username=kwargs.get("username", "Test"), 
            password=kwargs.get("password", "test")
        )
        page = user.add_page(
            BasePage(**(kwargs or dict(title="My First Page")))
        )
        return user, page    

    def test_registers_visit_of_anonymous_user(self):
        user, page = self.create_user_with_page()
        self.client.get(page.get_absolute_url())
        self.assertEqual(page.visits.count(), 1)
        visit = page.visits.first()
        self.assertIsNone(visit.user)

    def test_registers_visit_of_logged_in_user(self):
        user, page = self.create_user_with_page()
        self.client.login(username="Test", password="test")
        self.client.get(page.get_absolute_url())
        self.assertEqual(page.visits.count(), 1)
        visit = page.visits.first()
        self.assertEqual(visit.user, user)

    def test_registers_only_the_first_visit_from_given_id(self):
        user, page = self.create_user_with_page()
        self.client.get(page.get_absolute_url())
        self.client.login(username="Test", password="test")
        self.client.get(page.get_absolute_url())
        self.assertEqual(page.visits.count(), 1)
        visit = page.visits.first()
        self.assertIsNone(visit.user)


class ExternalFileView(TestCase):

    @staticmethod
    def setup_view(view, request, *args, **kwargs):
        view.request = request
        view.args = args
        view.kwargs = kwargs
        return view

    def test_get_object_returns_specific_page(self):
        user = User.objects.create_user(username="Test", password="test")
        page = user.add_page(HTMLUploadPage(title="File Page", file="test.html"))

        request_factory = RequestFactory()
        request = request_factory.get(
            "/fake_url", data={"slug": user.slug, "pk": page.pk}
        )

        view = views.ExternalFileView()
        view = ExternalFileView.setup_view(view, request, slug=user.slug, 
                                         pk=page.pk)

        page_view = view.get_object()

        self.assertEqual(page, page_view)

    def test_returns_correct_template(self):
        user = User.objects.create_user(username="Test", password="test")
        page = user.add_page(HTMLUploadPage(title="File Page", file="test.html"))

        request_factory = RequestFactory()
        request = request_factory.get(
            "/fake_url", data={"slug": user.slug, "pk": page.pk}
        )

        view = views.ExternalFileView()
        view = ExternalFileView.setup_view(view, request, slug=user.slug, 
                                         pk=page.pk)
                                                 
        self.assertEqual("/media/" + view.get_template_names()[0], page.file.url)