page_registry = list()

def register_page(cls):
    if cls not in page_registry:
        page_registry.append(cls)
    return cls