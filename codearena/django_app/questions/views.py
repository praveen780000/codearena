from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect, get_object_or_404

from .models import Question
from submissions.models import Submission
from submissions.services import judge_code, JudgeServiceError


@login_required
def question_list_view(request):
    questions = Question.objects.all()
    return render(request, 'questions/question_list.html', {'questions': questions})


@login_required
def practice_view(request, question_id):
    question = get_object_or_404(Question, id=question_id)
    submissions = Submission.objects.filter(question=question, user=request.user, room__isnull=True)

    if request.method == 'POST':
        if request.user.role != 'student':
            messages.error(request, "Only students can submit practice solutions.")
            return redirect('practice', question_id=question.id)

        code = request.POST.get('code', '')
        other_subs_qs = Submission.objects.filter(question=question).exclude(user=request.user)[:50]
        other_submissions = [{"username": s.user.username, "code": s.code} for s in other_subs_qs]

        try:
            result = judge_code(code, question.sample_input, question.sample_output, other_submissions)
        except JudgeServiceError as exc:
            messages.error(request, f"Could not reach the judge service: {exc}")
            return redirect('practice', question_id=question.id)

        Submission.objects.create(
            user=request.user, question=question, room=None, code=code,
            output=result.get('output', ''), status=result.get('status', 'Error'),
            similarity_score=result.get('similarity_score', 0.0),
            most_similar_user=result.get('most_similar_user') or '',
        )
        return redirect('practice', question_id=question.id)

    return render(request, 'questions/practice.html', {
        'question': question,
        'submissions': submissions,
    })
