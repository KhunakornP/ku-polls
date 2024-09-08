"""File for storing functions used by test cases"""
import datetime
from django.utils import timezone
from polls.models import Question


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
