from django import forms
from django.core.exceptions import ValidationError
from django.utils.translation import ugettext as _

from astorcore.models import Comment


class CommentForm(forms.ModelForm):
    class Meta:
        model = Comment
        fields = ["body"]
        widgets = {
            "body": forms.Textarea(
                attrs={
                    "placeholder": "Enter your comment.",
                    "class": "form-control",
                    "cols": 10, "rows": 3
                }
            ),
        }

    def __init__(self, page, author, *args, **kwargs):
        super(CommentForm, self).__init__(*args, **kwargs)
        self.author = author
        self.page = page

    def is_valid(self):
        super(CommentForm, self).is_valid()
        if not self.author or not self.author.pk:
            raise ValidationError(_("Invalid author."), code="invalid")
        if not self.page or not self.page.pk:
            raise ValidationError(_("Invalid page."), code="invalid")
        return True

    def save(self, commit=True):
        instance = super(CommentForm, self).save(commit=False)
        instance.author = self.author
        instance.save()
        self.page.add_comment(comment=instance)
        return instance


class ReplyForm(forms.ModelForm):
    class Meta:
        model = Comment
        fields = ["body"]
        widgets = {
            "body": forms.Textarea(
                attrs={
                    "placeholder": "Enter your reply.",
                    "class": "form-control",
                    "cols": 10, "rows": 3
                }
            )
        }

    def __init__(self, comment, author, *args, **kwargs):
        super(ReplyForm, self).__init__(*args, **kwargs)
        self.author = author
        self.comment = comment

    def is_valid(self):
        super(ReplyForm, self).is_valid()
        if not self.author or not self.author.pk:
            raise ValidationError(_("Invalid author."), code="invalid")
        if not self.comment or not self.comment.pk:
            raise ValidationError(_("Invalid comment."), code="invalid")
        return True

    def save(self, commit=True):
        instance = super(ReplyForm, self).save(commit=False)
        instance.author = self.author
        instance.save()
        self.comment.reply(comment=instance)
        return instance