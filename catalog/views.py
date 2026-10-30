from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.core.cache import cache
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse, reverse_lazy
from django.utils.decorators import method_decorator
from django.contrib import messages
from django.views.decorators.cache import cache_page
from django.views.generic import (
    ListView, DetailView, CreateView, UpdateView, DeleteView, View
)
from django.http import HttpResponseRedirect

from .forms import ContactForm, ProductForm
from .models import Product, Category, Contact
from .services import CatalogService


class HomeView(ListView):
    """Домашняя страница."""

    model = Product
    template_name = "catalog/home.html"
    context_object_name = "page_obj"
    paginate_by = 6
    ordering = ['-created_at']


class ProductDetailView(LoginRequiredMixin, DetailView):
    """Просмотр карточки продукта."""

    model = Product
    template_name = "catalog/product_detail.html"
    context_object_name = "product"

    @method_decorator(cache_page(60 * 15))
    def dispatch(self, *args, **kwargs):
        return super().dispatch(*args, **kwargs)


class ProductCreateView(LoginRequiredMixin, CreateView):
    """Создание продукта."""

    model = Product
    form_class = ProductForm
    template_name = "catalog/product_form.html"

    def form_valid(self, form):
        form.instance.owner = self.request.user
        response = super().form_valid(form)
        messages.success(self.request, f'Товар «{self.object.name}» успешно добавлен!')
        return response

    def form_invalid(self, form):
        messages.error(self.request, 'Пожалуйста, исправьте ошибки в форме.')
        return super().form_invalid(form)

    def get_success_url(self):
        return reverse('catalog:product_detail', kwargs={'pk': self.object.pk})


class OwnerOrModeratorMixin(UserPassesTestMixin):
    """Пропускает владельца продукта или модератора (can_unpublish_product)."""

    def test_func(self):
        product = self.get_object()
        user = self.request.user
        if user == product.owner:
            return True
        return user.has_perm('catalog.can_unpublish_product')

    def handle_no_permission(self):
        messages.error(self.request, 'У вас нет прав на это действие.')
        return redirect('catalog:home')


class ProductUpdateView(LoginRequiredMixin, OwnerOrModeratorMixin, UpdateView):
    """Редактирование продукта."""

    model = Product
    form_class = ProductForm
    template_name = "catalog/product_form.html"

    def get_success_url(self):
        return reverse(
            "catalog:product_detail",
            kwargs={"pk": self.object.pk},
        )

    def form_valid(self, form):
        response = super().form_valid(form)
        messages.success(self.request, f'Товар «{self.object.name}» обновлён!')
        return response

    def form_invalid(self, form):
        messages.error(self.request, 'Пожалуйста, исправьте ошибки в форме.')
        return super().form_invalid(form)


class ProductDeleteView(LoginRequiredMixin, OwnerOrModeratorMixin, DeleteView):
    """Удаление продукта с подтверждением."""
    model = Product
    template_name = "catalog/product_confirm_delete.html"
    success_url = reverse_lazy('catalog:home')

    def form_valid(self, form):
        messages.success(self.request, 'Товар удалён.')
        return super().form_valid(form)


class ProductUnpublishView(LoginRequiredMixin, View):
    """Отмена публикации продукта"""
    def post(self, request, pk):
        product = get_object_or_404(Product, pk=pk)
        if not request.user.has_perm('catalog.can_unpublish_product'):
            messages.error(request, 'Недостаточно прав.')
            return redirect('catalog:product_detail', pk=pk)
        product.status = Product.PublicationStatus.DRAFT
        product.save(update_fields=['status'])
        messages.success(request, 'Публикация отменена.')
        return redirect('catalog:product_detail', pk=pk)


class CategoryProductsView(ListView):
    """Список продуктов в категории."""

    template_name = "catalog/category_products.html"
    context_object_name = "products"
    paginate_by = 6

    def get_queryset(self):
        self.category = get_object_or_404(Category, pk=self.kwargs['pk'])
        cache_key = f'category_products_{self.category.pk}'

        products = cache.get(cache_key)
        if products is None:
            products = list(CatalogService.get_products_by_category(self.category.pk))
            cache.set(cache_key, products, 60 * 10)  # 10 минут

        return products

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['category'] = self.category
        return context


class ContactsView(View):
    """Форма обратной связи."""

    def get(self, request, *args, **kwargs):
        form = ContactForm()
        contact_info = Contact.objects.first()
        return self._render(request, form, contact_info)

    def post(self, request, *args, **kwargs):
        form = ContactForm(request.POST)
        if form.is_valid():
            messages.success(request, "Ваше сообщение успешно отправлено! Мы свяжемся с вами в ближайшее время.")
            return HttpResponseRedirect(reverse('catalog:contacts'))
        messages.error(request, "Пожалуйста, исправьте ошибки в форме.")
        contact_info = Contact.objects.first()
        return self._render(request, form, contact_info)

    def _render(self, request, form, contact_info):
        return render(request, "catalog/contacts.html",
                      {"form": form, "contact_info": contact_info})
