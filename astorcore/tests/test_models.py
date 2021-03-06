import unittest

from django.test import TestCase, RequestFactory
from django.contrib.auth import get_user_model
from django.contrib.auth.models import AnonymousUser
from django.urls import reverse

from astorcore.models import (
    ContentPage, Page, Comment, PageVisit
)


User = get_user_model()


class PageModelTest(TestCase):

    def test_create_and_save_page(self):
        page = Page()
        page.save()
        self.assertIsNotNone(page.pk)

    def test_get_absolute_url(self):
        user = User.objects.create(username="Test", password="test")
        page = user.add_page(instance=Page())
        self.assertEqual(
            page.get_absolute_url(), 
            reverse("astormain:page", kwargs={"slug": user.slug,
                                              "pk": page.pk}))

    def test_specific_returns_correct_type(self):
        page = ContentPage(title="Test")
        page.save()
        self.assertIs(type(page.specific), ContentPage)


class ContentPageTest(TestCase):

    def test_publish_creates_new_page_with_the_same_data(self):
        page = ContentPage.objects.create(title="My First Page")
        page.publish()
        self.assertEqual(ContentPage.objects.count(), 2)
        page1, page2 = ContentPage.objects.all()
        self.assertEqual(page1.title, page2.title)

    def test_publish_returns_new_page(self):
        page = ContentPage.objects.create(title="My First Page")
        new_page = page.publish()
        list_ = list(ContentPage.objects.all())

        self.assertCountEqual(list_, [page, new_page])

    def test_published_new_page_has_the_same_user(self):
        user = User.objects.create(username="Test", password="test")
        page = user.add_page(instance=ContentPage(title="Test"))
        new_page = page.publish()
        self.assertEqual(user, new_page.user)

    def test_publish_creates_relation_to_published_page(self):
        page = ContentPage.objects.create(title="My First Page")
        new_page = page.publish()
        self.assertEqual(page.published_page, new_page)

    def test_multiple_publish_creates_only_one_page(self):
        page = ContentPage.objects.create(title="My First Page")
        page.publish()
        page.publish()  
        page.publish()
        self.assertEqual(ContentPage.objects.count(), 2)

    def test_unpublish_removes_previously_published_page(self):
        page = ContentPage.objects.create(title="My First Page")
        page.publish()
        page.unpublish()
        self.assertEqual(ContentPage.objects.count(), 1)

    def test_publish_page_after_unpublishing(self):
        page = ContentPage.objects.create(title="My First Page")
        page.publish()
        page.unpublish()
        new_page = page.publish()
        self.assertEqual(ContentPage.objects.count(), 2)
        self.assertEqual(new_page.title, "My First Page")

    def test_for_chaning_draft_only(self):
        page = ContentPage.objects.create(title="My First Page")
        page.publish()
        page.title = "Updated Title"
        page.save()
        self.assertEqual(page.published_page.title, "My First Page")

    def test_deleting_draft_does_not_deletes_published_page(self):
        page = ContentPage.objects.create(title="My First Page")
        pub_page = page.publish()
        page.delete()
        self.assertEqual(ContentPage.objects.count(), 1)
        self.assertEqual(ContentPage.objects.first().id, pub_page.id)

    def test_publishes_subclass_of_base_page(self):
        page = ContentPage.objects.create(title="My First Page")
        pub_page = page.publish()
        self.assertEqual(ContentPage.objects.count(), 2)

    def test_publish_sets_page_as_live(self):
        user = User.objects.create_user(username="Test", password="test")
        page1 = user.add_page(ContentPage(title="My First Entry"))
        page2 = user.add_page(ContentPage(title="My Second Entry"))
        pub_page2 = page2.publish()
        self.assertTrue(pub_page2.live)

    def test_publish_users_page(self):
        user = User.objects.create_user(username="Test", password="test")
        page1 = user.add_page(instance=ContentPage(title="My First Entry"))
        page2 = user.add_page(instance=ContentPage(title="F**K"))
        pub_page = page2.publish()
        self.assertEqual(ContentPage.objects.count(), 3)

    def test_can_add_tags_to_page(self):
        user = User.objects.create_user(username="Test", password="test")
        page = user.add_page(ContentPage(title="My First Entry"))
        page.tags.add("entry", "intro", "astor")
        page = Page.objects.first().specific
        self.assertEqual(page.tags.count(), 3)
        tags = [ tag.name for tag in page.tags.all() ]
        self.assertCountEqual(tags, ["entry", "intro", "astor"])

    def test_for_adding_comment_to_page(self):
        user = User.objects.create_user(username="Test", password="test")
        page = user.add_page(ContentPage(title="My First Entry"))
        comment = page.add_comment(body="Very nice entry.")
        page.refresh_from_db()
        self.assertEqual(page.comments.count(), 1)
        self.assertEqual(page.comments.all()[0].body, comment.body)

    def test_add_comment_accepts_instance(self):
        user = User.objects.create_user(username="Test", password="test")
        page = user.add_page(ContentPage(title="My First Entry"))
        comment = Comment.objects.create(body="Very nice entry.", author=user)
        page.add_comment(comment)
        page.refresh_from_db()
        self.assertEqual(page.comments.count(), 1)
        self.assertEqual(page.comments.all()[0].body, comment.body)


class PageVisitTest(TestCase):

    def test_register_visit_creates_new_pagevisit(self):
        page = ContentPage.objects.create(title="Test Page")
        page.register_visit()
        self.assertEqual(PageVisit.objects.count(), 1)

    def test_register_visit_sets_proper_page_and_user(self):
        user = User.objects.create_user(username="Test", password="test")
        page = ContentPage.objects.create(title="Test Page")
        page.register_visit(user=user)
        visit = PageVisit.objects.first()
        self.assertEqual(visit.page.specific, page.specific)        
        self.assertEqual(visit.user, user)

    def test_register_visit_accepts_request_as_first_argument(self):
        page = ContentPage.objects.create(title="Test Page")
        request = RequestFactory().get("/fake_url")
        page.register_visit(request)

    def test_register_visit_takes_user_from_request(self):
        user = User.objects.create_user(username="Test", password="test")
        page = ContentPage.objects.create(title="Teset Page")
        request = RequestFactory().get("/fake_url")
        request.user = user
        request.session = {}
        page.register_visit(request)
        visit = PageVisit.objects.first()
        self.assertEqual(visit.user, user)

    def test_register_visit_ignores_anonymous_user(self):
        page = ContentPage.objects.create(title="Test Page")
        request = RequestFactory().get("/fake_url")
        request.user = AnonymousUser()
        page.register_visit(request)
        visit = PageVisit.objects.first()
        self.assertIsNone(visit.user)

    def test_inspect_page_visits_frequency(self):
        page = ContentPage.objects.create(title="Test Page")
        page.register_visit()
        page.register_visit()
        self.assertEqual(page.visits.count(), 2)

    def test_ignores_multiple_visits_from_the_same_ip(self):
        page = ContentPage.objects.create(title="Test Page")
        request = RequestFactory().get("/fake_url")
        request.user = AnonymousUser()
        request.META = dict(REMOTE_ADDR="127.0.0.1")
        page.register_visit(request)
        page.register_visit(request)
        self.assertEqual(page.visits.count(), 1)

class CommentTest(TestCase):

    def create_user_and_page(self):
        user = User.objects.create_user(username="Test", password="test")
        page = user.add_page(ContentPage(title="My First Entry"))   
        return user, page  

    def test_for_replying_to_comment(self):
        user, page = self.create_user_and_page()
        comment = page.add_comment(body="Comment #1")
        reply = comment.reply(body="Comment #2")
        self.assertEqual(Comment.objects.count(), 2)
        self.assertEqual(reply.parent, comment)
        self.assertIn(reply, comment.replies.all())