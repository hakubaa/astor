from django.conf.urls import url
from django.urls import reverse

from astoraccount.views import index_page, page_new, page_create, page_edit
from django.contrib.auth import views as auth_views

app_name = "astoraccount"
urlpatterns = [
    url(r'^$', index_page, name="index"),
    url(r'^pages/new$', page_new, name="page_new"),
    url(r'^pages/create$', page_create, name="page_create"),
    url(r'^pages/(?P<page_id>\d+)', page_edit, name="page_edit"),
    url(r'^login/$', auth_views.login, 
        {"template_name": "astoraccount/login.html"}, name="login"),
    url(r'^logout/$', auth_views.logout, 
        {"next_page": "/"}, name="logout"),
]
