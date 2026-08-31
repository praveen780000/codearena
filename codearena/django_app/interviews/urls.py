from django.urls import path
from . import views

urlpatterns = [
    path('create/', views.create_room_view, name='create_room'),
    path('join/', views.join_room_view, name='join_room'),
    path('<str:room_code>/', views.room_detail_view, name='room_detail'),
]
