import operator
from functools import reduce
from copy import copy

from django.db.models import Q
from django.shortcuts import get_object_or_404
from taggit.models import Tag
from rest_framework.exceptions import NotFound
from rest_framework.views import APIView
from rest_framework.reverse import reverse
from rest_framework import status, generics, permissions
from rest_framework.response import Response
from rest_framework.decorators import api_view

from astorcore.serializers import (
    TagSerializer, PageSerializer, CommentSerializer
)
from astorcore.models import Page, Comment
from astorcore.decorators import get_serializers


class MappingFieldsLookupMixin(object):

    def get_object(self):
        queryset = self.get_queryset()
        queryset = self.filter_queryset(queryset)
        filter = {}
        for field in self.lookup_fields:
            filter[self.lookup_mapping.get(field, field)] = self.kwargs[field]
        q = reduce(operator.and_, (Q(x) for x in filter.items()))
        return get_object_or_404(queryset, q)    



@api_view(["GET"])
def api_root(request, format=None):
    return Response({
        "tags": reverse("api:tag-list", request=request, format=format),
        "analyses": reverse("api:analysis-list", request=request, 
                            format=format),
        "comments": reverse("api:comment-list", request=request, format=format)
    })


class TagList(generics.ListCreateAPIView):
    queryset = Tag.objects.all()
    serializer_class = TagSerializer
    permission_classes = (permissions.IsAuthenticatedOrReadOnly,)


class TagDetail(generics.RetrieveUpdateDestroyAPIView):
    queryset = Tag.objects.all()
    serializer_class = TagSerializer
    lookup_field = "slug"
    permission_classes = (permissions.IsAuthenticatedOrReadOnly,)


class AnalysisList(generics.ListAPIView):
    queryset = Page.objects.all()
    serializer_class = PageSerializer
    lookup_url_kwarg = "apk"


class AnalysisDetail(generics.RetrieveUpdateDestroyAPIView):
    queryset = Page.objects.all()
    lookup_field = "pk"
    lookup_url_kwarg = "apk"
    permission_classes = (permissions.IsAuthenticatedOrReadOnly,)

    def get_object(self):
        obj = super(AnalysisDetail, self).get_object()
        return obj.specific 

    def get_serializer_class(self):
        obj = self.get_object()
        serializers = get_serializers()

        serializer_class = None
        for serializer in get_serializers():
            if type(obj) == serializer.Meta.model:
                serializer_class = serializer
                break

        assert serializer_class is not None, (
            "No serializer registered for '%s'." % obj.__class__.__name__
        )

        return serializer_class


class CommentList(generics.ListCreateAPIView):
    queryset = Comment.objects.all()
    serializer_class = CommentSerializer
    permission_classes = (permissions.IsAuthenticatedOrReadOnly,)


class CommentDetail(generics.RetrieveUpdateDestroyAPIView):
    queryset = Comment.objects.all()
    serializer_class = CommentSerializer
    permission_classes = (permissions.IsAuthenticatedOrReadOnly,)

    lookup_field = "pk"
    lookup_url_kwarg = "cpk"


class AnalysisCommentList(generics.ListCreateAPIView):
    queryset = Page.objects.all()
    serializer_class = CommentSerializer
    permission_classes = (permissions.IsAuthenticatedOrReadOnly,)

    lookup_field = "pk"
    lookup_url_kwarg = "apk"

    def get_object(self, format=None):
        obj = super(AnalysisCommentList, self).get_object()
        return obj.specific 

    def get(self, request, format=None, **kwargs):
        analysis = self.get_object()
        comments = analysis.comments.all()
        serializer = CommentSerializer(
            comments, many=True, context={"request": request}
        )
        return Response(serializer.data)       

    def post(self, request, format=None, **kwargs):
        analysis = self.get_object()
        data = copy(request.data)
        data["page"] = analysis.pk # required by serializer
        serializer = CommentSerializer(data=data)
        if serializer.is_valid():
            serializer.save(author=request.user)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)     


class AnalysisCommentDetail(MappingFieldsLookupMixin, 
                            generics.RetrieveUpdateAPIView):
    queryset = Comment.objects.all()
    serializer_class = CommentSerializer
    permission_classes = (permissions.IsAuthenticatedOrReadOnly,)

    lookup_fields = ("apk", "cpk")
    lookup_mapping = {"apk": "page__pk", "cpk": "pk"}


class CommentReplyList(#MappingFieldsLookupMixin,
                       generics.ListCreateAPIView):
    queryset = Comment.objects.all()
    serializer_class = CommentSerializer
    permission_classes = (permissions.IsAuthenticatedOrReadOnly,)

    lookup_field = "pk"
    lookup_url_kwarg = "cpk"

    def get(self, request, format=None, **kwargs):
        comment = self.get_object()
        replies = comment.replies.all()
        serializer = CommentSerializer(
            replies, many=True, context={"request": request}
        )
        return Response(serializer.data)     

    def post(self, request, format=None, **kwargs):
        comment = self.get_object()
        data = copy(request.data)
        data["parent"] = comment.pk # required by serializer
        serializer = CommentSerializer(data=data)
        if serializer.is_valid():
            serializer.save(author=request.user)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)  


class CommentReplyDetail(MappingFieldsLookupMixin, 
                         generics.RetrieveUpdateAPIView):
    queryset = Comment.objects.all()
    serializer_class = CommentSerializer
    permission_classes = (permissions.IsAuthenticatedOrReadOnly,)

    lookup_fields = ("cpk", "rpk")
    lookup_mapping = {"rpk": "pk", "cpk": "parent__pk"}