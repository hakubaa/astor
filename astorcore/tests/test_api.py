import unittest
import json

from django.test import TestCase, RequestFactory
from django.urls import reverse
from django.http.response import Http404
from django.contrib.auth import get_user_model
from taggit.models import Tag

from astorcore.models import BasePage, Comment
from astorcore.views import (
    AnalysisList, AnalysisDetail, AnalysisCommentDetail,
    CommentReplyDetail
)
from astorcore.serializers import BasePageSerializer


User = get_user_model()


class SetupViewMixin(object):

    @staticmethod
    def setup_view(view, request, *args, **kwargs):
        view.request = request
        view.args = args
        view.kwargs = kwargs
        return view


class TagsTest(TestCase):

    def create_tags(self, tags):
        return [ Tag.objects.create(name=tag) for tag in tags ]

    def test_get_request_returns_list_of_tags(self):
        tags = self.create_tags(["my", "first", "tag"])
        response = self.client.get(reverse("api:tag-list"))
        data = json.loads(response.content.decode())
        self.assertEqual(len(data), 3)
        self.assertCountEqual(
            [ tag["name"] for tag in data ], 
            [ tag.name for tag in tags ]
        )

    def test_for_creating_new_tag_with_post_request(self):
        user = User.objects.create_user(username="test", password="test123")
        self.client.login(username="test", password="test123")
        response = self.client.post(reverse("api:tag-list"),
                                    {"name": "Python", "slug": "python"})
        self.assertEqual(response.status_code, 201)
        tag = Tag.objects.first()
        self.assertEqual(tag.name, "Python")

    def test_get_a_tag_by_using_its_slug(self):
        tags = self.create_tags(["tags", "are", "awesome"])
        response = self.client.get(
            reverse("api:tag-detail", kwargs={"slug": tags[0].slug })
        )
        data = json.loads(response.content.decode())
        self.assertEqual(data["id"], tags[0].id)
        self.assertEqual(data["name"], tags[0].name)

    def test_delete_a_with_delete_request(self):
        user = User.objects.create_user(username="test", password="test123")
        tags = self.create_tags(["tags", "are", "awesome"])
        self.client.login(username="test", password="test123")
        response = self.client.delete(
            reverse("api:tag-detail", kwargs={"slug": tags[0].slug })
        )
        self.assertEqual(response.status_code, 204)
        self.assertEqual(Tag.objects.count(), 2)


class AnalysisDetailTest(SetupViewMixin, TestCase):

    def test_get_object_returns_specific_page(self):
        page = BasePage.objects.create()

        request_factory = RequestFactory()
        request = request_factory.get("/fake_url", data={"apk": page.pk})

        view = AnalysisDetail()
        view = AnalysisDetailTest.setup_view(view, request, apk=page.pk)

        page_view = view.get_object()

        self.assertEqual(page, page_view)

    def test_get_serializer_class_returns_correct_serializer(self):  
        page = BasePage.objects.create()

        request_factory = RequestFactory()
        request = request_factory.get("/fake_url", data={"apk": page.pk})

        view = AnalysisDetail()
        view = AnalysisDetailTest.setup_view(view, request, apk=page.pk)

        serializer = view.get_serializer_class()
        self.assertEqual(serializer, BasePageSerializer)

    def test_get_request_returns_analysis(self):
        page = BasePage.objects.create(title="WTF")

        response = self.client.get(
            reverse("api:analysis-detail", kwargs={"apk": page.pk})
        )

        self.assertEqual(response.status_code, 200)
        data = json.loads(response.content.decode())
        self.assertEqual(data["title"], page.title)


class AnalysisListTest(SetupViewMixin, TestCase):

    def test_returns_list_of_analyses(self):
        page1 = BasePage.objects.create(title="Test Page #1")
        page2 = BasePage.objects.create(title="Test Page #2")

        response = self.client.get(reverse("api:analysis-list")) 

        self.assertEqual(response.status_code, 200)
        data = json.loads(response.content.decode())
        ids = [ page["id"] for page in data ]
        self.assertCountEqual(ids, [ page1.id, page2.id ])


class AnalysisCommentDetailTest(SetupViewMixin, TestCase):

    def test_get_object_returns_correct_comment(self):
        page = BasePage.objects.create(title="Valid Page")
        comment = page.add_comment(body="Valid Comment")
        # create fake page & comment
        BasePage.objects.create(title="Fake Page").add_comment(body="Fake Cmnt")

        request_factory = RequestFactory()
        request = request_factory.get(
            "/fake_url", 
            data=dict(apk=page.pk, cpk=comment.pk)
        )

        view = AnalysisCommentDetailTest.setup_view(
            AnalysisCommentDetail(),
            request, apk=page.pk, cpk=comment.pk
        )
        comment_view = view.get_object()

        self.assertEqual(comment_view, comment)

    def test_get_object_raises_404_when_invalid_apk(self):
        page = BasePage.objects.create(title="Valid Page")
        comment = page.add_comment(body="Valid Comment")  
        fake_page = BasePage.objects.create(title="Fake Page")

        request_factory = RequestFactory()
        request = request_factory.get(
            "/fake_url", 
            data=dict(apk=fake_page.pk, cpk=comment.pk)
        )

        view = AnalysisCommentDetailTest.setup_view(
            AnalysisCommentDetail(),
            request, apk=fake_page.pk, cpk=comment.pk
        )
        with self.assertRaises(Http404):
            comment_view = view.get_object()


    def test_for_returning_comment(self):
        page = BasePage.objects.create(title="Test Page")
        comment = page.add_comment(body="Test Comment")

        response = self.client.get(
            reverse("api:analysis-comment-detail", 
                    kwargs=dict(apk=page.pk, cpk=comment.pk))
        )
        data = json.loads(response.content.decode())

        self.assertEqual(response.status_code, 200)
        self.assertEqual(data["body"], comment.body)

    def test_for_returning_comment_without_analysis_pk(self):
        page = BasePage.objects.create(title="Test Page")
        comment = page.add_comment(body="Test Comment")

        response = self.client.get(
            reverse("api:comment-detail", kwargs=dict(cpk=comment.pk))
        )

        self.assertEqual(response.status_code, 200)
        data = json.loads(response.content.decode())
        self.assertEqual(data["body"], "Test Comment")


class AnalysisCommentListTest(TestCase):

    def test_logged_in_user_adds_comment(self):
        page = BasePage.objects.create(title="Test Page")
        user = User.objects.create_user(username="Test", password="test123")
        self.client.login(username="Test", password="test123")

        response = self.client.post(
            reverse("api:analysis-comment-list", kwargs=dict(apk=page.pk)),
            data = dict(body="Test Comment", author=user.pk)
        )     

        self.assertEqual(response.status_code, 201)
        comment = Comment.objects.first()
        self.assertEqual(comment.body, "Test Comment")
        self.assertEqual(comment.page.pk, page.pk)

    def test_returns_401_when_anonymouse_user_adds_comment(self):
        page = BasePage.objects.create(title="Test Page")

        response = self.client.post(
            reverse("api:analysis-comment-list", kwargs=dict(apk=page.pk)),
            data = dict(body="Test Comment")
        )

        self.assertEqual(response.status_code, 403)

    def test_sets_author_of_the_comment(self):
        page = BasePage.objects.create(title="Test Page")
        user = User.objects.create_user(username="Test", password="test123")
        fake_user = User.objects.create_user(username="Fake", password="fake12")
        self.client.login(username="Test", password="test123")

        response = self.client.post(
            reverse("api:analysis-comment-list", kwargs=dict(apk=page.pk)),
            data = dict(body="Test Comment", author=user.pk)
        )     

        comment = Comment.objects.first()
        self.assertEqual(comment.author, user)

    def test_returns_comments_for_selected_analysis(self):
        page = BasePage.objects.create(title="Test Page")
        fake_page = BasePage.objects.create(title = "Fakse Page")
        page.add_comment(body="Test Comment #0").reply(body="Test Reply #0#0")
        fake_page.add_comment(body="Test Comment #1")
        page.add_comment(body="Test Comment #2")

        response = self.client.get(
            reverse("api:analysis-comment-list", kwargs=dict(apk=page.pk))
        )

        self.assertEqual(response.status_code, 200)
        data = json.loads(response.content.decode())
        self.assertEqual(len(data), 2)


class CommentReplyDetailTest(SetupViewMixin, TestCase):

    def test_get_object_returns_correct_comment(self):
        page = BasePage.objects.create(title="Valid Page")
        comment = page.add_comment(body="Valid Comment")
        reply = comment.reply(body="Valid Reply")
        # create fake page & comment & reply
        BasePage.objects.create(title="Fake Page").\
            add_comment(body="Fake Cmnt").reply(body="Fake Reply")

        request_factory = RequestFactory()
        request = request_factory.get(
            "/fake_url", 
            data=dict(apk=page.pk, cpk=comment.pk, rpk=reply.pk)
        )

        view = self.setup_view(
            CommentReplyDetail(),
            request, apk=page.pk, cpk=comment.pk, rpk=reply.pk
        )
        reply_view = view.get_object()

        self.assertEqual(reply_view, reply)

    def test_get_object_raises_404_when_invalid_cpk(self):
        page = BasePage.objects.create(title="Valid Page")
        comment = page.add_comment(body="Valid Comment")
        reply = comment.reply(body="Valid Reply")

        fake_comment = BasePage.objects.create(title="Fake Page").\
                           add_comment(body="Fake Comment")

        request_factory = RequestFactory()
        request = request_factory.get(
            "/fake_url", 
            data=dict(apk=page.pk, cpk=fake_comment.pk, rpk=reply.pk)
        )

        view = self.setup_view(
            CommentReplyDetail(),
            request, apk=page.pk, cpk=fake_comment.pk, rpk=reply.pk
        )
        with self.assertRaises(Http404):
            reply_view = view.get_object()

    def test_for_returning_reply(self):
        page = BasePage.objects.create(title="Valid Page")
        page.add_comment(body="Fake Comment")
        comment = page.add_comment(body="Valid Comment")
        reply = comment.reply(body="Valid Reply")

        response = self.client.get(
            reverse("api:analysis-comment-reply-detail", 
                    kwargs=dict(apk=page.pk, cpk=comment.pk, rpk=reply.pk))
        )
        data = json.loads(response.content.decode())

        self.assertEqual(response.status_code, 200)
        self.assertEqual(data["body"], reply.body)
        self.assertEqual(data["parent"], comment.pk)


class CommentReplyListTest(TestCase):

    def test_logged_in_user_adds_reply(self):
        page = BasePage.objects.create(title="Test Page")
        comment = page.add_comment(body="Test Comment")
        user = User.objects.create_user(username="Test", password="test123")
        self.client.login(username="Test", password="test123")

        response = self.client.post(
            reverse("api:analysis-comment-reply-list", 
                    kwargs=dict(apk=page.pk, cpk=comment.pk)),
            data = dict(body="Test Reply")
        )     

        self.assertEqual(response.status_code, 201)
        reply = Comment.objects.filter(parent__id=comment.pk)[0]
        self.assertEqual(reply.body, "Test Reply")
        self.assertEqual(reply.parent.pk, comment.pk)

    def test_returns_401_when_anonymouse_user_adds_reply(self):
        page = BasePage.objects.create(title="Test Page")
        comment = page.add_comment(body="Test Comment")

        response = self.client.post(
            reverse("api:analysis-comment-reply-list", 
                    kwargs=dict(apk=page.pk, cpk=comment.pk)),
            data = dict(body="Test Reply")
        )  

        self.assertEqual(response.status_code, 403)

    def test_sets_author_of_the_reply(self):
        page = BasePage.objects.create(title="Test Page")
        comment = page.add_comment(body="Test Comment")
        user = User.objects.create_user(username="Test", password="test123")
        fake_user = User.objects.create_user(username="Fake", password="fake12")
        self.client.login(username="Test", password="test123")

        response = self.client.post(
            reverse("api:analysis-comment-reply-list", 
                    kwargs=dict(apk=page.pk, cpk=comment.pk)),
            data = dict(body="Test Reply")
        )    

        reply = Comment.objects.filter(parent__id=comment.pk)[0]
        self.assertEqual(reply.author, user)

    def test_returns_replies_for_selected_comment(self):
        page = BasePage.objects.create(title="Test Page")
        page.add_comment(body="Test Comment #0").reply(body="Test Reply #0#0")
        page.add_comment(body="Test Comment #1")
        comment = page.add_comment(body="Test Comment #2")
        comment.reply(body="Test Reply #2#0")
        comment.reply(body="Test Reply #2#1")

        response = self.client.get(
            reverse("api:analysis-comment-reply-list",
                    kwargs=dict(apk=page.pk, cpk=comment.pk))
        )

        self.assertEqual(response.status_code, 200)
        data = json.loads(response.content.decode())
        self.assertEqual(len(data), 2)