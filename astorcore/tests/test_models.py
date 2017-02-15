import unittest

from django.test import TestCase
from django.contrib.auth import get_user_model
from django.urls import reverse

from astorcore.models import IndexPage, ContentPage, BasePage, Page, Comment


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
            reverse("astormain:page", kwargs={"username": user.slug,
                                              "page_id": page.id}))

    def test_specific_returns_correct_type(self):
        page = BasePage(title="Test")
        page.save()
        self.assertIs(type(page.specific), BasePage)


class BasePageTest(TestCase):

    def test_publish_creates_new_page_with_the_same_data(self):
        page = BasePage.objects.create(title="My First Page")
        page.publish()
        self.assertEqual(BasePage.objects.count(), 2)
        page1, page2 = BasePage.objects.all()
        self.assertEqual(page1.title, page2.title)

    def test_publish_returns_new_page(self):
        page = BasePage.objects.create(title="My First Page")
        new_page = page.publish()
        list_ = list(BasePage.objects.all())

        self.assertCountEqual(list_, [page, new_page])

    def test_published_new_page_has_the_same_user(self):
        user = User.objects.create(username="Test", password="test")
        page = user.add_page(instance=BasePage(title="Test"))
        new_page = page.publish()
        self.assertEqual(user, new_page.user)

    def test_publish_creates_relation_to_published_page(self):
        page = BasePage.objects.create(title="My First Page")
        new_page = page.publish()
        self.assertEqual(page.published_page, new_page)

    def test_multiple_publish_creates_only_one_page(self):
        page = BasePage.objects.create(title="My First Page")
        page.publish()
        page.publish()  
        page.publish()
        self.assertEqual(BasePage.objects.count(), 2)

    def test_unpublish_removes_previously_published_page(self):
        page = BasePage.objects.create(title="My First Page")
        page.publish()
        page.unpublish()
        self.assertEqual(BasePage.objects.count(), 1)

    def test_publish_page_after_unpublishing(self):
        page = BasePage.objects.create(title="My First Page")
        page.publish()
        page.unpublish()
        new_page = page.publish()
        self.assertEqual(BasePage.objects.count(), 2)
        self.assertEqual(new_page.title, "My First Page")

    def test_for_chaning_draft_only(self):
        page = BasePage.objects.create(title="My First Page")
        page.publish()
        page.title = "Updated Title"
        page.save()
        self.assertEqual(page.published_page.title, "My First Page")

    def test_deleting_draft_does_not_deletes_published_page(self):
        page = BasePage.objects.create(title="My First Page")
        pub_page = page.publish()
        page.delete()
        self.assertEqual(BasePage.objects.count(), 1)
        self.assertEqual(BasePage.objects.first().id, pub_page.id)

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
        self.assertEqual(BasePage.objects.count(), 3)

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