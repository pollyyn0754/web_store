from django.core.exceptions import ValidationError

FORBIDDEN_WORDS = [
    'казино',
    'криптовалюта',
    'крипта',
    'биржа',
    'дешево',
    'бесплатно',
    'обман',
    'полиция',
    'радар',
]


def validate_forbidden_words(value: str):
    """Проверяет наличие запрещённых слов (в любом регистре)."""
    if not value:
        return
    lowered = value.lower()
    for word in FORBIDDEN_WORDS:
        if word in lowered:
            raise ValidationError(
                f'Слово «{word}» запрещено использовать в названии и описании продукта.'
            )
