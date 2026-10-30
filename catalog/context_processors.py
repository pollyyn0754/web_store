from .services import CatalogService

def categories(request):
    """Передаёт список всех категорий во все шаблоны."""
    return {
        'all_categories': CatalogService.get_all_categories()
    }
