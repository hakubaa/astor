from django.conf.urls import url
from django.contrib import admin
from django.views.generic import TemplateView


import astormain.views as views

app_name = "astormain"
urlpatterns = [
    url(r'^$', views.HomePageView.as_view(), name="home"),
    url(r'da/(?P<slug>\w+)$', views.UserProfileView.as_view(), name="profile"),
    url(r'da/(?P<slug>\w+)/pages/(?P<pk>\d+)$', 
        views.AnalysisView.as_view(), name="page"),
    url(r'da/(?P<slug>\w+)/pages/(?P<pk>\d+)/file$', 
        views.ExternalFileView.as_view(), name="external_file") 
]
