from django.urls import path
from . import views

app_name = 'core'
urlpatterns = [
    path('home/', views.HomeView.as_view(), name='home'),
    path('login/', views.LoginView.as_view(), name='login'),
    path('user/', views.UserView.as_view(), name='user'),
]
