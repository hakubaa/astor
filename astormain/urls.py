from django.conf.urls import url
from django.contrib import admin

from astormain.views import home_page

app_name = "astormain"
urlpatterns = [
    url(r'^$', home_page, name="home"),
]
