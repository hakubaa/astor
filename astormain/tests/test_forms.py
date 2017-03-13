import unittest

from django.core.exceptions import ValidationError
from django.test import TestCase

from astoraccount.models import User
from astorcore.models import ContentPage, Comment
from astormain.forms import CommentForm, ReplyForm


class CommentFormTest(unittest.TestCase):

    def test_constructor_requires_page_and_user(self):
        with self.assertRaises(TypeError):
            form = CommentForm()
        with self.assertRaises(TypeError):
            form = CommentForm(page=None)
        with self.assertRaises(TypeError):
            form = CommentForm(author=None)

    def test_raises_validation_error_when_invalid_author(self):
        form = CommentForm(page=ContentPage(title="Test"), author=None)
        with self.assertRaises(ValidationError):
            form.is_valid()

    def test_raises_validation_error_when_invalid_page(self):
        form = CommentForm(page=None, author=User(username="test"))
        with self.assertRaises(ValidationError):
            form.is_valid()

    def test_raises_validation_error_when_user_not_saved(self):
        user = User(username="test")
        page = ContentPage(title="Page")
        page.id = 5
        page.pk = page.id
        form = CommentForm(page=page,author=user)
        with self.assertRaises(ValidationError):
            form.is_valid()

    def test_raises_validation_error_when_page_not_saved(self):
        user = User(username="teset")
        user.id = 5
        user.pk = 5
        page = ContentPage(title="Page")
        form = CommentForm(page=page,author=user)
        with self.assertRaises(ValidationError):
            form.is_valid()

    def test_saved_user_and_page_make_validation_successfull(self):
        user = User(username="test")
        user.id = 5
        user.pk = user.id
        page = ContentPage(title="Page")
        page.id = 3 
        page.pk = page.id
        form = CommentForm(page=page, author=user)
        self.assertTrue(form.is_valid())


class CommentFormSaveTest(TestCase):

    def test_save_adds_comment_to_page_and_sets_author(self):
        user = User.objects.create_user(username="Test", password="test1234")
        page = user.add_page(ContentPage(title="My First Page"))
        form = CommentForm(page=page, author=user, 
                           data={"body": "My First Comment"})
        self.assertTrue(form.is_valid())
        form.save()
        self.assertEqual(page.comments.count(), 1)
        comment = page.comments.first()
        self.assertEqual(comment.author, user)
        self.assertEqual(comment.body, "My First Comment")


class ReplyFormTest(unittest.TestCase):

    def test_constructor_requires_comment_and_user(self):
        with self.assertRaises(TypeError):
            form = ReplyForm()
        with self.assertRaises(TypeError):
            form = ReplyForm(comment=None)
        with self.assertRaises(TypeError):
            form = ReplyForm(author=None)

    def test_saved_user_and_comment_make_validation_successfull(self):
        user = User(username="test")
        user.id = 5
        user.pk = user.id
        comment = Comment(body="Page")
        comment.id = 3 
        comment.pk = comment.id
        form = ReplyForm(comment=comment, author=user)
        self.assertTrue(form.is_valid())


class ReplyFormSaveTest(TestCase):

    def test_save_adds_reply_to_comment_and_sets_author(self):
        user = User.objects.create_user(username="Test", password="test1234")
        page = user.add_page(ContentPage(title="My First Page"))
        comment = page.add_comment(body="Comment #1", author=user)
        form = ReplyForm(comment=comment, author=user, 
                         data={"body": "Reply #1"})
        self.assertTrue(form.is_valid())
        form.save()
        comment.refresh_from_db()
        self.assertEqual(comment.replies.count(), 1)
        reply = comment.replies.first()
        self.assertEqual(reply.body, "Reply #1")
        self.assertEqual(reply.author, user)
        self.assertIsNone(reply.page)
        self.assertEqual(reply.parent, comment)

