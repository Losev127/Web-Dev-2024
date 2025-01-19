from django import forms
from .models import Adver, Review, District
from django.utils.timezone import now

class AdverForm(forms.ModelForm):
    class Meta:
        model = Adver
        fields = ['price', 'own', 'image', 'mortgage', 'score', 'apartment']
        exclude = ['date_created']  # Исключаем поле date_created
        help_texts = {
            'price': 'Укажите стоимость в рублях.',
            'own': 'Введите имя владельца.',
            'image': 'Загрузите изображение квартиры.',
            'mortgage': 'Выберите, доступна ли ипотека.',
            'score': 'Укажите рейтинг от 1 до 10.',
            'apartment': 'Выберите квартиру из списка.',
        }
        error_messages = {
            'price': {
                'required': 'Пожалуйста, укажите стоимость.',
                'invalid': 'Введите корректное числовое значение.',
            },
            'own': {
                'required': 'Пожалуйста, укажите имя владельца.',
            },
            'score': {
                'min_value': 'Рейтинг не может быть меньше 1.',
                'max_value': 'Рейтинг не может быть больше 10.',
            },
        }

    def clean_score(self):
        """
        Валидация поля score (рейтинг).
        """
        score = self.cleaned_data.get('score')
        if score < 1 or score > 10:
            raise forms.ValidationError("Рейтинг должен быть от 1 до 10.")
        return score

    def clean_price(self):
        """
        Валидация поля price (цена).
        """
        price = self.cleaned_data.get('price')
        if price < 1000000:
            raise forms.ValidationError("Цена не может быть ниже 1,000,000 рублей.")
        return price

    def save(self, commit=True):
        adver = super().save(commit=False)
        if not adver.date_created:
            adver.date_created = now()
        if commit:
            adver.save()
        return adver



class ReviewForm(forms.ModelForm):
    text = forms.CharField(widget=forms.Textarea(attrs={'class': 'form-control', 'placeholder': 'Ваш отзыв'}))

    class Meta:
        model = Review
        fields = ['author', 'text', 'rating']
        widgets = {
            'author': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Ваше имя'}),
        }
        labels = {
            'author': 'Автор',
            'text': 'Отзыв',
            'rating': 'Рейтинг',
        }
        help_texts = {
            'author': 'Укажите ваше имя или псевдоним.',
            'text': 'Оставьте ваш отзыв о квартире.',
            'rating': 'Укажите рейтинг от 1 до 5.',
        }
        error_messages = {
            'author': {
                'required': 'Пожалуйста, укажите ваше имя.',
            },
            'text': {
                'required': 'Пожалуйста, напишите отзыв.',
            },
            'rating': {
                'required': 'Пожалуйста, укажите рейтинг.',
                'invalid': 'Введите корректное числовое значение.',
                'min_value': 'Рейтинг не может быть меньше 1.',
                'max_value': 'Рейтинг не может быть больше 5.',
            },
        }

    def clean_rating(self):
        rating = self.cleaned_data.get('rating')
        if rating is None:
            raise forms.ValidationError("Рейтинг обязателен для заполнения.")
        if rating < 1 or rating > 5:
            raise forms.ValidationError("Рейтинг должен быть в диапазоне от 1 до 5.")
        return rating



class ApartmentFilterForm(forms.Form):
    district = forms.ModelChoiceField(queryset=District.objects.all(), required=False, label="Район")
    min_area = forms.IntegerField(required=False, min_value=0, label="Минимальная площадь (кв.м.)")
    max_area = forms.IntegerField(required=False, min_value=0, label="Максимальная площадь (кв.м.)")
    rooms = forms.IntegerField(required=False, min_value=1, label="Количество комнат")
    min_floor = forms.IntegerField(required=False, min_value=0, label="Минимальный этаж")
    max_floor = forms.IntegerField(required=False, min_value=0, label="Максимальный этаж")
    address = forms.CharField(required=False, label="Адрес")
    description = forms.CharField(required=False, label="Описание")