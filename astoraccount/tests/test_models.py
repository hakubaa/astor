from django.test import TestCase
from django.contrib.auth import get_user_model
from django.contrib.contenttypes.models import ContentType
from django.template.defaultfilters import slugify

from astorcore.models import BasePage, IndexPage, RootPage
from astoraccount.models import Activity


User = get_user_model()


class UserTest(TestCase):

    def test_init_root_page_for_new_users(self):
        user = User.objects.create_user(username="Test", password="test")
        self.assertEqual(RootPage.objects.count(), 1)
        page = RootPage.objects.first()
        self.assertEqual(user.root_page, page)

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

    def test_creates_slug_on_the_base_of_username(self):
        user = User.objects.create_user(username="The Maste of the Universe", 
                                        password="test")
        self.assertEqual(user.slug, slugify(user.username))


class ActivityTest(TestCase):

    def test_set_user_as_content_object(self):
        user = User.objects.create_user(username="Test", password="test")
        act = Activity(message="Create new user.", content_object=user)
        act.save()
        ctype = act.content_type
        self.assertEqual(ctype, ContentType.objects.get_for_model(User))
        self.assertEqual(act.object_id, user.id)

    def test_set_page_as_content_object(self):
        page = BasePage.add_root()
        act = Activity(message="Create new page.", content_object=page)
        act.save()
        ctype = act.content_type
        self.assertEqual(ctype, ContentType.objects.get_for_model(BasePage))
        self.assertEqual(act.object_id, page.id)