from django.conf.urls import url

from astoraccount.views import index_page

app_name = "astoraccount"
urlpatterns = [
    url(r'^$', index_page, name="index"),
]
