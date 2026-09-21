from django.shortcuts import render, get_object_or_404, redirect
from django.http import HttpResponseRedirect
from django.urls import reverse
from django.contrib import messages
from django.core.paginator import Paginator

from .forms import ContactForm, ProductForm
from .models import Product, Contact


def home(request):
    """Главная страница с пагинацией списка товаров."""
    products = Product.objects.order_by('-created_at')
    paginator = Paginator(products, 6)  # по 6 товаров на страницу
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    return render(request, "catalog/home.html", {"page_obj": page_obj})


def product_detail(request, pk):
    product = get_object_or_404(Product, pk=pk)
    return render(request, "catalog/product_detail.html", {"product": product})


def product_create(request):
    """Добавление нового товара."""
    if request.method == 'POST':
        form = ProductForm(request.POST, request.FILES)
        if form.is_valid():
            product = form.save()
            messages.success(request, f'Товар «{product.name}» успешно добавлен!')
            return redirect('catalog:product_detail', pk=product.pk)
        else:
            messages.error(request, 'Пожалуйста, исправьте ошибки в форме.')
    else:
        form = ProductForm()

    return render(request, "catalog/product_form.html", {"form": form})


def contacts(request):
    if request.method == "POST":
        form = ContactForm(request.POST)
        if form.is_valid():
            messages.success(
                request,
                "Ваше сообщение успешно отправлено! Мы свяжемся с вами в ближайшее время."
            )
            return HttpResponseRedirect(reverse('catalog:contacts'))
        else:
            messages.error(request, "Пожалуйста, исправьте ошибки в форме.")
    else:
        form = ContactForm()

    contact_info = Contact.objects.first()

    return render(
        request,
        "catalog/contacts.html",
        {"form": form, "contact_info": contact_info},
    )
