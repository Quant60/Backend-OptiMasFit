from django.contrib import admin, messages
from django.utils.translation import ngettext
from .models import Plan, User

# ───── PlanAdmin ─────
@admin.register(Plan)
class PlanAdmin(admin.ModelAdmin):
    list_display   = ['user', 'date_created', 'calories']
    search_fields  = ['user__username']
    list_filter    = ['date_created', 'user']
    # стандартный экшен «Delete selected Plan» уже присутствует


# ───── UserAdmin ─────
@admin.action(description='Удалить все планы выбранных пользователей')
def delete_all_plans(modeladmin, request, queryset):
    total_plans = 0
    for user in queryset:
        cnt = user.plans.count()
        user.plans.all().delete()
        total_plans += cnt

    modeladmin.message_user(
        request,
        ngettext(
            'Удалён %(count)d план.',
            'Удалено %(count)d планов.',
            total_plans
        ) % {'count': total_plans},
        level=messages.SUCCESS
    )

@admin.action(description='Удалить пользователей и все их планы')
def delete_users_and_plans(modeladmin, request, queryset):
    total_users = queryset.count()
    total_plans = sum(u.plans.count() for u in queryset)
    # сначала удаляем планы
    for user in queryset:
        user.plans.all().delete()
    # потом самих пользователей
    deleted, _ = queryset.delete()

    modeladmin.message_user(
        request,
        ngettext(
            'Удалён %(users)d пользователь и %(plans)d план.',
            'Удалено %(users)d пользователей и %(plans)d планов.',
            total_users
        ) % {'users': total_users, 'plans': total_plans},
        level=messages.SUCCESS
    )

@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    list_display   = [
        'username', 'email',
        'age', 'height', 'weight',
        'goal', 'training_level', 'target_months'
    ]
    search_fields  = ['username', 'email']
    list_filter    = ['goal', 'training_level']
    actions        = [
        delete_all_plans,
        delete_users_and_plans,
    ]
