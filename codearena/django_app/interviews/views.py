from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect, get_object_or_404

from .forms import CreateRoomForm
from .models import Room
from submissions.models import Submission
from submissions.services import judge_code, JudgeServiceError


@login_required
def create_room_view(request):
    if request.user.role != 'interviewer':
        messages.error(request, "Only interviewers can create rooms.")
        return redirect('dashboard')

    if request.method == 'POST':
        form = CreateRoomForm(request.POST)
        if form.is_valid():
            room = form.save(commit=False)
            room.created_by = request.user
            room.save()
            messages.success(request, f"Room created! Share this code with your candidate: {room.room_code}")
            return redirect('room_detail', room_code=room.room_code)
    else:
        form = CreateRoomForm()

    return render(request, 'interviews/create_room.html', {'form': form})


@login_required
def join_room_view(request):
    if request.method == 'POST':
        code = request.POST.get('room_code', '').strip().upper()
        room = Room.objects.filter(room_code=code).first()
        if room:
            return redirect('room_detail', room_code=room.room_code)
        messages.error(request, "No room found with that code.")
    return render(request, 'interviews/join_room.html')


@login_required
def room_detail_view(request, room_code):
    room = get_object_or_404(Room, room_code=room_code)
    question = room.question
    submissions = Submission.objects.filter(room=room, user=request.user)

    if request.method == 'POST':
        if not question:
            messages.error(request, "This room has no question assigned yet.")
            return redirect('room_detail', room_code=room.room_code)

        code = request.POST.get('code', '')
        other_subs_qs = Submission.objects.filter(question=question).exclude(user=request.user)[:50]
        other_submissions = [{"username": s.user.username, "code": s.code} for s in other_subs_qs]

        try:
            result = judge_code(code, question.sample_input, question.sample_output, other_submissions)
        except JudgeServiceError as exc:
            messages.error(request, f"Could not reach the judge service: {exc}")
            return redirect('room_detail', room_code=room.room_code)

        Submission.objects.create(
            user=request.user, question=question, room=room, code=code,
            output=result.get('output', ''), status=result.get('status', 'Error'),
            similarity_score=result.get('similarity_score', 0.0),
            most_similar_user=result.get('most_similar_user') or '',
        )
        return redirect('room_detail', room_code=room.room_code)

    return render(request, 'interviews/room_detail.html', {
        'room': room,
        'question': question,
        'submissions': submissions,
    })
