from django.test import TestCase
from django.contrib.auth import get_user_model
from django.contrib.contenttypes.models import ContentType

from astorcore.models import Page, IndexPage
from astoraccount.models import Activity

User = get_user_model()


class UserTest(TestCase):

    def test_init_base_page_for_new_users(self):
        user = User.objects.create_user(username="Test", password="test")
        self.assertEqual(Page.objects.count(), 1)
        page = Page.objects.first()
        self.assertEqual(user.root_page, page)

    def test_accepts_root_page_in_constructor(self):
        page = Page.add_root()
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
        self.assertEqual(Page.objects.count(), 1)

    def test_for_changing_user_root_page(self):
        user = User.objects.create(username="Test", password="test")
        page = Page.add_root()
        user.set_root_page(page)
        self.assertEqual(user.root_page, page)

    def test_set_root_page_removes_previous_page_when_required(self):
        user = User.objects.create(username="Test", password="test")
        page = Page.add_root()
        user.set_root_page(page, remove_current_root=True)
        self.assertEqual(Page.objects.count(), 1)

    def test_set_root_does_not_delete_previous_root_if_other_owners(self):
        user1 = User.objects.create(username="Test", password="test")
        user2 = User.objects.create(username="Test2", password="test",
                                    root_page=user1.root_page)
        page = Page.add_root()
        user2.set_root_page(page, remove_current_root=True)
        self.assertEqual(Page.objects.count(), 2)

    def test_add_page_adds_page_to_user_pages_hierarchy(self):
        user = User.objects.create_user(username="Test", password="test")
        page = IndexPage(title="My First Page")
        user.add_page(page)
        self.assertEqual(user.root_page.get_children().count(), 1)

    def test_add_activity_registers_new_activity_for_the_user(self):
        user = User.objects.create_user(username="Test", password="test")
        act = Activity(message="Win a lottery!")
        act.save()
        user.add_activity(instance=act)
        self.assertEqual(user.activities.count(), 1)
        self.assertEqual(user.activities.first(), act)

    def test_add_activity_create_activity_when_no_instance(self):
        user = User.objects.create_user(username="Test", password="test")
        user.add_activity(message="Win a lottery!", number=Activity.UPDATE_USER)
        self.assertEqual(user.activities.count(), 1)


class ActivityTest(TestCase):

    def test_set_user_as_content_object(self):
        user = User.objects.create_user(username="Test", password="test")
        act = Activity(message="Create new user.", content_object=user)
        act.save()
        ctype = act.content_type
        self.assertEqual(ctype, ContentType.objects.get_for_model(User))
        self.assertEqual(act.object_id, user.id)

    def test_set_page_as_content_object(self):
        page = Page.add_root()
        act = Activity(message="Create new page.", content_object=page)
        act.save()
        ctype = act.content_type
        self.assertEqual(ctype, ContentType.objects.get_for_model(Page))
        self.assertEqual(act.object_id, page.id)