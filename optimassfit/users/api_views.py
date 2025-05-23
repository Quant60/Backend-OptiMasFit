from rest_framework.decorators import api_view, authentication_classes, permission_classes
from rest_framework.authentication import TokenAuthentication
from rest_framework.permissions import IsAuthenticated, IsAdminUser, AllowAny
from rest_framework.authtoken.models import Token
from django.views.decorators.csrf import ensure_csrf_cookie
from django.shortcuts import get_object_or_404
from django.http import JsonResponse
from django.contrib.auth import login, logout, authenticate
from .forms import RegisterForm, ProfileUpdateForm
from .models import User, Plan, Workout, RecommendationTemplate, WorkoutTemplate
from .utils import calculate_calories, calculate_macros, get_age_category, get_training_recommendations
from drf_spectacular.utils import (
    extend_schema, OpenApiResponse, OpenApiTypes, OpenApiExample)
from .serializers import (
    LoginRequestSerializer, LoginResponseSerializer,
    RegisterRequestSerializer, RegisterResponseSerializer,
    CSRFResponseSerializer, LogoutResponseSerializer,
    ProfileUpdateRequestSerializer, GenericStatusSerializer,
    DashboardSerializer, PlansListSerializer,
    UsersListSerializer, AdminUserSerializer, WorkoutSerializer,
    PlanSerializer,RecommendationTemplateSerializer, RegisterDetailSerializer )
from drf_spectacular.utils import extend_schema_view, extend_schema
from rest_framework.authtoken.views import ObtainAuthToken
from rest_framework.response import Response
from rest_framework import viewsets
from django.db import IntegrityError
from rest_framework import status


@extend_schema_view(
    post=extend_schema(
        tags=["Auth"],
        request=LoginRequestSerializer,
        responses=LoginResponseSerializer,
    )
)
class TokenView(ObtainAuthToken):
    pass

@extend_schema(
    examples=[
        OpenApiExample(
            name="Cookie set",
            value={"detail": "CSRF cookie set"},
            response_only=True,
            status_codes=[200],
        )
    ]
)
@ensure_csrf_cookie
@ensure_csrf_cookie
@api_view(['GET'])
@permission_classes([AllowAny])
def api_get_csrf(request):
    """Установка CSRF-cookie для клиента"""
    return JsonResponse({'detail': 'CSRF cookie set'})

@extend_schema(
    tags=["Auth"],
    request=RegisterRequestSerializer,
    responses={
        201: OpenApiResponse(
            response=RegisterResponseSerializer,
            description="Created",
            examples=[
                OpenApiExample(
                    "Пример ответа с данными пользователя",
                    value={
                        "token": "0123456789abcdef",
                        "user": {
                            "id": 5,
                            "username": "user1",
                            "email": "user@example.com",
                            "age": 25,
                            "height": 190.0,
                            "weight": 80.0,
                            "gender": "male",
                            "goal": "lose_weight",
                            "training_level": "2-3",
                            "target_months": 3,
                            "date_joined": "2025-05-08T12:34:56Z",
                            "password_hash": "pbkdf2_sha256$260000$..."
                        }
                    }
                )
            ]
        ),
        400: OpenApiResponse(description="Invalid form")
    }
)
@api_view(['POST'])
@authentication_classes([])
@permission_classes([AllowAny])
def api_register(request):
    """Регистрация нового пользователя, возвращает токен и данные юзера (с хешем пароля)"""
    form = RegisterForm(request.data)
    if form.is_valid():
        user = form.save()
        login(request, user)
        token, _ = Token.objects.get_or_create(user=user)
        user_data = RegisterDetailSerializer(user).data
        return JsonResponse({'token': token.key, 'user': user_data}, status=201)
    return JsonResponse({'errors': form.errors}, status=400)

@extend_schema(
    tags=["Auth"],
    request=LoginRequestSerializer,
    responses={
        200: LoginResponseSerializer,
        400: OpenApiResponse(description="Invalid credentials")
    },
)
@api_view(['POST'])
@permission_classes([AllowAny])
def api_login(request):

    username = request.data.get('username')
    password = request.data.get('password')

    user = authenticate(username=username, password=password)
    if not user:
        return JsonResponse({'error': 'Invalid credentials'}, status=400)

    login(request, user)
    token, _ = Token.objects.get_or_create(user=user)

    return JsonResponse({
        'token': token.key,
        'username': user.username,
        'password_hash': user.password,
    })

@extend_schema(
    tags=["Profile"],
    request=ProfileUpdateRequestSerializer,
    responses={
        200: GenericStatusSerializer,
        400: OpenApiResponse(description="Invalid form")
    },
    examples=[
        OpenApiExample(
            name="Пример обновления профиля",
            summary="Частичное обновление данных пользователя",
            value={
                "age": 28,
                "height": 199.0,
                "weight": 110.0,
                "goal": "gain_weight",
                "training_level": "1",
                "target_months": 3
            },
            request_only=True
        )
    ]
)
@api_view(['POST'])
@authentication_classes([TokenAuthentication])
@permission_classes([IsAuthenticated])
def api_profile_update(request):
    """Обновление профиля и создание нового снимка плана"""
    user = request.user
    form = ProfileUpdateForm(request.data, instance=user)
    if not form.is_valid():
        return JsonResponse({'error': 'Invalid form'}, status=400)

    form.save()
    user.refresh_from_db()

    # расчёт
    age_cat  = get_age_category(user.age)
    calories = calculate_calories(user, user.training_level)
    macros   = calculate_macros(user.weight, age_cat, user.goal, user.gender)

    # ищем шаблон/фолбэк
    try:
        tpl = RecommendationTemplate.objects.get(
            gender=user.gender,
            age_category=age_cat,
            goal=user.goal
        )
        description = tpl.description
        workouts    = [wt.name for wt in tpl.workouts.all()]
    except RecommendationTemplate.DoesNotExist:
        rec = get_training_recommendations(user.gender, age_cat, user.goal)
        description = rec.get('description', '')
        workouts    = rec.get('workouts', [])

    # создаём план
    plan = Plan.objects.create(
        user=user,
        goal_snapshot=user.goal,
        age_snapshot=user.age,
        height_snapshot=user.height,
        weight_snapshot=user.weight,
        training_level_snapshot=user.training_level,
        calories=calories,
        macros=macros,
        training_recommendations=description
    )
    # сохраняем тренировки
    for name in workouts:
        Workout.objects.create(plan=plan, name=name)

    # возвращаем статус + текущий снимок
    return JsonResponse({
        'status': 'updated',
        'plan': {
            'age':                  plan.age_snapshot,
            'weight':               plan.weight_snapshot,
            'height':               plan.height_snapshot,
            'goal':                 plan.goal_snapshot,
            'training_level':       plan.training_level_snapshot,
            'target_months':        user.target_months,        # если нужно
        }
    })


@extend_schema(
    tags=["Plans"],
    responses=DashboardSerializer
)
@api_view(['GET'])
@authentication_classes([TokenAuthentication])
@permission_classes([IsAuthenticated])
def api_user_dashboard(request):
    """Возвращает текущий план и информацию по питанию и тренировкам для авторизованного пользователя"""
    user = request.user
    plan_history = user.plans.all().order_by('-date_created')
    current = plan_history[0] if plan_history else None

    if current:
        calories = current.calories
        macros = current.macros
        # Описание рекомендаций, сохранённое при создании плана
        description = current.training_recommendations
        workouts = list(current.workouts.values_list('name', flat=True))
    else:
        age_cat = get_age_category(user.age)
        calories = calculate_calories(user, user.training_level)
        macros = calculate_macros(user.weight, age_cat, user.goal, user.gender)
        description = ''
        workouts = []

    return JsonResponse({
        'calories': calories,
        'macros': macros,
        'training_description': description,
        'workouts': workouts,
        'age_category': get_age_category(user.age),
        'training_level': user.training_level,
        'plans_count': plan_history.count()
    })


@extend_schema(tags=["Plans"], responses=PlansListSerializer)
@api_view(['GET'])
@authentication_classes([TokenAuthentication])
@permission_classes([IsAuthenticated])
def api_user_plans(request):
    user = request.user
    plans = user.plans.all().order_by('-date_created')
    serializer = PlansListSerializer({'plans': plans})

    return Response(serializer.data)


@extend_schema(tags=["Misc"], responses=OpenApiTypes.OBJECT)
@api_view(['GET'])
@permission_classes([AllowAny])
def api_index(request):
    """Точка входа в API"""
    return JsonResponse({'message': 'Welcome to OptiMassFit API'})

@extend_schema(tags=["Auth"], responses=LogoutResponseSerializer)
@api_view(['POST'])
@authentication_classes([TokenAuthentication])
@permission_classes([IsAuthenticated])
def api_logout(request):
    """Выход пользователя из сессии API"""
    logout(request)
    return JsonResponse({'status': 'logged out'})

@extend_schema(
    tags=["Admin"],
    responses={200: AdminUserSerializer(many=True)},
)
@api_view(['GET'])
@authentication_classes([TokenAuthentication])
@permission_classes([IsAuthenticated, IsAdminUser])
def api_custom_admin_dashboard(request):
    """Список всех пользователей для админа"""
    qs = User.objects.prefetch_related("plans").order_by("username")
    return Response(AdminUserSerializer(qs, many=True).data)

@extend_schema(tags=["Admin"], responses=GenericStatusSerializer)
@api_view(['DELETE'])
@authentication_classes([TokenAuthentication])
@permission_classes([IsAuthenticated, IsAdminUser])
def api_admin_delete_user(request, user_id):
    """Удаление пользователя (только админ)"""
    u = get_object_or_404(User, id=user_id)
    u.delete()
    return JsonResponse({'status': 'deleted'})



@extend_schema(
    tags=["Profile"],
    request=ProfileUpdateRequestSerializer,
    responses={"200": GenericStatusSerializer},
)
@api_view(['PUT'])
@authentication_classes([TokenAuthentication])
@permission_classes([IsAuthenticated])
def api_update_snapshot(request):
    """Обновление отдельных полей профиля и создание нового снимка плана"""
    user = request.user
    # Обновляем профиль
    for field in ['age', 'height', 'weight', 'goal', 'training_level', 'target_months']:
        if field in request.data:
            setattr(user, field, request.data[field])
    user.save()

    # Расчёт параметров
    age_cat = get_age_category(user.age)
    calories = calculate_calories(user, user.training_level)
    macros = calculate_macros(user.weight, age_cat, user.goal, user.gender)

    # Получаем шаблон рекомендаций
    tpl = RecommendationTemplate.objects.get(
        gender=user.gender,
        age_category=age_cat,
        goal=user.goal
    )

    # Создаём новый план
    plan = Plan.objects.create(
        user=user,
        goal_snapshot=user.goal,
        age_snapshot=user.age,
        height_snapshot=user.height,
        weight_snapshot=user.weight,
        training_level_snapshot=user.training_level,
        calories=calories,
        macros=macros,
        training_recommendations=tpl.description
    )

    # Создаём Workout-записи
    for wt in tpl.workouts.all():
        Workout.objects.create(plan=plan, name=wt.name)

    return JsonResponse({'new_plan_id': plan.id})

@extend_schema(
    tags=["Admin"],
    request=WorkoutSerializer,
    responses=WorkoutSerializer,
    examples=[
        OpenApiExample(
            "Пример создания тренировки",
            summary="POST /api/admin/plans/{plan_pk}/workouts/",
            value={"name": "Yoga"},
            request_only=True
        )
    ]
)
class WorkoutViewSet(viewsets.ModelViewSet):
    """
    CRUD для Workout в рамках плана (Admin only).
    """
    serializer_class = WorkoutSerializer
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated, IsAdminUser]

    def get_queryset(self):
        return Workout.objects.filter(plan_id=self.kwargs["plan_pk"])

    def perform_create(self, serializer):
        # Привязываем к плану из URL
        serializer.save(plan_id=self.kwargs['plan_pk'])

@extend_schema_view(
    list=extend_schema(
        tags=["Admin"],
        description="Список всех планов (только для админа)",
        responses=PlanSerializer(many=True),
    ),
    create=extend_schema(
        tags=["Admin"],
        request=PlanSerializer,
        responses=PlanSerializer,
        examples=[
            OpenApiExample(
                "План: Похудение, уровень 1",
                summary="Lose weight, level 1",
                value={
                    "user": 5,
                    "goal_snapshot": "lose_weight",
                    "age_snapshot": 30,
                    "height_snapshot": 180.0,
                    "weight_snapshot": 75.0,
                    "training_level_snapshot": "1",
                    "calories": 1800,
                    "macros": {"protein": 120, "fat": 60, "carbs": 200}
                },
                request_only=True
            ),
            OpenApiExample(
                "План: Набор массы, уровень 2-3",
                summary="Gain weight, level 2-3",
                value={
                    "user": 5,
                    "goal_snapshot": "gain_weight",
                    "age_snapshot": 25,
                    "height_snapshot": 175.0,
                    "weight_snapshot": 68.0,
                    "training_level_snapshot": "2-3",
                    "calories": 2600,
                    "macros": {"protein": 140, "fat": 80, "carbs": 300}
                },
                request_only=True
            ),
            OpenApiExample(
                "План: Поддержание, уровень 4-5",
                summary="Maintain, level 4-5",
                value={
                    "user": 5,
                    "goal_snapshot": "maintain",
                    "age_snapshot": 40,
                    "height_snapshot": 170.0,
                    "weight_snapshot": 70.0,
                    "training_level_snapshot": "4-5",
                    "calories": 2200,
                    "macros": {"protein": 130, "fat": 70, "carbs": 250}
                },
                request_only=True
            ),
        ]
    ),
    retrieve=extend_schema(
        tags=["Admin"],
        description="Получить один план по ID",
        responses=PlanSerializer
    ),
    update=extend_schema(
        tags=["Admin"],
        request=PlanSerializer,
        responses=PlanSerializer
    ),
    partial_update=extend_schema(
        tags=["Admin"],
        request=PlanSerializer,
        responses=PlanSerializer
    ),
    destroy=extend_schema(
        tags=["Admin"],
        description="Удалить план по ID",
        responses={204: None}
    ),
)
class PlanViewSet(viewsets.ModelViewSet):
    """
    CRUD для Plan (только для админа).
    """
    queryset = Plan.objects.all()
    serializer_class = PlanSerializer
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated, IsAdminUser]

    def perform_create(self, serializer):
        # Берём user из поля запроса и привязываем его к создаваемому плану
        user_id = self.request.data.get('user')
        user = get_object_or_404(User, pk=user_id)
        serializer.save(user=user)

@extend_schema_view(
    list=extend_schema(tags=["Admin"]),
    retrieve=extend_schema(tags=["Admin"]),
    create=extend_schema(tags=["Admin"]),
    update=extend_schema(tags=["Admin"]),
    partial_update=extend_schema(tags=["Admin"]),
    destroy=extend_schema(tags=["Admin"]),
)
class RecommendationTemplateViewSet(viewsets.ModelViewSet):
    """
    CRUD для шаблонов рекомендаций (Admin only).
    При POST, если шаблон с такими полями уже есть,
    просто добавляем к нему новые упражнения.
    """
    queryset = RecommendationTemplate.objects.all()
    serializer_class = RecommendationTemplateSerializer
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated, IsAdminUser]

    def create(self, request, *args, **kwargs):
        data = request.data.copy()
        workouts = data.pop('workouts', [])
        gender = data.get('gender')
        age_cat = data.get('age_category')
        goal    = data.get('goal')

        # 1) Попробуем найти уже существующий шаблон
        tpl = RecommendationTemplate.objects.filter(
            gender=gender,
            age_category=age_cat,
            goal=goal
        ).first()

        if tpl:
            # 2) Добавляем к нему новые упражнения
            created_names = set(tpl.workouts.values_list('name', flat=True))
            for w in workouts:
                name = w.get('name')
                if name and name not in created_names:
                    WorkoutTemplate.objects.create(recommendation=tpl, name=name)
            # 3) Вернём обновленный объект
            serializer = self.get_serializer(tpl)
            return Response(serializer.data, status=status.HTTP_200_OK)

        # 4) Если не нашли – создаём как обычно
        try:
            return super().create(request, *args, **kwargs)
        except IntegrityError:
            # на всякий случай, если unique всё же пропустил
            return Response(
                {"detail": "Unable to create or update template."},
                status=status.HTTP_400_BAD_REQUEST
            )
