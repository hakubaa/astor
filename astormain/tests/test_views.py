import unittest

from django.test import TestCase
from django.urls import resolve, reverse
from django.contrib.auth import get_user_model

from astormain.views import home_page


User = get_user_model()


class HomePageTest(TestCase):

    def test_account_root_url_resolves_to_index_view(self):
        found = resolve("/")
        self.assertEqual(found.func, home_page)

    def test_uses_correct_template(self):
        response = self.client.get("/")
        self.assertTemplateUsed(response, "astormain/home.html")

    def test_sets_proper_link_to_my_astor_for_logged_in_users(self):
        user = User.objects.create_user("spider", "spider@jago.com", 
                                        "spiderpass")
        self.client.login(username="spider", password="spiderpass")
        response = self.client.get("/")
        self.assertContains(response, "/account/")

    def test_sets_link_to_login_in_my_astor_if_anonymouse_user(self):
        response = self.client.get("/")
        self.assertContains(response, "/login")