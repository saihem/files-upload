from django.urls import path
from . import views

app_name = 'core'
urlpatterns = [
    path('home/', views.HomeView.as_view(), name='home'),
    path('login/', views.LoginView.as_view(), name='login'),
]
