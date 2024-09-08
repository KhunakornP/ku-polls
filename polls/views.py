import logging

from django.contrib.auth import (user_logged_in, user_logged_out,
                                 user_login_failed)
from django.contrib.auth import login, authenticate
from django.contrib.auth.forms import UserCreationForm
from django.dispatch import receiver
from django.urls import reverse
from django.contrib import messages
from django.http import HttpResponseRedirect
from django.shortcuts import render, get_object_or_404, redirect
from django.views import generic
from django.utils import timezone
from django.contrib.auth.decorators import login_required
from .models import Choice, Question, Vote

# get a logger instance for the polls app
logger = logging.getLogger(__name__)


class IndexView(generic.ListView):
    """
    View that displays the 5 most recent poll questions

    returns: A rendered template of the 5 most recent poll questions
    """
    template_name = "polls/index.html"
    context_object_name = "latest_question_list"

    def get_queryset(self):
        """Returns the last 5 published questions"""
        return Question.objects.filter(
            pub_date__lte=timezone.now()).order_by("-pub_date")[:5]


class DetailView(generic.DetailView):
    """
    View that displays the choices (details) of a poll question

    returns: A rendered template of the question's choices
    """
    model = Question
    template_name = "polls/detail.html"

    def get_queryset(self):
        """Only return questions that are currently published"""
        return Question.objects.filter(pub_date__lte=timezone.now())

    def get_context_data(self, **kwargs):
        """
        Override the get_context_data() method and check if the user
        has previously selected a choice.
        """
        context = super().get_context_data(**kwargs)
        # check if user is logged in
        if self.request.user.is_authenticated:
            # check if user had previously voted
            try:
                vote = Vote.objects.get(
                    user=self.request.user,
                    choice__question=self.question)
                context['prev_vote'] = vote.choice.id
                return context
            # user has not voted yet for this question
            except Vote.DoesNotExist:
                context['prev_vote'] = None
                return context
        return context

    def get(self, request, *args, **kwargs):
        """
        Override the get() method and checks if the poll is valid to access
        if the poll has ended redirect the user to the results page
        """
        try:
            self.question = Question.objects.get(pk=kwargs['pk'])
        # check if the poll exists
        except Question.DoesNotExist:
            logger.error(f"{request.user} tried to access a poll that does not"
                         f" exists. Poll PK: {kwargs['pk']}")
            messages.error(request, "Error: Poll was not found")
            return HttpResponseRedirect(reverse("polls:index"))
        question = Question.objects.get(pk=kwargs['pk'])
        # check of the poll is published
        if not question.is_published():
            logger.error(f"{request.user} tried to access an unpublished poll."
                         f"Poll PK:{kwargs['pk']}")
            messages.error(request, "Error: Poll was not found")
            return HttpResponseRedirect(reverse("polls:index"))
        if not question.can_vote():
            return HttpResponseRedirect("./results")
        return super().get(request, *args, **kwargs)


class ResultsView(generic.DetailView):
    """
    View that displays the results of a poll question

    returns: A rendered template of the poll's result
    """
    model = Question
    template_name = "polls/results.html"

    def get(self, request, *args, **kwargs):
        """
        Override the get() method checks if
        the poll's result is valid to access
        """
        try:
            Question.objects.get(pk=kwargs['pk'])
        # check if the poll exists
        except Question.DoesNotExist:
            logger.error(f"{request.user} tried to access a poll that does not"
                         f" exists. Poll PK: {kwargs['pk']}")
            messages.error(request, "Error: Poll was not found")
            return HttpResponseRedirect(reverse("polls:index"))
        question = Question.objects.get(pk=kwargs['pk'])
        # check if the poll is published
        if not question.is_published():
            logger.error(f"{request.user} tried to access an unpublished poll."
                         f"Poll PK:{kwargs['pk']}")
            messages.error(request, "Error: Poll was not found")
            return HttpResponseRedirect(reverse("polls:index"))
        return super().get(request, *args, **kwargs)


@login_required
def vote(request, question_id):
    """Handler for submitting a vote"""
    question = get_object_or_404(Question, pk=question_id)
    try:
        selected_choice = question.choice_set.get(pk=request.POST['choice'])
    except (KeyError, Choice.DoesNotExist):
        messages.error(request, "You didn't select a choice!, "
                                "please select a choice before voting.")
        logger.error(f"{request.user} tried to vote on an invalid choice in "
                     f"question {question_id}.) {question.question_text}")
        return HttpResponseRedirect(
            reverse("polls:detail", args=(question_id,)))
    try:
        vote = Vote.objects.get(user=request.user, choice__question=question)
        prev_choice = vote.choice
        vote.choice = selected_choice
        vote.save()
        messages.success(request,
                         f"Your vote has changed to '{selected_choice}' "
                         f"from '{prev_choice}'")
        logger.info(f"{request.user} changed their vote from "
                    f"'{prev_choice}' to '{selected_choice}' in "
                    f"question {question_id}.) {question.question_text}")
        return HttpResponseRedirect(
            reverse("polls:results", args=(question_id,)))
    except Vote.DoesNotExist:
        new_vote = Vote.objects.create(choice=selected_choice,
                                       user=request.user)
        new_vote.save()
        messages.success(request,
                         f"Your vote for '{selected_choice}' has been "
                         f"recorded")
        logger.info(f"{request.user} voted for '{selected_choice}' in "
                    f"question {question_id}.) {question.question_text}")
        return HttpResponseRedirect(
            reverse("polls:results", args=(question_id,)))


def register(request):
    """Handler for creating new users"""
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            form.save()
            username = form.cleaned_data.get('username')
            raw_passwd = form.cleaned_data.get('password1')
            user = authenticate(username=username, password=raw_passwd)
            login(request, user)
        return redirect('polls:index')
    else:
        form = UserCreationForm()
    return render(request, 'registration/register.html', {'form': form})


def get_client_ip(request):
    """Get the visitor’s IP address using request headers."""
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        ip = x_forwarded_for.split(',')[0]
    else:
        ip = request.META.get('REMOTE_ADDR')
    return ip


@receiver(user_logged_in)
def create_user_log_on_login(request, user, *args, **kwargs):
    """Logs the user and ip on a successful login"""
    client_ip = get_client_ip(request)
    logger.info(f"Login: {user} from IP: {client_ip}.")


@receiver(user_logged_out)
def create_user_log_on_logout(request, user, *args, **kwargs):
    """Logs the user and ip on user logout"""
    client_ip = get_client_ip(request)
    logger.info(f"Logout: {user} from IP: {client_ip}.")


@receiver(user_login_failed)
def create_user_log_on_failed_login(request, *args, **kwargs):
    """Logs the visitor's ip when a login attempt fails"""
    client_ip = get_client_ip(request)
    logger.warning(f"IP: {client_ip} failed to login.")
