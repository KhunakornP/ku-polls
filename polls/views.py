from django.urls import reverse
# from django.contrib.messages.views import
from django.db.models import F
from django.http import HttpResponseRedirect
from django.shortcuts import render, get_object_or_404
from django.views import generic
from django.utils import timezone
from .models import Choice, Question


class IndexView(generic.ListView):
    template_name = "polls/index.html"
    context_object_name = "latest_question_list"

    def get_queryset(self):
        """Returns the last 5 published questions"""
        return Question.objects.filter(
            pub_date__lte=timezone.now()).order_by("-pub_date")[:5]


class DetailView(generic.DetailView):
    model = Question
    template_name = "polls/detail.html"

    def get_queryset(self):
        """Only return questions that are currently published"""
        return Question.objects.filter(pub_date__lte=timezone.now())

    def get(self, request, *args, **kwargs):
        """
        Override the get() method and checks if the poll is valid to access
        """
        try:
            Question.objects.get(pk=kwargs['pk'])
        except Question.DoesNotExist:
            return HttpResponseRedirect(reverse("polls:index"))
        question = Question.objects.get(pk=kwargs['pk'])
        if not question.is_published():
            return HttpResponseRedirect(reverse("polls:index"))
        return super().get(request, *args, **kwargs)


class ResultsView(generic.DetailView):
    model = Question
    template_name = "polls/results.html"

    def get(self, request, *args, **kwargs):
        """
        Override the get() method checks if
        the poll's result is valid to access
        """
        try:
            Question.objects.get(pk=kwargs['pk'])
        except Question.DoesNotExist:
            return HttpResponseRedirect(reverse("polls:index"))
        question = Question.objects.get(pk=kwargs['pk'])
        if not question.is_published():
            return HttpResponseRedirect(reverse("polls:index"))
        return super().get(request, *args, **kwargs)


def vote(request, question_id):
    """Handler for submitting a vote"""
    question = get_object_or_404(Question, pk=question_id)
    try:
        selected_choice = question.choice_set.get(pk=request.POST['choice'])
    except (KeyError, Choice.DoesNotExist):
        return render(request,
                      "polls/detail.html",
                      {
                          "question": question,
                          "error_message": "You didn't select a choice."
                      })
    else:
        selected_choice.votes = F("votes") + 1
        selected_choice.save()
        return HttpResponseRedirect(
            reverse("polls:results", args=(question_id,)))
