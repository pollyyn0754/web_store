from django.contrib import messages
from django.core.mail import send_mail
from django.conf import settings
from django.urls import reverse_lazy
from django.views.generic import (
    ListView, DetailView, CreateView, UpdateView, DeleteView
)

from .models import BlogPost
from .forms import BlogPostForm


class BlogPostListView(ListView):
    """Список только опубликованных статей."""
    model = BlogPost
    template_name = 'blog/blogpost_list.html'
    context_object_name = 'posts'
    paginate_by = 6

    def get_queryset(self):
        # Фильтрация: показываем только опубликованные статьи
        return BlogPost.objects.filter(is_published=True)


class BlogPostDetailView(DetailView):
    """Просмотр статьи с инкрементом счётчика просмотров."""
    model = BlogPost
    template_name = 'blog/blogpost_detail.html'
    context_object_name = 'post'

    def get_object(self, queryset=None):
        obj = super().get_object(queryset)
        # Увеличиваем счётчик просмотров
        obj.views_count += 1
        obj.save(update_fields=['views_count'])

        # Дополнительное задание: поздравление при 100 просмотрах
        if obj.views_count == 100:
            try:
                send_mail(
                    subject='Поздравляем! Статья достигла 100 просмотров',
                    message=(
                        f'Статья «{obj.title}» достигла 100 просмотров!\n\n'
                        f'Ссылка: /blog/{obj.pk}/'
                    ),
                    from_email=settings.DEFAULT_FROM_EMAIL,
                    recipient_list=[settings.DEFAULT_FROM_EMAIL],
                    fail_silently=True,
                )
            except Exception:
                pass

        return obj


class BlogPostCreateView(CreateView):
    model = BlogPost
    form_class = BlogPostForm
    template_name = 'blog/blogpost_form.html'
    success_url = reverse_lazy('blog:post_list')

    def form_valid(self, form):
        response = super().form_valid(form)
        messages.success(self.request, f'Статья «{self.object.title}» создана!')
        return response


class BlogPostUpdateView(UpdateView):
    model = BlogPost
    form_class = BlogPostForm
    template_name = 'blog/blogpost_form.html'

    def form_valid(self, form):
        response = super().form_valid(form)
        messages.success(self.request, f'Статья «{self.object.title}» обновлена!')
        return response

    def get_success_url(self):
        # Перенаправление на просмотр статьи после редактирования
        return reverse_lazy('blog:post_detail', kwargs={'pk': self.object.pk})


class BlogPostDeleteView(DeleteView):
    model = BlogPost
    template_name = 'blog/blogpost_confirm_delete.html'
    success_url = reverse_lazy('blog:post_list')

    def form_valid(self, form):
        messages.success(self.request, 'Статья удалена.')
        return super().form_valid(form)

