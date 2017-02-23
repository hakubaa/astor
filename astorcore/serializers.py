from django.contrib.contenttypes.models import ContentType
from taggit.models import Tag
from rest_framework import serializers
from rest_framework.reverse import reverse

from astorcore.models import Page, BasePage, ContentPage, IndexPage, Comment
from astorcore.decorators import register_serializer


class AnalysisCommentListHyperlink(serializers.HyperlinkedRelatedField):
    view_name = "api:analysis-comment-list"

    def __init__(self, *args, **kwargs):
        kwargs["read_only"] = True
        super(AnalysisCommentListHyperlink, self).__init__(*args, **kwargs)

    def get_url(self, obj, view_name, request, format):
        url_kwargs = {
            self.lookup_url_kwarg: request.resolver_match.kwargs.get(
                                       self.lookup_url_kwarg
                                   )
        }
        return reverse(view_name, kwargs=url_kwargs, request=request, 
                       format=format)


class ContentTypeSerializer(serializers.ModelSerializer):
    class Meta:
        model = ContentType
        fields = ["id", "model"]


class TagSerializer(serializers.HyperlinkedModelSerializer):
    url = serializers.HyperlinkedIdentityField(
        view_name="api:tag-detail", lookup_field="slug"
    )

    class Meta:
        model = Tag
        fields = ["id", "url", "name", "slug"]


class PageSerializer(serializers.HyperlinkedModelSerializer):
    url = serializers.HyperlinkedIdentityField(
        view_name="api:analysis-detail", lookup_field="pk",
        lookup_url_kwarg="apk"
    )
    content_type = ContentTypeSerializer()

    class Meta:
        model = Page
        fields = ["id", "url", "content_type"]


@register_serializer
class BasePageSerializer(serializers.HyperlinkedModelSerializer):
    # comments = AnalysisCommentListHyperlink(
    #     lookup_field="pk", lookup_url_kwarg="apk"
    # )

    comments = serializers.PrimaryKeyRelatedField(
        many=True, read_only=True, required=False
    )
    
    class Meta:
        model = BasePage
        fields = ["id", "title", "comments"]


@register_serializer
class ContentPageSerializer(BasePageSerializer):
    class Meta:
        model = ContentPage
        fields = BasePageSerializer.Meta.fields + ["abstract", "body"]


@register_serializer
class IndexPageSerializer(BasePageSerializer):
    class Meta:
        model = IndexPage
        fields = BasePageSerializer.Meta.fields + ["abstract"]


class CommentSerializer(serializers.ModelSerializer):
    replies = serializers.PrimaryKeyRelatedField(
        many=True, read_only=True, required=False
    )
    author = serializers.ReadOnlyField(source="author.username")

    class Meta:
        model = Comment
        fields = ["id", "page", "author", "parent", "body", 
                  "timestamp", "replies"]

    def validate(self, data):
        if "page" not in data and "parent" not in data:
            raise serializers.ValidationError(
                {"page": ["this field (or parent) is required"]}
            )
        return data