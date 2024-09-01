"""Models for the polls application"""
import datetime
from django.db import models
from django.utils import timezone


class Question(models.Model):
    """
    A class representing poll questions.
    Questions have a title represented by 'question_text'
    and a publishing date represented by 'pub_date'
    """
    question_text = models.CharField(max_length=200)
    pub_date = models.DateTimeField("Date published", default=timezone.now)
    end_date = models.DateTimeField("End date", null=True, blank=True)

    def was_published_recently(self):
        """
        Determines if the poll question was published within 1 day of
        its creation
        :return: A boolean, True if the pub_date is at most 1 day in the past
        False if pub_date is in the future or pub_date is more than 1 day old
        """
        return (timezone.now() >= self.pub_date
                >= timezone.now() - datetime.timedelta(days=1))

    def is_published(self):
        """
        Determines if the poll question should be visible/is published.
        :return: A boolean, True if current date is after the pub_date,
        False otherwise.
        """
        return self.pub_date <= timezone.now()

    def can_vote(self):
        """
        Determines if the poll can be voted on.
        Polls can be voted on if the current date is before the end date and
        after it's publishing date. If the end date is not specified, the poll
        can be voted on anytime after the start date.
        :return: A boolean, True if current date is between pub_date and
        end_date or anytime after the pub_date if end_date is NULL,
        False otherwise
        """
        if self.end_date:
            return self.pub_date <= timezone.now() <= self.end_date
        else:
            return self.pub_date <= timezone.now()

    def __str__(self):
        """Returns the Question's text for the user"""
        return self.question_text


class Choice(models.Model):
    """
    A class for users to choose poll answers.
    One Question object may have many Choice objects but one Choice object
    may only be associated with one question.
    """
    question = models.ForeignKey(Question, on_delete=models.CASCADE)
    choice_text = models.CharField(max_length=200)
    votes = models.IntegerField(default=0)

    def __str__(self):
        """Returns the Choice's text for the user"""
        return self.choice_text
