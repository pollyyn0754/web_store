from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group, Permission
from django.contrib.contenttypes.models import ContentType
from django.test import TestCase
from django.urls import reverse
from .models import BlogPost


class BlogPermissionsTests(TestCase):
    def setUp(self):
        User = get_user_model()
        self.author = User.objects.create_user(email='author@test.ru', password='pass12345')
        self.manager = User.objects.create_user(email='cm@test.ru', password='pass12345')

        group, _ = Group.objects.get_or_create(name='Контент-менеджер')
        perm = Permission.objects.get(
            content_type=ContentType.objects.get_for_model(BlogPost),
            codename='can_manage_blog',
        )
        group.permissions.add(perm)
        self.manager.groups.add(group)

        self.post = BlogPost.objects.create(
            title='Тест', content='Контент', is_published=True,
        )

    def test_anonymous_cannot_create(self):
        response = self.client.get(reverse('blog:post_create'))
        self.assertEqual(response.status_code, 302)
        self.assertIn('/users/login/', response.url)   # проверяем, что ведёт на логин

    def test_author_without_group_cannot_create(self):
        self.client.login(email='author@test.ru', password='pass12345')
        response = self.client.get(reverse('blog:post_create'))
        # handle_no_permission переопределён на redirect → 302
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, reverse('blog:post_list'))

    def test_content_manager_can_create(self):
        self.client.login(email='cm@test.ru', password='pass12345')
        response = self.client.get(reverse('blog:post_create'))
        self.assertEqual(response.status_code, 200)

    def test_content_manager_can_delete(self):
        self.client.login(email='cm@test.ru', password='pass12345')
        response = self.client.post(reverse('blog:post_delete', args=[self.post.pk]))
        self.assertEqual(response.status_code, 302)
        self.assertFalse(BlogPost.objects.filter(pk=self.post.pk).exists())

    def test_superuser_can_create(self):
        User = get_user_model()
        admin = User.objects.create_superuser(email='admin@test.ru', password='pass12345')
        self.client.login(email='admin@test.ru', password='pass12345')
        response = self.client.get(reverse('blog:post_create'))
        self.assertEqual(response.status_code, 200)
