from django.http import HttpResponse
from django.shortcuts import render, get_object_or_404
from .models import Question


def index(request):
    return HttpResponse("Welcome to KU-polls, you are currently "
                        "viewing all polls")


def detail(request, question_id):
    question = get_object_or_404(Question, pk=question_id)
    return render(request, "polls/detail.html", {"question": question})


def results(request, question_id):
    return HttpResponse(f"Showing results for question: {question_id}")


def vote(request, question_id):
    return HttpResponse(f"Your voting on question: {question_id}")


def index(request):
    latest_question_list = Question.objects.order_by("-pub_date")[:5]
    context = {
        "latest_question_list": latest_question_list
    }
    return render(request, "polls/index.html", context)
