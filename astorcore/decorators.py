PAGE_REGISTRY = list()
FORM_REGISTRY = list()

def register_page(cls):
    if cls not in PAGE_REGISTRY:
        PAGE_REGISTRY.append(cls)
    return cls

def get_page_models():
    return PAGE_REGISTRY

def register_form(cls):
    if cls not in FORM_REGISTRY:
        FORM_REGISTRY.append(cls)
    return cls;

def get_forms():
    return FORM_REGISTRY