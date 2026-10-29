from django.shortcuts import render, redirect
from django.urls import reverse_lazy
from django.views.generic import CreateView, UpdateView
from django.contrib.auth.views import LoginView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.mail import send_mail
from django.contrib import messages
from django.conf import settings

from .forms import UserRegisterForm, UserLoginForm, UserProfileForm


class UserRegisterView(CreateView):
    """Регистрация пользователя."""
    form_class = UserRegisterForm
    template_name = 'users/register.html'
    success_url = reverse_lazy('users:login')

    def form_valid(self, form):
        # super() сохраняет форму один раз и кладёт объект в self.object
        response = super().form_valid(form)
        user = self.object

        send_mail(
            subject='Добро пожаловать в Skystore!',
            message=(
                f'Здравствуйте! Вы успешно зарегистрировались на сайте Skystore.\n'
                f'Ваш логин: {user.email}'
            ),
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[user.email],
            fail_silently=False,
        )
        messages.success(
            self.request,
            'Регистрация прошла успешно! Теперь вы можете войти.'
        )
        return response


class UserLoginView(LoginView):
    """Авторизация по email и паролю."""
    form_class = UserLoginForm
    template_name = 'users/login.html'

    def form_invalid(self, form):
        messages.error(self.request, 'Неверный email или пароль.')
        return super().form_invalid(form)


class UserProfileUpdateView(LoginRequiredMixin, UpdateView):
    """Редактирование профиля."""
    form_class = UserProfileForm
    template_name = 'users/profile.html'
    success_url = reverse_lazy('users:profile')

    def get_object(self, queryset=None):
        return self.request.user

    def form_valid(self, form):
        messages.success(self.request, 'Профиль успешно обновлен.')
        return super().form_valid(form)
