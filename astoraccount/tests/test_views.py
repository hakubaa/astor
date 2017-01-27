from django.test import TestCase
from django.urls import resolve

from astoraccount.views import index_page


class AccountIndexPageTest(TestCase):

    def test_account_root_url_resolves_to_index_view(self):
        found = resolve("/account/")
        self.assertEqual(found.func, index_page)

    def test_uses_correct_template(self):
        response = self.client.get("/account/")
        self.assertTemplateUsed(response, "astoraccount/index.html")