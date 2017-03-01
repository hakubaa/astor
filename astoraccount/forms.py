from django.forms import ModelForm
from django.forms.widgets import TextInput

from ckeditor.widgets import CKEditorWidget

from astorcore.models import (
    IndexPage, ContentPage, HTMLUploadPage
)
from astorcore.decorators import register_form


@register_form
class IndexPageForm(ModelForm):
    class Meta:
        model = IndexPage
        fields = ["title", "abstract"]
        widgets = {
            "title": TextInput(attrs={"placeholder": "Enter a title."}),
        }

@register_form
class ContentPageForm(IndexPageForm):
    class Meta:
        model = ContentPage
        fields = IndexPageForm.Meta.fields + ["body", "tags"]
        widgets = {
            "title": TextInput(attrs={"placeholder": "Enter a title."}),
            "body": CKEditorWidget(),
            "tags": TextInput(attrs={"data-role": "tagsinput" }),
        }


    def clean_tags(self):
        data = self.cleaned_data["tags"]
        data = list(set(tag.lower() for tag in data))
        return data


@register_form
class HTMLUploadPageForm(ModelForm):
    class Meta:
        model = HTMLUploadPage
        fields = ["title", "abstract", "file"]