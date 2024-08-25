import datetime
from django.test import TestCase
from django.utils import timezone
from django.urls import reverse
from .models import Question


def create_question(text, days):
    """
    Creates a Question object with the given "text" and published
    number of "days" offset to now. The "days" can be positive (in the future)
    or negative (in the past). This function is used for a few test cases.
    :param text: The question's text
    :param days: The publishing date of the question offset from now
    :return: A Question object with question_text = text and a publishing date
    equal to timezone.now() +- days
    """
    time = timezone.now() + datetime.timedelta(days=days)
    return Question.objects.create(question_text=text, pub_date=time)


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


class QuestionIndexViewTests(TestCase):
    """Tests for the Index View"""
    def test_no_questions(self):
        """
        Test if the index view returns an appropriate message if
        no polls are available
        """
        response = self.client.get(reverse("polls:index"))
        self.assertEquals(response.status_code, 200)
        self.assertContains(response, "No polls are available.")
        self.assertQuerySetEqual(response.context["latest_question_list"], [])

    def test_past_question(self):
        """
        Questions with a pub_date in the past is shown in the index page
        """
        question = create_question("Do toasters dream of electric sheep?", -2)
        response = self.client.get(reverse("polls:index"))
        self.assertEquals(response.status_code, 200)
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
