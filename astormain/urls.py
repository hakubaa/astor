from django.conf.urls import url
from django.contrib import admin

from astormain.views import home_page, user_profile
import astormain.views as views

app_name = "astormain"
urlpatterns = [
    url(r'^$', home_page, name="home"),
    url(r'da/(?P<username>\w+)$', user_profile, name="profile"),
    url(r'da/(?P<username>\w+)/pages/(?P<pk>\d+)', 
        views.AnalysisView.as_view(), name="page")
]
