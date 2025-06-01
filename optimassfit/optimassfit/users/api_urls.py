from django.urls import path, include
from rest_framework.authtoken.views import obtain_auth_token
from rest_framework_nested import routers
from drf_spectacular.views import SpectacularAPIView, SpectacularSwaggerView
from . import api_views


router = routers.SimpleRouter()
router.register(r'admin/templates', api_views.RecommendationTemplateViewSet, basename='rec-template')
router.register(r'admin/plans', api_views.PlanViewSet, basename='admin-plan')


plans_router = routers.NestedSimpleRouter(router, r'admin/plans', lookup='plan')
plans_router.register(r'workouts', api_views.WorkoutViewSet, basename='plan-workouts')

urlpatterns = [

    # Public endpoints
    path('', api_views.api_index),
    path('csrf/', api_views.api_get_csrf),
    path('register/', api_views.api_register),
    path('login/', api_views.api_login),
    path('token/', api_views.CustomObtainAuthToken.as_view()),
    path('logout/', api_views.api_logout),

    # User profile & plans
    path('dashboard/', api_views.api_user_dashboard),
    path('plans/', api_views.api_user_plans),
    path('profile/update/', api_views.api_profile_update),
    path('profile/update_snapshot/', api_views.api_update_snapshot),

    # Admin functional endpoints
    path('admin/dashboard/', api_views.api_custom_admin_dashboard),
    path('',              api_views.api_index),
    path('csrf/',         api_views.api_get_csrf),
    path('register/',     api_views.api_register),
    path('login/',        api_views.api_login),
    path('token/',        obtain_auth_token),
    path('logout/',       api_views.api_logout),


    path('dashboard/',    api_views.api_user_dashboard),
    path('plans/',        api_views.api_user_plans),
    path('profile/update/',          api_views.api_profile_update),
    path('profile/update_snapshot/', api_views.api_update_snapshot),

    path('admin/dashboard/',          api_views.api_custom_admin_dashboard),
    path('admin/users/<int:user_id>/', api_views.api_admin_delete_user),
    path('', include(router.urls)),
    path('', include(plans_router.urls)),

    # OpenAPI + Swagger UI
    path('schema/', api_views.CustomSpectacularAPIView.as_view(), name='schema'),

    path('schema/',  SpectacularAPIView.as_view(),   name='schema'),
    path('swagger/', SpectacularSwaggerView.as_view(url_name='schema'), name='swagger-ui'),
]
