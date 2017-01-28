from django.test import TestCase
from django.contrib.auth import get_user_model

from astorcore.models import BasePage, IndexPage

User = get_user_model()


class UserTest(TestCase):

    def test_init_base_page_for_new_users(self):
        user = User.objects.create_user(username="Test", password="test")
        self.assertEqual(BasePage.objects.count(), 1)
        page = BasePage.objects.first()
        self.assertEqual(user.root_page, page)

    def test_accepts_root_page_in_constructor(self):
        page = BasePage.add_root()
        user = User.objects.create(username="Test", password="test",
                                   root_page=page)
        self.assertEqual(user.root_page, page)

    def test_two_users_with_the_same_root_page(self):
        user1 = User.objects.create(username="Test", password="test")
        user2 = User.objects.create(username="Test2", password="test",
                                    root_page=user1.root_page)
        users = list(User.objects.all())
        self.assertEqual(len(users), 2)
        self.assertEqual(users[0].root_page, users[1].root_page)
        self.assertEqual(BasePage.objects.count(), 1)

    def test_for_changing_user_root_page(self):
        user = User.objects.create(username="Test", password="test")
        page = BasePage.add_root()
        user.set_root_page(page)
        self.assertEqual(user.root_page, page)

    def test_set_root_page_removes_previous_page_when_required(self):
        user = User.objects.create(username="Test", password="test")
        page = BasePage.add_root()
        user.set_root_page(page, remove_current_root=True)
        self.assertEqual(BasePage.objects.count(), 1)

    def test_set_root_does_not_delete_previous_root_if_other_owners(self):
        user1 = User.objects.create(username="Test", password="test")
        user2 = User.objects.create(username="Test2", password="test",
                                    root_page=user1.root_page)
        page = BasePage.add_root()
        user2.set_root_page(page, remove_current_root=True)
        self.assertEqual(BasePage.objects.count(), 2)

    def test_add_page_adds_page_to_user_pages_hierarchy(self):
        user = User.objects.create_user(username="Test", password="test")
        page = IndexPage(title="My First Page")
        user.add_page(page)
        self.assertEqual(user.root_page.get_children().count(), 1)
