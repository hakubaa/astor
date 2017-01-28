from django.conf.urls import url

from astoraccount.views import index_page, page_new, page_create
#, page_edit

app_name = "astoraccount"
urlpatterns = [
    url(r'^$', index_page, name="index"),
    url(r'pages/new$', page_new, name="page_new"),
    url(r'pages/create$', page_create, name="page_create"),
    #url(r'pages/(\d+)', page_edit, name="page_edit"),
]
