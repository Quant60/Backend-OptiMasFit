
from rest_framework import serializers
from .models import Plan, User
from .models import Workout
from .models import RecommendationTemplate, WorkoutTemplate


class LoginRequestSerializer(serializers.Serializer):
    username = serializers.CharField()
    password = serializers.CharField()

class LoginResponseSerializer(serializers.Serializer):
    token = serializers.CharField()
    username = serializers.CharField()

class RegisterRequestSerializer(serializers.Serializer):
    username       = serializers.CharField(max_length=150)
    email          = serializers.EmailField()
    password1      = serializers.CharField(write_only=True)
    password2      = serializers.CharField(write_only=True)
    age            = serializers.IntegerField()
    height         = serializers.FloatField()
    weight         = serializers.FloatField()
    gender         = serializers.ChoiceField(choices=["male", "female"])
    goal           = serializers.ChoiceField(choices=["lose_weight", "gain_weight", "maintain"])
    training_level = serializers.ChoiceField(choices=["1", "2-3", "4-5", "6+"])
    target_months  = serializers.ChoiceField(choices=[1, 3])

    def validate(self, data):
        if data["password1"] != data["password2"]:
            raise serializers.ValidationError("Пароли не совпадают")
        return data

class RegisterResponseSerializer(LoginResponseSerializer):
    pass


class CSRFResponseSerializer(serializers.Serializer):
    detail = serializers.CharField(default="CSRF cookie set")


class LogoutResponseSerializer(serializers.Serializer):
    status = serializers.CharField(default="logged out")



class ProfileUpdateRequestSerializer(serializers.Serializer):

    age            = serializers.IntegerField(required=False)
    height         = serializers.FloatField(required=False)
    weight         = serializers.FloatField(required=False)
    goal           = serializers.CharField(required=False)
    training_level = serializers.CharField(required=False)
    target_months = serializers.ChoiceField(choices=[1, 3], required=False)

class GenericStatusSerializer(serializers.Serializer):
    status = serializers.CharField()


class PlanShortSerializer(serializers.Serializer):
    class Meta:
        model = Plan
        fields = ("id", "date_created", "calories")

class PlansListSerializer(serializers.Serializer):
    plans = PlanShortSerializer(many=True)


class DashboardSerializer(serializers.Serializer):
    calories = serializers.FloatField()
    macros = serializers.DictField()
    training_description = serializers.CharField()
    workouts = serializers.ListField(child=serializers.CharField())
    age_category = serializers.CharField()
    training_level = serializers.CharField()
    plans_count = serializers.IntegerField()


class UsersListItemSerializer(serializers.Serializer):
    username = serializers.CharField()
    email    = serializers.EmailField()

class UsersListSerializer(serializers.Serializer):
    users = UsersListItemSerializer(many=True)




class AdminUserSerializer(serializers.ModelSerializer):
    """Полная информация для admin‑панели"""
    current_plan = serializers.SerializerMethodField()
    plan_history = PlanShortSerializer(source="plans", many=True)

    class Meta:
        model  = User
        fields = (
            "username", "email",
            "age", "goal", "training_level",
            "current_plan", "plan_history",
        )


    def get_current_plan(self, obj):
        plan = obj.plans.order_by("-date_created").first()
        return PlanShortSerializer(plan).data if plan else None


class WorkoutSerializer(serializers.ModelSerializer):
    class Meta:
        model = Workout
        fields = ['id', 'plan', 'name']
        read_only_fields = ['id', 'plan']

class PlanSerializer(serializers.ModelSerializer):
    class Meta:
        model = Plan
        fields = [
            'id', 'user', 'date_created',
            'goal_snapshot','age_snapshot','height_snapshot','weight_snapshot',
            'training_level_snapshot','calories','macros'
        ]
        read_only_fields = ['id','date_created','user']

class WorkoutTemplateSerializer(serializers.ModelSerializer):
    class Meta:
        model = WorkoutTemplate
        fields = ['id', 'name']
        read_only_fields = ['id']

class RecommendationTemplateSerializer(serializers.ModelSerializer):
    workouts = WorkoutTemplateSerializer(many=True)

    class Meta:
        model = RecommendationTemplate
        fields = [
            'id',
            'gender',
            'age_category',
            'goal',
            'description',
            'workouts'
        ]
        read_only_fields = ['id']

    def create(self, validated_data):
        workouts_data = validated_data.pop('workouts')
        rec = RecommendationTemplate.objects.create(**validated_data)
        for w in workouts_data:
            WorkoutTemplate.objects.create(recommendation=rec, **w)
        return rec

    def update(self, instance, validated_data):
        workouts_data = validated_data.pop('workouts', [])

        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()
        # полностью пересоздаём упражнения
        instance.workouts.all().delete()
        for w in workouts_data:
            WorkoutTemplate.objects.create(recommendation=instance, **w)
        return instance

class RegisterDetailSerializer(serializers.ModelSerializer):
    password_hash = serializers.CharField(source='password', read_only=True)

    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'age', 'height', 'weight',
                  'gender', 'goal', 'training_level', 'target_months',
                  'date_joined', 'password_hash']
        read_only_fields = fields

class PlanListItemSerializer(serializers.ModelSerializer):
    """Список планов пользователя с КБЖУ и рекомендациями"""
    class Meta:
        model = Plan
        fields = [
            'id',
            'date_created',
            'goal_snapshot',
            'age_snapshot',
            'height_snapshot',
            'weight_snapshot',
            'training_level_snapshot',
            'calories',
            'macros',
            'training_recommendations',
        ]
        read_only_fields = fields

class PlansListSerializer(serializers.Serializer):
    plans = PlanListItemSerializer(many=True)