import logging

from celery import shared_task

from .models import Issue

logger = logging.getLogger(__name__)


@shared_task
def pause_issue(issue_id):
    print(issue_id)
    issue = Issue.objects.get(id=issue_id)
    issue.pause()
    issue.save()
    return True


@shared_task
def resolve_issue(issue_id):
    print(issue_id)
    issue = Issue.objects.get(id=issue_id)
    issue.resolve()
    issue.save()
    return True


@shared_task
def reopen_issue(issue_id):
    print(issue_id)
    issue = Issue.objects.get(id=issue_id)
    issue.reopen()
    issue.save()
    return True
