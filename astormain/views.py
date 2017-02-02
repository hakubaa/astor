from django.shortcuts import render, get_object_or_404

from astorcore.models import Page


def home_page(request):
    newest_entries = [ page.specific for page in Page.objects.all() 
                                     if not page.is_root() ]
    return render(request, "astormain/home.html", 
                  { "newest_entries": newest_entries })


def entry_page(request, username, page_id):
    page = get_object_or_404(Page, pk=page_id).specific
    return render(request, page.template_name, {"page": page})


def user_profile(request, username):
    pass