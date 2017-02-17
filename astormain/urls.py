from django.conf.urls import url
from django.contrib import admin

import astormain.views as views

app_name = "astormain"
urlpatterns = [
    url(r'^$', views.HomePageView.as_view(), name="home"),
    url(r'da/(?P<slug>\w+)$', views.UserProfileView.as_view(), name="profile"),
    url(r'da/(?P<slug>\w+)/pages/(?P<pk>\d+)', 
        views.AnalysisView.as_view(), name="page")
]
