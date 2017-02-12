from django.conf.urls import url
from django.urls import reverse
from django.contrib.auth import views as auth_views
from django.views.generic import TemplateView

# from astoraccount.views import (
#     #page_create#, page_edit
# )
import astoraccount.views as views


app_name = "astoraccount"
urlpatterns = [
    url(r'^test/$', TemplateView.as_view(template_name="astoraccount/test.html"),
        name="test"),
    url(r'^$', views.AccountIndexView.as_view(), name="index"),
    url(r'^404/$', TemplateView.as_view(template_name="astoraccount/404.html"), 
        name="404"),
    url(r'^analyses/$', views.AnalysesView.as_view(), name="analyses"),
    url(r'^analyses/new/$', views.NewPageView.as_view(), name="page_new"),
    url(r'^analyses/create/$', views.CreatePageView.as_view(), 
        name="page_create"),
    url(r'^analyses/(?P<pk>\d+)/', views.page_edit, name="page_edit"),
    url(r'^login/$', auth_views.login, 
        {"template_name": "astoraccount/login.html"}, name="login"),
    url(r'^logout/$', auth_views.logout, 
        {"next_page": "/"}, name="logout"),
]
