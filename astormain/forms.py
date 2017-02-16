from django import forms
from django.core.exceptions import ValidationError
from django.utils.translation import ugettext as _

from astorcore.models import Comment


class CommentForm(forms.ModelForm):
    class Meta:
        model = Comment
        fields = ["body"]
        widgets = {
            "body": forms.TextInput(
                attrs={"placeholder": "Enter your comment."}
            ),
        }

    def __init__(self, page, user, *args, **kwargs):
        super(CommentForm, self).__init__(*args, **kwargs)
        self.user = user
        self.page = page

    def is_valid(self):
        super(CommentForm, self).is_valid()
        if not self.user or not self.user.pk:
            raise ValidationError(_("Invalid user."), code="invalid")
        if not self.page or not self.page.pk:
            raise ValidationError(_("Invalid page."), code="invalid")
        return True

    def save(self, commit=True):
        instance = super(CommentForm, self).save(commit=False)
        instance.author = self.user
        instance.save()
        self.page.add_comment(comment=instance)
        return instance