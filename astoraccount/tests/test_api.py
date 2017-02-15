import json

from django.test import TestCase
from django.contrib.auth import get_user_model
from django.urls import reverse


User = get_user_model()


class UserListTest(TestCase):

    def test_get_request_returns_list_of_user(self):
        kate = User.objects.create_user(username="kate", password="kate123")
        mike = User.objects.create_user(username="mike", password="mike123")
        response = self.client.get(reverse("api:user_list"))
        data = json.loads(response.content)
        self.assertTrue(len(data), 2)
        user_names = [ user["username"] for user in data ]
        self.assertCountEqual(user_names, [kate.username, mike.username])