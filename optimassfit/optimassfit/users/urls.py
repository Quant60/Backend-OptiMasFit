from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('register/', views.register_view, name='register'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('dashboard/', views.user_dashboard, name='user_dashboard'),
    path('profile/update/', views.profile_update_view, name='profile_update'),
    path('plan/<int:plan_id>/', views.user_plan_view, name='user_plan'),
    path('admin/dashboard/', views.custom_admin_dashboard, name='custom_admin_dashboard'),
    path('admin/delete/<int:user_id>/', views.admin_delete_user, name='admin_delete_user'),
]
