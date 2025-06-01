from django.contrib import admin
from django.urls import include, path
from django.shortcuts import render

def home(request):                 # стартовая страница
    return render(request, 'index.html')

urlpatterns = [
    path('',        home,               name='home'),
    path('users/',  include('users.urls')),      # HTML
    path('api/',    include('users.api_urls')),  # JSON
    path('admin/',  admin.site.urls),
]
