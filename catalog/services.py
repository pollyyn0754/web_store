from .models import Product, Category


class CatalogService:
    """Сервис для работы с продуктами и категориями."""

    @staticmethod
    def get_products_by_category(category_id):
        """Возвращает список продуктов в указанной категории."""
        return (
            Product.objects
            .filter(category_id=category_id)
            .select_related('category')
            .order_by('name')
        )

    @staticmethod
    def get_all_categories():
        """Возвращает queryset всех категорий, упорядоченный по имени."""
        return Category.objects.all().order_by('name')
