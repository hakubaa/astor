import unittest
import sys
import time

from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.common.exceptions import WebDriverException

from django.contrib.staticfiles.testing import StaticLiveServerTestCase
from django.contrib.auth import BACKEND_SESSION_KEY, SESSION_KEY, get_user_model
from django.contrib.sessions.backends.db import SessionStore
from django.urls import reverse
from django.conf import settings


User = get_user_model()


class FunctionalTest(StaticLiveServerTestCase):

    def setUp(self):
        self.browser = webdriver.Firefox()
        self.browser.implicitly_wait(3)

    def tearDown(self):
        self.browser.quit()

    def create_user(self, username="Test", password="test"):
        user = User.objects.create_user(username=username, password=password)
        return user

    def wait_for(self, function_with_assertion, timeout = 10):
        start_time = time.time()
        while time.time() - start_time < timeout:
            try:
                return function_with_assertion()
            except (AssertionError, WebDriverException):
                time.sleep(0.1)
        # one more try, which will raise any errors if they are outstanding
        return function_with_assertion()

    def wait_for_element_with_id(self, element_id, timeout=10):
        WebDriverWait(self.browser, timeout = timeout).until(
            lambda b: b.find_element_by_id(element_id),
            'Could not find element with id {}. Page text was:\n{}'.format(
                element_id, self.browser.find_element_by_tag_name('body').text
            )
        )

    def wait_for_page_with_text_in_url(self, text, timeout=10):
        WebDriverWait(self.browser, timeout=timeout).until(
            lambda b: text.lower() in b.current_url.lower(),
            "Could not load page with '%s' in url." % text
        )

    def wait_for_page_which_url_ends_with(self, text, timeout=10):
        WebDriverWait(self.browser, timeout=timeout).until(
            lambda b: b.current_url.lower().endswith(text.lower()),
            "Could not load page withc url ends wiht '%s'." % text
        )      

    def login_user(self, username, password, test_for_login=True):
        self.browser.get(self.live_server_url + "/account/login")
        self.browser.implicitly_wait(3)

        input_username = self.browser.find_element_by_id("id_username")
        input_password = self.browser.find_element_by_id("id_password")

        input_username.send_keys(username)
        input_password.send_keys(password)

        self.browser.find_element_by_xpath(
            "//input[@type='submit' and @value='Submit']"
        ).click()

        WebDriverWait(self.browser, timeout = 10).until(
            lambda b: b.find_element_by_link_text("Log Out"),
            "Could not find 'Log Out' link"
        )

        if test_for_login:
            self.assertEqual(
                self.browser.current_url, 
                self.live_server_url + "/account/"
            )
