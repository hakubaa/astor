from django.conf.urls import url
from django.conf.urls import include
from rest_framework.urlpatterns import format_suffix_patterns

import astorcore.views as views


urlpatterns = [
    url(r"^$", views.api_root),
    url(r'^tags/$', views.TagList.as_view(), name="tag-list"),
    url(r'^tags/(?P<slug>[-\w]+)$', views.TagDetail.as_view(), 
        name="tag-detail"),

    url(r"^comments/$", views.CommentList.as_view(), name="comment-list"),
    url(r"^comments/(?P<cpk>[-\w]+)$", views.CommentDetail.as_view(), 
        name="comment-detail"),
    url(r"^comments/(?P<cpk>\d+)/replies/$",
        views.CommentReplyList.as_view(), name="comment-reply-list"),
    url(r"^comments/(?P<cpk>\d+)/replies/(?P<rpk>\d+)",
        views.CommentReplyDetail.as_view(), name="comment-reply-detail"),  

    url(r"^analyses/$", views.AnalysisList.as_view(), name="analysis-list"),
    url(r"^analyses/(?P<apk>\d+)$", views.AnalysisDetail.as_view(),
        name="analysis-detail"),
    url(r"^analyses/(?P<apk>\d+)/comments/$", 
        views.AnalysisCommentList.as_view(), name="analysis-comment-list"),
    url(r"^analyses/(?P<apk>\d+)/comments/(?P<cpk>\d+)$",
        views.AnalysisCommentDetail.as_view(), name="analysis-comment-detail"),
    url(r"^analyses/(?P<apk>\d+)/comments/(?P<cpk>\d+)/replies/$",
        views.CommentReplyList.as_view(), name="analysis-comment-reply-list"),
    url(r"^analyses/(?P<apk>\d+)/comments/(?P<cpk>\d+)/replies/(?P<rpk>\d+)",
        views.CommentReplyDetail.as_view(), name="analysis-comment-reply-detail"),
  
]
urlpatterns = format_suffix_patterns(urlpatterns)