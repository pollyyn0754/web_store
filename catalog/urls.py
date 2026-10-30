from django.urls import path
from catalog.apps import CatalogConfig
from catalog.views import (
    HomeView, ContactsView, ProductDetailView,
    ProductCreateView, ProductUpdateView, ProductDeleteView, ProductUnpublishView, CategoryProductsView
)

app_name = CatalogConfig.name

urlpatterns = [
    path("", HomeView.as_view(), name="home"),
    path("contacts/", ContactsView.as_view(), name="contacts"),
    path("product/<int:pk>/", ProductDetailView.as_view(), name="product_detail"),
    path("product/create/", ProductCreateView.as_view(), name="product_create"),
    path("product/<int:pk>/update/", ProductUpdateView.as_view(), name="product_update"),
    path("product/<int:pk>/delete/", ProductDeleteView.as_view(), name="product_delete"),
    path("product/<int:pk>/unpublish/", ProductUnpublishView.as_view(), name="product_unpublish"),
    path("category/<int:pk>/products/", CategoryProductsView.as_view(), name="category_products"),
]
