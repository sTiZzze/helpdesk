from django.contrib.auth.models import User
from django.test import TestCase

from issues.models import Issue, State


class IssueModelTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.user = User.objects.create_user(username='testuser', password='12345')
        cls.user.save()

    def test_create_issue(self):
        issue = Issue.objects.create(topic='topic', text='text', user=self.user)
        issue.save()
        self.assertEqual(issue.user, self.user)
        self.assertEqual(issue.topic, 'topic')
        self.assertEqual(issue.text, 'text')
        self.assertEqual(issue.state, State.OPEN)

    def test_pause_issue(self):
        issue = Issue.objects.create(topic='topic', text='text', user=self.user)
        issue.pause()
        issue.save()
        self.assertEqual(issue.state, State.PAUSED)
