from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import AuthenticationForm
from .forms import RegisterForm, ProfileUpdateForm
from .models import User, Plan
from .utils import calculate_calories, calculate_macros, get_age_category, get_training_recommendations


def index(request):
    return render(request, 'index.html')


def login_view(request):
    if request.method == 'POST':
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            login(request, form.get_user())
            return redirect('user_dashboard')
    else:
        form = AuthenticationForm()
    return render(request, 'login.html', {'form': form})


def register_view(request):
    if request.method == 'POST':
        form = RegisterForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect('user_dashboard')
    else:
        form = RegisterForm()
    return render(request, 'register.html', {'form': form})

@login_required
def logout_view(request):
    logout(request)
    return redirect('index')

@login_required
def user_dashboard(request):
    user = request.user
    age_cat = get_age_category(user.age)
    calories = calculate_calories(user, user.training_level)
    macros = calculate_macros(user.weight, age_cat, user.goal, user.gender)
    recs = get_training_recommendations(user.gender, age_cat, user.goal)
    history = user.plans.all().order_by('-date_created')
    return render(request, 'dashboard.html', {
        'user': user,
        'calories': calories,
        'macros': macros,
        'training_recommendations': recs,
        'plan_history': history
    })

@login_required
def profile_update_view(request):
    user = request.user
    if request.method == 'POST':
        form = ProfileUpdateForm(request.POST, instance=user)
        if form.is_valid():
            form.save()
            age_cat = get_age_category(user.age)
            calories = calculate_calories(user, user.training_level)
            macros = calculate_macros(user.weight, age_cat, user.goal, user.gender)
            recs = get_training_recommendations(user.gender, age_cat, user.goal)
            Plan.objects.create(
                user=user,
                goal_snapshot=user.goal,
                age_snapshot=user.age,
                height_snapshot=user.height,
                weight_snapshot=user.weight,
                training_level_snapshot=user.training_level,
                calories=calories,
                macros=macros,
                training_recommendations=recs
            )
            return redirect('user_dashboard')
    else:
        form = ProfileUpdateForm(instance=user)
    return render(request, 'profile_update.html', {'form': form})

@login_required
def user_plan_view(request, plan_id):
    plan = get_object_or_404(Plan, id=plan_id)
    age_cat = get_age_category(plan.age_snapshot or request.user.age)
    recs = plan.training_recommendations or get_training_recommendations(plan.user.gender, age_cat, plan.goal_snapshot)
    return render(request, 'user_plan.html', {'plan': plan, 'training_recommendations': recs})

@login_required
def custom_admin_dashboard(request):
    if not request.user.is_staff:
        return redirect('user_dashboard')
    users = User.objects.all().order_by('username')
    return render(request, 'custom_admin_dashboard.html', {'users': users})

@login_required
def admin_delete_user(request, user_id):
    if not request.user.is_staff:
        return redirect('custom_admin_dashboard')
    get_object_or_404(User, id=user_id).delete()
    return redirect('custom_admin_dashboard')
