from django.shortcuts import render, redirect
from django.urls import reverse
from django.contrib.contenttypes.models import ContentType
from django.http import HttpResponse
from django.contrib.auth.decorators import login_required
from django.contrib.auth import get_user_model
from django.contrib import messages

from astorcore.models import Page, ContentPage
from astorcore.decorators import get_page_models, get_forms
from astoraccount.models import Activity
import astoraccount.forms


def index_page(request):
    '''Returns root page of the account'''
    return render(request, "astoraccount/index.html")


def page_new(request):
    '''Returns page to select type of new page'''
    pages = list()
    for page in get_page_models():
        content_type = ContentType.objects.get_for_model(page)    
        pages.append({
            "title": page.verbose_name.title(), 
            "type": content_type.app_label + ":" + content_type.model
        })
    return render(request, "astoraccount/page_new.html", {"pages": pages})


@login_required
def page_create(request):
    user = request.user
    if user.is_authenticated:
        app_label, model = request.GET["type"].split(":")
        ctype = ContentType.objects.get(app_label=app_label, model=model)
        cls = ctype.model_class()
        page = user.root_page.add_child(instance=cls())
        user.add_activity(
            number=Activity.NEW_PAGE, content_object=page,
            message="Page created: \"%s\" id=%d type=%s" % (page.specific.title, 
                page.id, page.specific.verbose_name.title())
        )

    return redirect(reverse("astoraccount:page_edit", 
                            kwargs={"page_id": page.id}))

@login_required
def page_edit(request, page_id):
    page = Page.objects.filter(id=page_id).first()

    # Find the proper form for the page.
    form_cls = None
    for form in get_forms():
        if type(page.specific) == form._meta.model:
            form_cls = form
            break

    if request.method == "POST":
        form = form_cls(request.POST, instance=page.specific)
        if form.is_valid:
            form.save()
            request.user.add_activity(
                number=Activity.UPDATE_PAGE, content_object=page,
                message="Page updated: \"%s\" id=%d type=%s" % (page.specific.title, 
                    page.id, page.specific.verbose_name.title())
            )
            messages.success(
                request, "The page was updated and published successfully.",
                fail_silently=True
            )
    else:
        form = form_cls(instance=page.specific)

    return render(request, "astoraccount/page_edit.html", 
                  {"form": form})