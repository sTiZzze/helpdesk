# Create your models here.
import logging

from django.conf import settings
from django.db import models
from django_fsm import FSMField, transition

logger = logging.getLogger(__name__)


class State(models.TextChoices):
    OPEN = 'open'
    PAUSED = 'paused'
    RESOLVED = 'resolved'


class Issue(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    topic = models.CharField(max_length=255)
    text = models.TextField()
    state = FSMField(default=State.OPEN, choices=State.choices, protected=False)
    created_at = models.DateTimeField(auto_now_add=True, db_index=True)
    updated_at = models.DateTimeField(auto_now_add=True, db_index=True)

    @transition(field=state, source=[State.OPEN], target=State.PAUSED)
    def pause(self):
        logger.info(f'{self!r} has been paused')

    @transition(field=state, source=[State.PAUSED, State.OPEN], target=State.RESOLVED)
    def resolve(self):
        logger.info(f'{self!r} has been resolved')

    @transition(field=state, source=[State.RESOLVED, State.PAUSED], target=State.OPEN)
    def reopen(self):
        logger.info(f'{self!r} has been reopened')

    def __str__(self):
        return'Issue #{self.id}'.format(self=self)


class Message(models.Model):
    text = models.TextField(max_length=255)
    issue = models.ForeignKey(Issue, on_delete=models.CASCADE, related_name='messages')
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True, db_index=True)

    def __str__(self):
        return self.text
