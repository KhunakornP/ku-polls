"""File for storing functions used by test cases"""
import datetime
from django.utils import timezone
from django.urls import reverse
from polls.models import Question, Choice
from django.contrib.auth.models import User


def create_question(text, days, end_date=None):
    """
    Creates a Question object with the given "text" and published
    number of "days" offset to now. The "days" can be positive (in the future)
    or negative (in the past). This function is used for a few test cases.
    :param text: The question's text
    :param days: The publishing date of the question offset from now
    :param end_date: The end_date for the question offset from now
    :return: A Question object with question_text = text and a publishing date
    equal to timezone.now() +- days
    """
    start_time = timezone.now() + datetime.timedelta(days=days)
    if end_date:
        end_time = timezone.now() + datetime.timedelta(days=end_date)
        return Question.objects.create(question_text=text, pub_date=start_time,
                                       end_date=end_time)
    return Question.objects.create(question_text=text, pub_date=start_time)


def create_choice(text, question):
    """
    Creates a Choice object with the given "text" and the question the
    choice is for
    :param text: The choice's text
    :param question: The question the choice belongs to
    :return: A Choice object with choice_text = text and its associated
    question
    """
    return Choice.objects.create(question=question, choice_text=text)


def create_user(username="dummy", password="password"):
    """
    Creates a user for testing
    :param username: The user's username
    :param password: The user's password
    :return: A user with the given username and password
    """
    user = User.objects.create(username=username, password=password)
    user.save()
    return user


def vote(choice, user):
    """
    Make a user vote a certain choice
    :param choice: The choice that the user is voting for
    :param user: The user that is voting for the choice
    :return: A HttpResponse object
    """
    response = user.post(reverse('polls:vote', args=(choice.question.id,)),
                         {"choice": choice.id})
    return response
