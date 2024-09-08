"""Test cases for poll views"""
from .functions import create_question
from django.test import TestCase
from django.urls import reverse


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
                                 [q1, q3], ordered=False)

    def test_display_open_and_closed_questions(self):
        """
        The index view should display questions which are published for
        questions that can and can't be voted on
        """
        q1 = create_question("What's the most popular coding language?",
                             -1, 10)
        q2 = create_question("How many snails are in Kasetsart university?",
                             12, 13)
        q3 = create_question("How many languages do you speak?", -5, -2)
        response = self.client.get(reverse("polls:index"))
        self.assertQuerySetEqual(response.context["latest_question_list"],
                                 [q1, q3], ordered=False)


class QuestionDetailViewTest(TestCase):
    """Tests for the Detail View"""
    def test_future_question(self):
        """
        The Detail View of a question with a pub_date in the future
        returns a redirect to the index page.
        """
        future_question = create_question("How was the field trip?", 5)
        url = reverse("polls:detail", args=(future_question.id,))
        response = self.client.get(url)
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, reverse("polls:index"))

    def test_past_question(self):
        """
        The Detail View of a question with a pub_date in the past should be
        accessible and display the question's text
        """
        question = create_question("What did you learn last week?", -7)
        url = reverse("polls:detail", args=(question.id,))
        response = self.client.get(url)
        self.assertContains(response, question.question_text)

    def test_non_existent_question(self):
        """
        Trying to access a details of a poll question that doesn't exist
        returns a redirect to the index page.
        """
        url = reverse("polls:detail", args=(99,))
        response = self.client.get(url)
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, reverse("polls:index"))
