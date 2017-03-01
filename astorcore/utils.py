from copy import copy

from django.db.models.deletion import Collector
from django.db.models.fields.related import ForeignKey


def clone_page(page, skip_fields=["published_page"]):
    '''Clones the page and its all related models. Saves cloned page in db.'''

    collector = Collector(using="default")
    collector.collect([page])
    collector.sort()

    # Identify all related models.
    related_models = collector.data.keys()
    data_models = list(
        (key, item.pop()) for key, item in collector.data.items()
    )

    # Collect requried data
    mstor = []
    for model_class, model_inst in data_models:
        ptr_names = list()
        for f in model_inst._meta.fields:
            if (isinstance(f, ForeignKey) and f.rel.to in related_models
                    and f.name not in skip_fields): # recursive relation
                ptr_names.append((f.name, f.rel.to))
        mstor.append((model_class, model_inst, ptr_names))

    # Create models starting from the first in the hierarchy
    mstor = reversed(mstor)
    ptrs = dict()
    for model_class, model_inst, base_ptrs in mstor:
        page_clone = copy(model_inst)
        page_clone.id = None
        page_clone.pk = None
        page_clone.published_page = None
        if base_ptrs:
            for ptr_name, ptr_class in base_ptrs:
                setattr(page_clone, ptr_name, ptrs[ptr_class])
        page_clone.save()
        ptrs[model_class] = page_clone

    return page_clone


def user_directory_path(instance, filename):
    '''
    Create path where the file will be save: MEDIA_ROOT/analyses/user_slug/page_pk/<filename>
    '''
    return "analyses/{0}/{1}/{2}".format(instance.user.slug, instance.pk, filename)