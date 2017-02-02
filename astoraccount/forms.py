from django.forms import ModelForm
from django.forms.widgets import TextInput

from astorcore.models import IndexPage, ContentPage
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
        fields = IndexPageForm.Meta.fields + ["body"]
        widgets = {
            "title": TextInput(attrs={"placeholder": "Enter a title."}),
        }