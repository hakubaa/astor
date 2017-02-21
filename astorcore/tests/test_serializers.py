import unittest

from django.contrib.auth import get_user_model

from astorcore.serializers import CommentSerializer
from astorcore.models import Comment, BasePage


User = get_user_model()


class CommentSerializerTest(unittest.TestCase):

    def test_is_valid_is_false_when_no_page(self):
        page = BasePage.objects.create(title="Page Test")
        cs = CommentSerializer(
                data={"body": "Comment Test"}
        )
        self.assertFalse(cs.is_valid())
        self.assertIn("page", cs.errors)

    def test_for_saving_comment_with_page_and_author(self):
        page = BasePage.objects.create(title="Page Test")
        user = User.objects.create_user(username="Test", password="test123")
        cs = CommentSerializer(
                data={"body": "Comment Test", "page": page.pk, "author": user.pk}
        )
        self.assertTrue(cs.is_valid())
        cs.save()
        comment = Comment.objects.first()
        self.assertEqual(comment.page, page)
        self.assertEqual(comment.author, user)
