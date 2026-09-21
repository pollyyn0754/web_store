from django.shortcuts import render
from django.http import HttpResponseRedirect
from django.urls import reverse
from django.contrib import messages

from .forms import ContactForm
from .models import Product, Contact


def home(request):
    # Последние 5 созданных продуктов: сортировка по дате создания по убыванию, срез [:5]
    latest_products = Product.objects.order_by('-created_at')[:5]

    # Вывод в консоль
    print('Последние 5 созданных продуктов:')
    for product in latest_products:
        print(
            f'  #{product.pk} | {product.name} | '
            f'{product.price} ₽ | {product.created_at:%d.%m.%Y %H:%M}'
        )

    return render(request, "home.html", {"latest_products": latest_products})


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

    # Данные из админки (первая запись контактов)
    contact_info = Contact.objects.first()

    return render(
        request,
        "contacts.html",
        {"form": form, "contact_info": contact_info},
    )
