from django.shortcuts import render, redirect
from django.urls import reverse
from django.contrib.contenttypes.models import ContentType
from django.http import HttpResponse
from django.contrib.auth.decorators import login_required
from django.contrib.auth import get_user_model
from django.contrib import messages
from django.utils.translation import ugettext as _
from django.core.paginator import Paginator
from django.views.generic import TemplateView, View
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic.list import ListView
from django.core.files.storage import FileSystemStorage
from django.conf import settings

from taggit.utils import edit_string_for_tags

from astorcore.models import Page
from astorcore.decorators import get_page_models, get_forms
from astoraccount.models import Activity
from astoraccount.forms import ContentPageForm


class AccountIndexView(LoginRequiredMixin, TemplateView):
    template_name = "astoraccount/index.html"

    def get_context_data(self, *args, **kwargs):
        context = super(AccountIndexView, self).get_context_data(*args, **kwargs)
        # Find recent edits, but do not show published pages.
        recent_edits = [page.specific for page in self.request.user.pages.all()]
        context["recent_edits"] = recent_edits
        return context


class AnalysesView(LoginRequiredMixin, TemplateView):
    template_name = "astoraccount/analyses.html"

    def get_context_data(self, *args, **kwargs):
        page = self.request.GET.get("page", 1)

        paginator = Paginator(self.request.user.pages.filter(editable=True), 10)
        try:
            analyses = paginator.page(page)
        except PageNotAnInteger:
            analyses = paginator.page(1)
        except EmptyPage:
            analyses = paginator.page(paginator.num_pages)

        # Get the most specific type of page.
        analyses.object_list = [analysis.specific for analysis in analyses]

        context = super(AnalysesView, self).get_context_data(*args, **kwargs)
        context["analyses"] = analyses

        return context


class NewPageView(LoginRequiredMixin, TemplateView):
    template_name = "astoraccount/page_new.html"

    def get_context_data(self, *args, **kwargs):
        context = super(NewPageView, self).get_context_data(*args, **kwargs)

        pages = list()
        for page in get_page_models():
            content_type = ContentType.objects.get_for_model(page)    
            pages.append({
                "title": page.verbose_name.title(), 
                "type": content_type.app_label + ":" + content_type.model,
                "help_text": page.help_text
            })
        context["pages"] = pages

        return context


class CreatePageView(LoginRequiredMixin, View):

    def get(self, request):
        user = self.request.user
        if user.is_authenticated:
            app_label, model = self.request.GET["type"].split(":")
            ctype = ContentType.objects.get(app_label=app_label, model=model)
            cls = ctype.model_class()
            page = user.add_page(instance=cls())
            
            user.add_activity(
                number=Activity.NEW_PAGE, content_object=page,
                message="Page created: \"%s\" id=%d type=%s" % (page.specific.title, 
                    page.id, page.specific.verbose_name.title())
            )

        return redirect(reverse("astoraccount:page_edit", kwargs={"pk": page.pk}))    


@login_required
def page_edit(request, pk):
    try:
        page = Page.objects.get(pk=pk)
    except Page.DoesNotExist:
        return redirect(reverse("astoraccount:404"))

    # Find the proper form for the page.
    form_cls = None
    for form in get_forms():
        if type(page.specific) == form._meta.model:
            form_cls = form
            break

    form = None
    form_data = dict(
        instance=page.specific,
        initial={
            "tags": edit_string_for_tags(page.specific.tags.all()).replace('"', '')
        }
    )

    if request.method == "POST":
        form = form_cls(request.POST, request.FILES, **form_data)
        if form.is_valid():
            page = form.save()

            request.user.add_activity(
                number=Activity.UPDATE_PAGE, content_object=page,
                message="Analysis updated: \"%s\" id=%d type=%s" % (
                    page.specific.title, page.id, 
                    page.specific.verbose_name.title()
                )
            )

            action = request.POST.get("action_type", "save_draft")
            if action == "save_draft":
                messages.success(
                    request, _("The draft has been saved."), fail_silently=True
                )
            else:
                pub_page = page.publish()
                messages.success(
                    request, _("The analysis has been saved and published."), 
                    fail_silently=True
                )

                request.user.add_activity(
                number=Activity.UPDATE_PAGE, content_object=page,
                message="Analysis published: \"%s\" id=%d type=%s" % (
                    page.specific.title, page.id, 
                    page.specific.verbose_name.title()
                )
            )

    else:
        if form_cls:
            form = form_cls(**form_data)

    return render(request, "astoraccount/page_edit.html", {"form": form})