from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse, reverse_lazy
from django.contrib import messages
from django.views.generic import (
    ListView, DetailView, CreateView, UpdateView, DeleteView, View
)
from django.http import HttpResponseRedirect

from .forms import ContactForm, ProductForm
from .models import Product, Contact


class HomeView(ListView):
    model = Product
    template_name = "catalog/home.html"
    context_object_name = "page_obj"
    paginate_by = 6
    ordering = ['-created_at']


class ProductDetailView(DetailView):
    model = Product
    template_name = "catalog/product_detail.html"
    context_object_name = "product"


class ProductCreateView(CreateView):
    model = Product
    form_class = ProductForm
    template_name = "catalog/product_form.html"

    def form_valid(self, form):
        response = super().form_valid(form)
        messages.success(self.request, f'Товар «{self.object.name}» успешно добавлен!')
        return response

    def form_invalid(self, form):
        messages.error(self.request, 'Пожалуйста, исправьте ошибки в форме.')
        return super().form_invalid(form)

    def get_success_url(self):
        return reverse('catalog:product_detail', kwargs={'pk': self.object.pk})


class ProductUpdateView(UpdateView):
    """Редактирование продукта."""
    model = Product
    form_class = ProductForm
    template_name = "catalog/product_form.html"

    def form_valid(self, form):
        response = super().form_valid(form)
        messages.success(self.request, f'Товар «{self.object.name}» обновлён!')
        return response

    def form_invalid(self, form):
        messages.error(self.request, 'Пожалуйста, исправьте ошибки в форме.')
        return super().form_invalid(form)

    def get_success_url(self):
        return reverse('catalog:product_detail', kwargs={'pk': self.object.pk})


class ProductDeleteView(DeleteView):
    """Удаление продукта с подтверждением."""
    model = Product
    template_name = "catalog/product_confirm_delete.html"
    success_url = reverse_lazy('catalog:home')

    def form_valid(self, form):
        messages.success(self.request, 'Товар удалён.')
        return super().form_valid(form)


class ContactsView(View):
    # ... оставляем без изменений ...
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
