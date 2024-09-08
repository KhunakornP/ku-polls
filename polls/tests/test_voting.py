"""Test cases for voting"""
from .functions import create_question, create_choice, create_user, vote
from polls.models import Vote
from django.test import TestCase


class VoteTestCase(TestCase):
    """Test cases for user voting"""
    def test_user_voting(self):
        """
        A user should be able to vote on a choice, when a user votes
        a Vote object is created in the database.
        """
        question = create_question("Do you hate roaches?", -1)
        c1 = create_choice("yes", question)
        c2 = create_choice("no", question)
        user = create_user("John McGregor", "Roaches123")
        self.client.force_login(user)
        vote(c1, self.client)  # vote yes
        self.assertEqual(c1.vote_set.count(), 1)
        self.assertEqual(c2.vote_set.count(), 0)

    def test_user_changes_vote(self):
        """
        When a user votes on a different choice on the same question,
        the previous Vote object has its choice updated to the latest choice
        """
        question = create_question("Do you hate roaches?", -1)
        c1 = create_choice("yes", question)
        c2 = create_choice("no", question)
        user = create_user("John McGregor", "Roaches123")
        self.client.force_login(user)
        vote(c1, self.client)  # vote yes
        self.assertEqual(c1.vote_set.count(), 1)
        self.assertEqual(c2.vote_set.count(), 0)
        vote(c2, self.client)  # actually maybe not
        self.assertEqual(c1.vote_set.count(), 0)
        self.assertEqual(c2.vote_set.count(), 1)

    def test_user_votes_on_multiple_questions(self):
        """
        A user can vote on multiple questions.
        """
        question1 = create_question("Have you found your Ideals?", -1)
        question2 = create_question("What's your favorite dish?", -1)
        c1 = create_choice("yes", question1)
        c2 = create_choice("no", question1)
        c3 = create_choice("Fried rice", question2)
        c4 = create_choice("Pizza", question2)
        user = create_user()
        self.client.force_login(user)
        vote(c1, self.client)
        vote(c3, self.client)
        # check the total votes, should be 2
        self.assertEqual(Vote.objects.count(), 2)
        # check the individual vote counts for choices
        self.assertEqual(c1.vote_set.count(), 1)
        self.assertEqual(c2.vote_set.count(), 0)
        self.assertEqual(c3.vote_set.count(), 1)
        self.assertEqual(c4.vote_set.count(), 0)

    def test_user_changes_vote_on_multiple_questions(self):
        """
        A user can vote on multiple questions. and can change their votes
        regardless of question.
        """
        question1 = create_question("Have you found your Ideals?", -1)
        question2 = create_question("What's your favorite dish?", -1)
        c1 = create_choice("yes", question1)
        c2 = create_choice("no", question1)
        c3 = create_choice("Fried rice", question2)
        c4 = create_choice("Pizza", question2)
        user = create_user()
        self.client.force_login(user)
        vote(c1, self.client)
        vote(c3, self.client)
        # invert the vote choices
        vote(c2, self.client)
        vote(c4, self.client)
        # check the total votes, should be 2
        self.assertEqual(Vote.objects.count(), 2)
        # check the individual vote counts for choices
        self.assertEqual(c1.vote_set.count(), 0)
        self.assertEqual(c2.vote_set.count(), 1)
        self.assertEqual(c3.vote_set.count(), 0)
        self.assertEqual(c4.vote_set.count(), 1)
