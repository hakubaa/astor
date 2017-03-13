from django.forms import ModelForm
from django.forms.widgets import TextInput

from ckeditor.widgets import CKEditorWidget

from astorcore.models import (
    ContentPage, HTMLUploadPage
)
from astorcore.decorators import register_form


@register_form
class ContentPageForm(ModelForm):
    class Meta:
        model = ContentPage
        fields =[ "title", "abstract", "img_url", "body", "tags", "img_url"]
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
        fields = ["title", "abstract", "img_url", "file"]