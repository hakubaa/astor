from django.urls import resolve
from django.template.loader import render_to_string
from django.test import TestCase
from django.http import HttpRequest

from astormain.views import home_page


class HomePageTest(TestCase):

    def test_root_url_resolves_to_home_page_view(self):
        found = resolve("/")
        self.assertEqual(found.func, home_page)

    def test_home_page_renders_correct_template(self):
        request = HttpRequest()
        response = home_page(request)
        expected_html = render_to_string("astormain/home.html")
        self.assertEqual(response.content.decode(), expected_html)
