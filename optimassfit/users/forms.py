from django import forms
from django.contrib.auth.forms import UserCreationForm
from .models import User

class RegisterForm(UserCreationForm):
    username = forms.CharField(
        label="Логин",
        max_length=150,
        required=True
    )
    email = forms.EmailField(
        label="Электронная почта",
        required=True
    )
    password1 = forms.CharField(
        label="Пароль",
        widget=forms.PasswordInput,
        required=True
    )
    password2 = forms.CharField(
        label="Подтверждение пароля",
        widget=forms.PasswordInput,
        required=True
    )
    age = forms.IntegerField(
        label="Возраст",
        min_value=10,
        max_value=100,
        required=True
    )
    height = forms.FloatField(
        label="Рост (см)",
        min_value=100,
        max_value=250,
        required=True
    )
    weight = forms.FloatField(
        label="Вес (кг)",
        min_value=30,
        max_value=200,
        required=True
    )
    gender = forms.ChoiceField(
        label="Пол",
        choices=[('male', 'Мужчина'), ('female', 'Женщина')]
    )
    goal = forms.ChoiceField(
        label="Цель",
        choices=[('lose_weight', 'Похудение'), ('gain_weight', 'Набор массы'), ('maintain', 'Поддержание веса')]
    )
    target_months = forms.ChoiceField(
        label="Период тренировок",
        choices=[(1, '1 месяц'), (3, '3 месяца')]
    )
    training_level = forms.ChoiceField(
        label="Количество тренировок в неделю",
        choices=[("1", "1 раз"), ("2-3", "2-3 раза"), ("4-5", "4-5 раз"), ("6+", "6 и более")]
    )

    class Meta:
        model = User
        fields = [
            'username',
            'email',
            'password1',
            'password2',
            'age',
            'height',
            'weight',
            'gender',
            'goal',
            'target_months',
            'training_level'
        ]

class ProfileUpdateForm(forms.ModelForm):
    """Форма обновления профиля пользователя"""
    class Meta:
        model = User
        fields = ['age', 'height', 'weight', 'goal', 'training_level', 'target_months']
        labels = {
            'age': 'Возраст',
            'height': 'Рост (см)',
            'weight': 'Вес (кг)',
            'goal': 'Цель',
            'training_level': 'Количество тренировок в месяц',
            'target_months': 'Период тренировок'
        }
