from django.core.management.base import BaseCommand
from django.core.management import call_command
from django.db import transaction

from catalog.models import Category, Product


class Command(BaseCommand):
    help = (
        'Удаляет все категории и продукты, затем загружает '
        'фикстуру catalog_fixture.json.'
    )

    def handle(self, *args, **options):
        self.stdout.write(self.style.WARNING('Удаляем существующие данные...'))
        with transaction.atomic():
            Product.objects.all().delete()
            Category.objects.all().delete()
        self.stdout.write(self.style.SUCCESS('Данные удалены.'))

        self.stdout.write('Загружаем catalog_fixture.json...')
        call_command('loaddata', 'catalog_fixture.json', verbosity=0)

        self.stdout.write(self.style.SUCCESS(
            f'Готово. Категорий: {Category.objects.count()}, '
            f'продуктов: {Product.objects.count()}.'
        ))
