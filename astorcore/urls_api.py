from django.conf.urls import url
from rest_framework.urlpatterns import format_suffix_patterns

import astorcore.views as views


urlpatterns = [
    url(r'^tags/$', views.TagList.as_view(), name="tag_list"),
    url(r'^tags/(?P<slug>[-\w]+)$', views.TagDetail.as_view(), 
        name="tag_detail"),
]
urlpatterns = format_suffix_patterns(urlpatterns)