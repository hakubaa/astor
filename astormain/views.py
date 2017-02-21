from django.shortcuts import render, get_object_or_404
from django.http import Http404
from django.contrib.auth import get_user_model

from django.views.generic import TemplateView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic.detail import SingleObjectMixin
from django.views.generic.edit import FormView

from astorcore.models import Page
from astormain.forms import CommentForm, ReplyForm


User = get_user_model()


class HomePageView(TemplateView):
    template_name = "astormain/home.html"

    def get_context_data(self, **kwargs):
        context = super(HomePageView, self).get_context_data(**kwargs)
        newest_entries = [ page.specific for page in Page.objects.all() 
                                         if page.specific.live ]
        context["newest_entries"] = newest_entries
        return context


class AnalysisView(SingleObjectMixin, FormView):
    model = Page
    form_class = CommentForm

    def get_object(self):
        try:
            user = User.objects.filter(slug=self.kwargs["slug"]).first()
        except User.DoesNotExist:
            raise Http404("User does not exist.")

        try:
            page = user.pages.get(pk=self.kwargs["pk"]).specific
        except Page.DoesNotExist:
            raise Http404("Analysis does not exist.")

        return page

    def get_template_names(self):
        return [self.get_object().template_name]

    def get_context_data(self, **kwargs):
        self.object = self.get_object()
        context = super(AnalysisView, self).get_context_data(**kwargs)
        context["page"] = self.object
        return context

    def get_form_kwargs(self):
        kwargs = super(AnalysisView, self).get_form_kwargs()
        kwargs.update({
            "page": self.get_object(),
            "author": self.request.user
        })
        return kwargs

    def get_success_url(self):
        return self.get_object().get_absolute_url()

    def form_valid(self, form):
        form.save()
        return super(AnalysisView, self).form_valid(form)


class UserProfileView(SingleObjectMixin, TemplateView):
    model = User
    template_name = "astormain/profile.html"

    def get_object(self):
        try:
            user = User.objects.filter(slug=self.kwargs["slug"]).first()
        except User.DoesNotExist:
            raise Http404("User does not exist.")
        return user

    def get_context_data(self, **kwargs):
        self.object = self.get_object()
        context = super(UserProfileView, self).get_context_data(**kwargs)
        analyses = [page.specific for page in self.object.pages.all() 
                                  if page.specific.live ]
        analyses = sorted(analyses, key=lambda item: item.first_published_date, 
                          reverse=True)
        context["analyses"] = analyses
        return context