from django.shortcuts import render
from django.http import HttpResponseRedirect
from django.urls import reverse
from django.contrib import messages

from .forms import ContactForm


def home(request):
    return render(request, "home.html")


def contacts(request):
    if request.method == "POST":
        form = ContactForm(request.POST)
        if form.is_valid():

            # Добавляем сообщение об успехе
            messages.success(request, "Ваше сообщение успешно отправлено! Мы свяжемся с вами в ближайшее время.")

            # Перенаправляем на страницу контактов для избежания повторной отправки
            return HttpResponseRedirect(reverse('catalog:contacts'))
        else:
            messages.error(request, "Пожалуйста, исправьте ошибки в форме.")
    else:
        form = ContactForm()

    return render(request, "contacts.html", {"form": form})
