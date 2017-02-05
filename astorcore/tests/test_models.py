import unittest

from django.test import TestCase
from django.contrib.auth import get_user_model
from django.urls import reverse

from astorcore.models import RootPage, IndexPage, ContentPage, BasePage


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

    def test_add_child_accepts_already_saved_page(self):
        root = RootPage()
        root.save()
        page = BasePage()
        page.save()
        page = root.add_child(instance=page)
        self.assertEqual(root.get_children_count(), 1)


class BasePageTest(TestCase):

    def test_publish_creates_new_page_with_the_same_data(self):
        page = BasePage.add_root(title="My First Page")
        page.publish()
        self.assertEqual(BasePage.objects.count(), 2)
        page1, page2 = BasePage.objects.all()
        self.assertEqual(page1.title, page2.title)

    def test_publish_returns_new_page(self):
        page = BasePage.add_root(title="My First Page")
        new_page = page.publish()
        list_ = list(BasePage.objects.all())

        self.assertCountEqual(list_, [page, new_page])

    def test_published_new_page_has_the_same_owner(self):
        user = User.objects.create(username="Test", password="test")
        page = user.add_page(instance=BasePage(title="Test"))
        new_page = page.publish()
        self.assertEqual(user, new_page.base_page.get_root_owner())

    def test_publish_creates_relation_to_published_page(self):
        page = BasePage.add_root(title="My First Page")
        new_page = page.publish()
        self.assertEqual(page.published_page, new_page)

    def test_multiple_publish_creates_only_one_page(self):
        page = BasePage.add_root(title="My First Page")
        page.publish()
        page.publish()  
        page.publish()
        self.assertEqual(BasePage.objects.count(), 2)

    def test_unpublish_removes_previously_published_page(self):
        page = BasePage.add_root(title="My First Page")
        page.publish()
        page.unpublish()
        self.assertEqual(BasePage.objects.count(), 1)

    def test_publish_page_after_unpublishing(self):
        page = BasePage.add_root(title="My First Page")
        page.publish()
        page.unpublish()
        new_page = page.publish()
        self.assertEqual(BasePage.objects.count(), 2)
        self.assertEqual(new_page.title, "My First Page")

    def test_for_chaning_draft_only(self):
        page = BasePage.add_root(title="My First Page")
        page.publish()
        page.title = "Updated Title"
        page.save()
        self.assertEqual(page.published_page.title, "My First Page")

    def test_deletes_published_page_with_the_draft_page(self):
        page = BasePage.add_root(title="My First Page")
        page.publish()
        page.delete()
        self.assertEqual(BasePage.objects.count(), 0)

    def test_published_page_has_no_parent_page(self):
        page = BasePage.add_root(title="My First Page")
        new_page = page.publish()
        self.assertIsNone(new_page.parent)

    def test_publishes_child_page(self):
        root = RootPage.add_root()
        page = root.add_child(instance=BasePage())
        pug_page = page.publish()
        self.assertEqual(BasePage.objects.count(), 2)
        self.assertEqual(BasePage.objects.filter(live=True).count(), 1)

    def test_publishes_subclass_of_base_page(self):
        root = RootPage.objects.create()
        page = root.add_child(instance=ContentPage(title="My First Page"))
        pug_page = page.publish()
        self.assertEqual(BasePage.objects.count(), 2)

    def test_publish_sets_page_as_live(self):
        user = User.objects.create_user(username="Test", password="test")
        page1 = user.add_page(ContentPage(title="My First Entry"))
        page2 = user.add_page(ContentPage(title="My Second Entry"))
        pub_page2 = page2.publish()
        self.assertTrue(pub_page2.live)

    def test_publish_users_page(self):
        user = User.objects.create_user(username="Test", password="test")
        page1 = user.add_page(instance=ContentPage(title="My First Entry"))
        page2 = user.add_page(instance=ContentPage(title="FUCK"))
        pub_page = page2.publish()
        self.assertEqual(BasePage.objects.count(), 3)