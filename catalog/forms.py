import os
from django import forms
from django.core.exceptions import ValidationError
from .models import Product
from .validators import validate_forbidden_words


class ContactForm(forms.Form):
    # ... оставляем без изменений ...
    name = forms.CharField(
        max_length=100, label="Имя",
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Ваше имя',
            'required': True
        })
    )
    phone = forms.CharField(
        max_length=20, label="Телефон",
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Контактный телефон',
            'required': True
        })
    )
    message = forms.CharField(
        label="Сообщение",
        widget=forms.Textarea(attrs={
            'class': 'form-control',
            'placeholder': 'Ваше сообщение',
            'rows': 4,
            'required': True
        })
    )


class ProductForm(forms.ModelForm):
    """Форма создания/редактирования продукта с валидацией."""

    class Meta:
        model = Product
        fields = ['name', 'description', 'image', 'category', 'price']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Название товара'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 4, 'placeholder': 'Описание'}),
            'category': forms.Select(attrs={'class': 'form-select'}),
            'price': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
            'image': forms.ClearableFileInput(attrs={'class': 'form-control'}),
        }
        labels = {
            'name': 'Наименование',
            'description': 'Описание',
            'image': 'Изображение',
            'category': 'Категория',
            'price': 'Цена',
        }

    # ---------- Задание 3: единая стилизация через __init__ ----------
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field_name, field in self.fields.items():
            # Bootstrap-стили для всех полей
            css_class = 'form-check-input' if isinstance(field.widget, forms.CheckboxInput) \
                else ('form-select' if isinstance(field.widget, forms.Select) else 'form-control')

            existing = field.widget.attrs.get('class', '')
            field.widget.attrs['class'] = f'{existing} {css_class}'.strip()
            field.widget.attrs.setdefault('placeholder', field.label or field_name.capitalize())

    # ---------- Задание 1: запрещённые слова ----------
    def clean_name(self):
        name = self.cleaned_data.get('name', '')
        validate_forbidden_words(name)
        return name

    def clean_description(self):
        description = self.cleaned_data.get('description', '')
        validate_forbidden_words(description)
        return description

    # ---------- Задание 2: цена не может быть отрицательной ----------
    def clean_price(self):
        price = self.cleaned_data.get('price')
        if price is None:
            return price
        if price < 0:
            raise ValidationError('Цена не может быть отрицательной.')
        return price

    # ---------- Доп. задание: валидация изображения ----------
    def clean_image(self):
        image = self.cleaned_data.get('image')

        if not image:
            return image

        # Проверка расширения
        ext = os.path.splitext(image.name)[1].lower().lstrip('.')
        if ext not in {'jpg', 'jpeg', 'png'}:
            raise ValidationError('Допустимы только файлы форматов JPEG и PNG.')

        # Проверка размера — не более 5 МБ
        max_size = 5 * 1024 * 1024
        if image.size > max_size:
            raise ValidationError('Размер файла не должен превышать 5 МБ.')

        # Дополнительная проверка MIME (если доступен)
        content_type = getattr(image, 'content_type', '')
        if content_type and content_type not in {'image/jpeg', 'image/png'}:
            raise ValidationError('Допустимы только изображения JPEG или PNG.')

        return image
