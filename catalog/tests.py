import io

from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group, Permission
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import TestCase
from django.urls import reverse
from catalog.models import Category, Product
from PIL import Image

from catalog.forms import ProductForm
from catalog.models import Category


def _make_image_file(name: str, size: tuple = (10, 10), fmt: str = 'PNG') -> SimpleUploadedFile:
    """Создаёт настоящее изображение в памяти и оборачивает в SimpleUploadedFile."""
    buffer = io.BytesIO()
    img = Image.new('RGB', size, color=(200, 100, 50))
    img.save(buffer, format=fmt)
    buffer.seek(0)
    ext = 'png' if fmt.upper() == 'PNG' else 'jpg'
    content_type = 'image/png' if fmt.upper() == 'PNG' else 'image/jpeg'
    return SimpleUploadedFile(f'{name}.{ext}', buffer.read(), content_type=content_type)


def _make_large_image(name: str = 'big', target_size_bytes: int = 6 * 1024 * 1024) -> SimpleUploadedFile:
    """Быстро создаёт валидное изображение, вес которого > 5 МБ."""
    buffer = io.BytesIO()
    # Создаем маленькую валидную картинку
    Image.new('RGB', (10, 10), color=(255, 0, 0)).save(buffer, format='PNG')

    # Достаем байты картинки и добавляем в конец "мусор" (padding)
    # Pillow проигнорирует лишние байты в конце, но Django посчитает общий размер файла
    data = buffer.getvalue() + b'\x00' * (target_size_bytes - buffer.tell())

    return SimpleUploadedFile(f'{name}.png', data, content_type='image/png')


class ProductFormValidationTests(TestCase):
    """Тесты валидации формы ProductForm."""

    def setUp(self):
        self.category = Category.objects.create(name='Тестовая категория')

    def _base_data(self, **overrides):
        data = {
            'name': 'Хороший товар',
            'description': 'Хорошее описание',
            'category': self.category.pk,
            'price': '100.00',
        }
        data.update(overrides)
        return data

    # ---------- 1. Запрещённые слова в названии ----------
    def test_forbidden_word_in_name(self):
        form = ProductForm(
            data=self._base_data(name='Казино мечты'),
            files={'image': _make_image_file('ok')},
        )
        self.assertFalse(form.is_valid())
        self.assertIn('name', form.errors)
        self.assertIn('казино', form.errors['name'][0].lower())

    # ---------- 2. Запрещённые слова в описании ----------
    def test_forbidden_word_in_description(self):
        form = ProductForm(
            data=self._base_data(description='Это просто обман!'),
            files={'image': _make_image_file('ok')},
        )
        self.assertFalse(form.is_valid())
        self.assertIn('description', form.errors)
        self.assertIn('обман', form.errors['description'][0].lower())

    # ---------- 3. Запрещённые слова в разном регистре ----------
    def test_forbidden_word_case_insensitive_upper(self):
        form = ProductForm(
            data=self._base_data(name='КРИПТОВАЛЮТА для всех'),
            files={'image': _make_image_file('ok')},
        )
        self.assertFalse(form.is_valid())
        self.assertIn('name', form.errors)

    def test_forbidden_word_case_insensitive_mixed(self):
        form = ProductForm(
            data=self._base_data(description='ДешеВо и сердито'),
            files={'image': _make_image_file('ok')},
        )
        self.assertFalse(form.is_valid())
        self.assertIn('description', form.errors)

    # ---------- 4. Отрицательная цена ----------
    def test_negative_price(self):
        form = ProductForm(
            data=self._base_data(price='-1.00'),
            files={'image': _make_image_file('ok')},
        )
        self.assertFalse(form.is_valid())
        self.assertIn('price', form.errors)
        self.assertIn('отрицательн', form.errors['price'][0].lower())

    # ---------- 5. Слишком большой файл ----------
    def test_image_too_large(self):
        big = _make_large_image('big', target_size_bytes=6 * 1024 * 1024)

        # В SimpleUploadedFile размер хранится в свойстве size
        self.assertGreater(big.size, 5 * 1024 * 1024)

        form = ProductForm(
            data=self._base_data(),
            files={'image': big},
        )
        self.assertFalse(form.is_valid())
        self.assertIn('image', form.errors)
        self.assertIn('5 мб', form.errors['image'][0].lower())

    # ---------- 6. Неверный формат файла ----------
    def test_image_wrong_format_gif(self):
        buffer = io.BytesIO()
        Image.new('RGB', (10, 10), color=(0, 255, 0)).save(buffer, format='GIF')
        buffer.seek(0)
        gif = SimpleUploadedFile('anim.gif', buffer.read(), content_type='image/gif')

        form = ProductForm(
            data=self._base_data(),
            files={'image': gif},
        )
        self.assertFalse(form.is_valid())
        self.assertIn('image', form.errors)
        self.assertIn('jpeg', form.errors['image'][0].lower())
        self.assertIn('png', form.errors['image'][0].lower())

    # ---------- 7. Успешная валидация PNG ----------
    def test_valid_form(self):
        form = ProductForm(
            data=self._base_data(),
            files={'image': _make_image_file('ok')},
        )
        self.assertTrue(form.is_valid(), msg=form.errors)

    # ---------- 8. Валидный файл JPG ----------
    def test_valid_jpg_image(self):
        jpg = _make_image_file('photo', fmt='JPEG')
        form = ProductForm(
            data=self._base_data(),
            files={'image': jpg},
        )
        self.assertTrue(form.is_valid(), msg=form.errors)


class PermissionTests(TestCase):
    def setUp(self):
        User = get_user_model()
        self.owner = User.objects.create_user(email='owner@test.ru', password='pass12345')
        self.other = User.objects.create_user(email='other@test.ru', password='pass12345')
        self.moderator = User.objects.create_user(email='mod@test.ru', password='pass12345')
        mod_group, _ = Group.objects.get_or_create(name='Модератор продуктов')
        mod_group.permissions.add(
            Permission.objects.get(codename='can_unpublish_product'),
            Permission.objects.get(codename='delete_product'),
        )
        self.moderator.groups.add(mod_group)

        self.category = Category.objects.create(name='Cat')
        self.product = Product.objects.create(
            name='Товар', category=self.category, price=100, owner=self.owner,
        )

    def test_owner_can_update(self):
        self.client.login(email='owner@test.ru', password='pass12345')
        response = self.client.get(reverse('catalog:product_update', args=[self.product.pk]))
        self.assertEqual(response.status_code, 200)

    def test_other_cannot_update(self):
        self.client.login(email='other@test.ru', password='pass12345')
        response = self.client.get(reverse('catalog:product_update', args=[self.product.pk]))
        self.assertIn(response.status_code, (302, 403))

    def test_moderator_can_delete(self):
        self.client.login(email='mod@test.ru', password='pass12345')
        response = self.client.post(reverse('catalog:product_delete', args=[self.product.pk]))
        self.assertIn(response.status_code, (302, 200))
