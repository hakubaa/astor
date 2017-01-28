import unittest
import sys
import time

from selenium import webdriver
from selenium.webdriver.common.keys import Keys

from django.test import LiveServerTestCase
from django.contrib.auth import BACKEND_SESSION_KEY, SESSION_KEY, get_user_model
from django.contrib.sessions.backends.db import SessionStore
from django.conf import settings


User = get_user_model()


class FunctionalTest(LiveServerTestCase):

    def setUp(self):
        self.browser = webdriver.Firefox()
        self.browser.implicitly_wait(3)

    def tearDown(self):
        self.browser.quit()

    def create_pre_authenticated_session(self, username, password):
        user = User.objects.create(username = username, password = password)
        session = SessionStore()
        session[SESSION_KEY] = user.pk 
        session[BACKEND_SESSION_KEY] = settings.AUTHENTICATION_BACKENDS[0]
        session.save()
        ## to set a cookie we need to first visit the domain.
        ## 404 pages load the quickest!
        self.browser.get(self.live_server_url + "/404_no_such_url/")
        self.browser.add_cookie(dict(
            name=settings.SESSION_COOKIE_NAME,
            value=session.session_key,
            path='/',
        ))
