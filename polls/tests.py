import datetime
import time
from django.test import TestCase
from django.utils import timezone
from django.urls import reverse
from .models import Question


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


class QuestionIndexViewTests(TestCase):
    """Tests for the Index View"""
    def test_no_questions(self):
        """
        Test if the index view returns an appropriate message if
        no polls are available
        """
        response = self.client.get(reverse("polls:index"))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "No polls are available.")
        self.assertQuerySetEqual(response.context["latest_question_list"], [])

    def test_past_question(self):
        """
        Questions with a pub_date in the past is shown in the index page
        """
        question = create_question("Do toasters dream of electric sheep?", -2)
        response = self.client.get(reverse("polls:index"))
        self.assertEqual(response.status_code, 200)
        self.assertQuerySetEqual(response.context["latest_question_list"],
                                 [question])

    def test_future_question(self):
        """
        Questions with a pub_date in the future should not show up
        in the index page
        """
        question = create_question("Do you like the new Iphong220?", 8008)
        response = self.client.get(reverse("polls:index"))
        self.assertQuerySetEqual(response.context["latest_question_list"],
                                 [])

    def test_display_questions(self):
        """
        The index view should only display questions with valid pub_dates
        that aren't in the future. The index page should also display
        multiple questions.
        """
        q1 = create_question("What's the most popular coding language?", -1)
        q2 = create_question("How many snails are in Kasetsart university?", 20)
        q3 = create_question("How many languages do you speak?", -5)
        response = self.client.get(reverse("polls:index"))
        self.assertQuerySetEqual(response.context["latest_question_list"],
                                 [q1, q3])


class QuestionDetailViewTest(TestCase):
    """Tests for the Detail View"""
    def test_future_question(self):
        """
        The Detail View of a question with a pub_date in the future
        returns a 404 not found when accessed
        """
        future_question = create_question("How was the field trip?", 5)
        url = reverse("polls:detail", args=(future_question.id,))
        response = self.client.get(url)
        self.assertEqual(response.status_code, 404)

    def test_past_question(self):
        """
        The Detail View of a question with a pub_date in the past should be
        accessible and display the question's text
        """
        question = create_question("What did you learn last week?", -7)
        url = reverse("polls:detail", args=(question.id,))
        response = self.client.get(url)
        self.assertContains(response, question.question_text)
