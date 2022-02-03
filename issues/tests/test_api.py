from django.contrib.auth.models import User
from django.urls import reverse
from mock import patch
from rest_framework import status
from rest_framework.test import APITestCase

from issues.models import Issue, State


class IssuesApiUserTestCase(APITestCase):
    @classmethod
    def setUpTestData(cls):
        cls.user = User.objects.create_user(username='testuser', password='12345')

    def setUp(self):
        self.client.login(username='testuser', password='12345')

    def test_create_issue(self):
        url = reverse('issues-list')
        data = {'text': 'text', 'topic': 'topic'}

        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Issue.objects.count(), 1)

        issue = Issue.objects.get()

        self.assertEqual(issue.text, 'text')
        self.assertEqual(issue.topic, 'topic')
        self.assertEqual(issue.user, self.user)
        self.assertEqual(issue.state, State.OPEN)

    def test_pause_issue(self):
        issue = Issue.objects.create(topic='topic', text='text', user=self.user)

        url = reverse('issues-pause', kwargs={'pk': issue.pk})
        response = self.client.post(url, None, format='json')

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)


class IssuesApiStaffTestCase(APITestCase):
    @classmethod
    def setUpTestData(cls):
        cls.user = User.objects.create_user(username='testuser', password='12345', is_staff=True)

    def setUp(self):
        self.client.login(username='testuser', password='12345')
        self.issue = Issue.objects.create(topic='topic', text='text', user=self.user)

    def test_pause_issue(self):
        url = reverse('issues-pause', kwargs={'pk': self.issue.pk})

        with patch('issues.views.pause_issue.delay') as mock_task:
            response = self.client.post(url, None, format='json')
            self.assertEqual(response.status_code, status.HTTP_200_OK)
            mock_task.assert_called_once_with(self.issue.pk)
