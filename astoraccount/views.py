from django.shortcuts import render
from django.contrib.contenttypes.models import ContentType

import astorcore.decorators as decos


def index_page(request):
    '''Returns root page of the account'''
    return render(request, "astoraccount/index.html")


def page_new(request):
    '''Returns page to select type of new page'''
    pages = list()
    for page in decos.page_registry:
        content_type = ContentType.objects.get_for_model(page)    
        pages.append({
            "title": page.verbose_name.title(), 
            "type": content_type.app_label + ":" + content_type.name 
        })
    return render(request, "astoraccount/page_new.html", {"pages": pages})


def page_create(request):
    pass