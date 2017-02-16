import unittest

from django.core.exceptions import ValidationError
from django.test import TestCase

from astoraccount.models import User
from astorcore.models import BasePage
from astormain.forms import CommentForm


class CommentFormTest(unittest.TestCase):

    def test_constructor_requires_page_and_user(self):
        with self.assertRaises(TypeError):
            form = CommentForm()
        with self.assertRaises(TypeError):
            form = CommentForm(page=None)
        with self.assertRaises(TypeError):
            form = CommentForm(user=None)

    def test_raises_validation_error_when_invalid_user(self):
        form = CommentForm(page=BasePage(title="Test"), user=None)
        with self.assertRaises(ValidationError):
            form.is_valid()

    def test_raises_validation_error_when_invalid_page(self):
        form = CommentForm(page=None, user=User(username="test"))
        with self.assertRaises(ValidationError):
            form.is_valid()

    def test_raises_validation_error_when_user_not_saved(self):
        user = User(username="test")
        page = BasePage(title="Page")
        page.id = 5
        page.pk = page.id
        form = CommentForm(page=page,user=user)
        with self.assertRaises(ValidationError):
            form.is_valid()

    def test_raises_validation_error_when_page_not_saved(self):
        user = User(username="teset")
        user.id = 5
        user.pk = 5
        page = BasePage(title="Page")
        form = CommentForm(page=page,user=user)
        with self.assertRaises(ValidationError):
            form.is_valid()

    def test_saved_user_and_page_make_validation_successfull(self):
        user = User(username="test")
        user.id = 5
        user.pk = user.id
        page = BasePage(title="Page")
        page.id = 3 
        page.pk = page.id
        form = CommentForm(page=page, user=user)
        self.assertTrue(form.is_valid())


class CommentFormSaveTest(TestCase):

    def test_save_adds_comment_to_page_and_sets_author(self):
        user = User.objects.create_user(username="Test", password="test1234")
        page = user.add_page(BasePage(title="My First Page"))
        form = CommentForm(page=page, user=user, 
                           data={"body": "My First Comment"})
        self.assertTrue(form.is_valid())
        form.save()
        self.assertEqual(page.comments.count(), 1)
        comment = page.comments.first()
        self.assertEqual(comment.author, user)
        self.assertEqual(comment.body, "My First Comment")