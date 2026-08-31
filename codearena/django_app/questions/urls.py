from django.urls import path
from . import views

urlpatterns = [
    path('', views.question_list_view, name='question_list'),
    path('<int:question_id>/practice/', views.practice_view, name='practice'),
]
