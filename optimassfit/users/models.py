from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin
from django.db import models
from django.conf import settings
from django.db import models


class UserManager(BaseUserManager):
    def create_user(self, username, password=None, **extra_fields):
        if not username:
            raise ValueError('The Username field must be set')
        user = self.model(username=username, **extra_fields)
        user.set_password(password)
        user.is_superuser = True  # Значение по умолчанию
        user.save(using=self._db)
        return user

    def create_superuser(self, username, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        extra_fields.setdefault('age', 18)
        extra_fields.setdefault('height', 170)
        extra_fields.setdefault('weight', 70)
        extra_fields.setdefault('gender', 'male')
        extra_fields.setdefault('goal', 'maintain')
        extra_fields.setdefault('target_months', 1)
        extra_fields.setdefault('training_level', '2-3')
        return self.create_user(username, password, **extra_fields)

    def get_by_natural_key(self, username):
        return self.get(**{self.model.USERNAME_FIELD: username})

class User(AbstractBaseUser, PermissionsMixin):
    username = models.CharField(max_length=150, unique=True)
    email = models.EmailField(unique=True, blank=True, null=True)
    password = models.CharField(max_length=128)
    age = models.IntegerField(null=True)
    height = models.FloatField(null=True)
    weight = models.FloatField(null=True)
    gender = models.CharField(max_length=10, choices=[('male', 'Мужчина'), ('female', 'Женщина')], null=True)
    goal = models.CharField(
        max_length=15,
        choices=[('lose_weight', 'Похудение'), ('gain_weight', 'Набор массы'), ('maintain', 'Поддержание')],
        null=True
    )
    target_months = models.IntegerField(choices=[(1, '1 месяц'), (3, '3 месяца')], null=True)
    training_level = models.CharField(
        max_length=10,
        choices=[("1", "1 раз"), ("2-3", "2-3 раза"), ("4-5", "4-5 раз"), ("6+", "6 и более")],
        default="2-3",
        null=True
    )
    date_joined = models.DateTimeField(auto_now_add=True)

    is_staff = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)

    USERNAME_FIELD = 'username'
    REQUIRED_FIELDS = ['email']

    objects = UserManager()

    def __str__(self):
        return self.username

class Plan(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='plans')
    date_created = models.DateTimeField(auto_now_add=True)

    # "Снимок" профиля на момент создания плана
    goal_snapshot = models.CharField(max_length=15, null=True, blank=True)
    age_snapshot = models.IntegerField(null=True, blank=True)
    weight_snapshot = models.FloatField(null=True, blank=True)
    height_snapshot = models.FloatField(null=True, blank=True)
    training_level_snapshot = models.CharField(max_length=10, null=True, blank=True)

    # КБЖУ и рекомендации
    calories = models.FloatField(null=True, blank=True)
    macros = models.JSONField(null=True, blank=True)
    training_recommendations = models.JSONField(null=True, blank=True)

    def __str__(self):
        return f"План от {self.date_created:%d.%m.%Y} для {self.user.username}"

class Workout(models.Model):
    """
    Отдельная модель для каждой тренировки,
    связанная с конкретным планом через ForeignKey.
    """
    plan = models.ForeignKey(
        Plan,
        on_delete=models.CASCADE,
        related_name='workouts'
    )
    name = models.CharField(
        max_length=255,
        help_text='Название упражнения или тренировки'
    )

    class Meta:
        verbose_name = 'Тренировка в плане'
        verbose_name_plural = 'Тренировки в плане'
        ordering = ['id']

    def __str__(self):
        return f"{self.name} (план {self.plan.id})"

class RecommendationTemplate(models.Model):
    GENDER_CHOICES = [('male', 'Мужчина'), ('female', 'Женщина')]
    AGE_CATEGORY_CHOICES = [
        ('10-18', '10-18 лет'),
        ('19-30', '19-30 лет'),
        ('31-59', '31-59 лет'),
        ('60+',   '60+ лет'),
    ]
    GOAL_CHOICES = [
        ('gain_weight', 'Набор массы'),
        ('maintain',    'Поддержание'),
        ('lose_weight', 'Похудение'),
    ]

    gender       = models.CharField(max_length=6, choices=GENDER_CHOICES)
    age_category = models.CharField(max_length=5, choices=AGE_CATEGORY_CHOICES)
    goal         = models.CharField(max_length=12, choices=GOAL_CHOICES)
    description  = models.TextField(help_text='Описание рекомендаций')

    class Meta:
        unique_together = ('gender', 'age_category', 'goal')
        verbose_name = 'Шаблон рекомендаций'
        verbose_name_plural = 'Шаблоны рекомендаций'

class WorkoutTemplate(models.Model):
    recommendation = models.ForeignKey(
        RecommendationTemplate,
        on_delete=models.CASCADE,
        related_name='workouts'
    )
    name = models.CharField(max_length=255, help_text='Упражнение шаблона')

    class Meta:
        ordering = ['id']
        verbose_name = 'Упражнение шаблона'
        verbose_name_plural = 'Упражнения шаблона'