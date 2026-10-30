from django.core.management.base import BaseCommand
from django.contrib.auth.models import Group, Permission
from django.contrib.contenttypes.models import ContentType
from catalog.models import Product
from blog.models import BlogPost


class Command(BaseCommand):
    help = 'Создаёт группы «Модератор продуктов» и «Контент-менеджер»'

    def handle(self, *args, **options):
        # Модератор продуктов
        mod, mod_created = Group.objects.get_or_create(name='Модератор продуктов')
        mod.permissions.set(Permission.objects.filter(
            content_type=ContentType.objects.get_for_model(Product),
            codename__in=['can_unpublish_product', 'delete_product'],
        ))
        self.stdout.write(self.style.SUCCESS(
            f'Группа «Модератор продуктов» {"создана" if mod_created else "обновлена"}.'
        ))

        # Контент-менеджер
        cm, cm_created = Group.objects.get_or_create(name='Контент-менеджер')
        cm.permissions.set(Permission.objects.filter(
            content_type=ContentType.objects.get_for_model(BlogPost),
            codename='can_manage_blog',
        ))
        self.stdout.write(self.style.SUCCESS(
            f'Группа «Контент-менеджер» {"создана" if cm_created else "обновлена"}.'
        ))
