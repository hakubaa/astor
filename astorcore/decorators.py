__all__ = ["register_page", "register_form", "register_serializer",
           "get_page_models", "get_forms", "get_serializers"]


PAGE_REGISTRY = list()
FORM_REGISTRY = list()
SERIALIZER_REGISTRY = list()

def create_register_decorator(register):
    def registrator(cls):
        if cls not in register:
            register.append(cls)
        return cls
    return registrator

def create_register_getter(register):
    def getter():
        return register
    return getter


register_page = create_register_decorator(PAGE_REGISTRY)
register_form = create_register_decorator(FORM_REGISTRY)
register_serializer = create_register_decorator(SERIALIZER_REGISTRY)

get_page_models = create_register_getter(PAGE_REGISTRY)
get_forms = create_register_getter(FORM_REGISTRY)
get_serializers = create_register_getter(SERIALIZER_REGISTRY)