"""Test cases for classes used in the voting process"""
import datetime
import time
from .functions import create_question
from django.test import TestCase
from django.utils import timezone
from polls.models import Question


class QuestionModelTestcase(TestCase):
    """Tests for the Question class"""
    def test_was_published_recently_with_future_question(self):
        """
        The was_published_recently() method should return False
        for questions with a pub_date in the future
        """
        time = timezone.now() + datetime.timedelta(days=30)
        future_question = Question(pub_date=time)
        self.assertFalse(future_question.was_published_recently())

    def test_was_published_recently_with_old_question(self):
        """
        The was_published_recently() method should return False
        for questions with a pub_date older than 1 day
        """
        time = timezone.now() - datetime.timedelta(days=30)
        old_question = Question(pub_date=time)
        self.assertFalse(old_question.was_published_recently())

    def test_was_published_recently_with_recent_question(self):
        """
        The was_published_recently() method should return True
        for questions with a pub_date within the last day
        """
        time = timezone.now()
        recent_question = Question(pub_date=time)
        self.assertTrue(recent_question.was_published_recently())

    def test_pub_date_has_default_value(self):
        """
        A question should have a publishing date which by default is
        the current time
        """
        recent_question1 = Question()
        time.sleep(0.00001)
        recent_question2 = Question()
        self.assertTrue(recent_question1.was_published_recently())
        self.assertNotEqual(recent_question1.pub_date,
                            recent_question2.pub_date)

    def test_end_date_can_be_null(self):
        """
        Question end dates are optional and when not specified are NULl (None)
        """
        default_question = Question()
        self.assertEqual(default_question.end_date, None)

    def test_can_vote(self):
        """
        The can_vote method should return True if the current date is after
        the publishing date and before the end date.
        If the end date is not specified the date can be any day after the
        publishing date.
        """
        valid_question = create_question("Have you done your work?", -5, 10)
        invalid_question = create_question("TODO: think of a question", 2, -10)
        self.assertTrue(valid_question.can_vote())
        self.assertFalse(invalid_question.can_vote())

    def test_cannot_vote_after_end_date(self):
        """
        Polls cannot be voted on if they are after the end date
        """
        ended_question = create_question("Does Caesar suck?", -10, -5)
        self.assertFalse(ended_question.can_vote())

    def test_can_vote_with_no_end_date(self):
        """
        If no end date is specified, polls can be voted on as long as
        the current date is after the published date.
        """
        valid_no_end = create_question("How are you feeling?", -1)
        invalid_no_end = create_question("Question template text?", 1)
        self.assertTrue(valid_no_end.can_vote())
        self.assertFalse(invalid_no_end.can_vote())
