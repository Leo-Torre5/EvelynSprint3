from django.urls import path
from .views import UserListView, UserCreateView, UserUpdateView, UserDeleteView
from django.contrib import admin

urlpatterns = [
    path('users/', UserListView.as_view(), name='user_list'),
    path('user/add/', UserCreateView.as_view(), name='user_add'),
    path('user/<int:pk>/', UserUpdateView.as_view(), name='user_update'),
    path('user/<int:pk>/delete/', UserDeleteView.as_view(), name='user_delete'),
]
