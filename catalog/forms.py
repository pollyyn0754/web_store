from django import forms
from .models import Product


class ContactForm(forms.Form):
    name = forms.CharField(
        max_length=100,
        label="Имя",
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Ваше имя',
            'required': True
        })
    )
    phone = forms.CharField(
        max_length=20,
        label="Телефон",
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
