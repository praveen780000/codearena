from django.contrib import messages
from django.contrib.auth import authenticate, login as auth_login, logout as auth_logout
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect

from .forms import RegisterForm
from interviews.models import Room
from questions.models import Question
from submissions.models import Submission


def register_view(request):
    if request.user.is_authenticated:
        return redirect('dashboard')
    if request.method == 'POST':
        form = RegisterForm(request.POST)
        if form.is_valid():
            user = form.save()
            auth_login(request, user)
            messages.success(request, "Account created. Welcome to CodeArena!")
            return redirect('dashboard')
    else:
        form = RegisterForm()
    return render(request, 'accounts/register.html', {'form': form})


def login_view(request):
    if request.user.is_authenticated:
        return redirect('dashboard')
    if request.method == 'POST':
        username = request.POST.get('username', '')
        password = request.POST.get('password', '')
        user = authenticate(request, username=username, password=password)
        if user is not None:
            auth_login(request, user)
            return redirect('dashboard')
        messages.error(request, "Invalid username or password.")
    return render(request, 'accounts/login.html')


def logout_view(request):
    auth_logout(request)
    messages.success(request, "Logged out.")
    return redirect('login')


@login_required
def dashboard_view(request):
    if request.user.role == 'interviewer':
        rooms = Room.objects.filter(created_by=request.user)
        return render(request, 'accounts/dashboard_interviewer.html', {'rooms': rooms})
    else:
        questions = Question.objects.all()
        recent_submissions = Submission.objects.filter(user=request.user)[:10]
        return render(request, 'accounts/dashboard_student.html', {
            'questions': questions,
            'recent_submissions': recent_submissions,
        })
