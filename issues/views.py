from django.shortcuts import get_object_or_404
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.viewsets import ViewSet
from rest_framework import status

from issues.permissions import IssuePermission

from issues.models import Issue
from issues.serializers import (CreateIssueSerializer, CreateMessageSerializer,
                                IssueSerializer, MessageSerializer)
from issues.tasks import pause_issue, resolve_issue, reopen_issue


class IssueViewSet(ViewSet):
    """
    Issues API
    """
    permission_classes = (IssuePermission,)

    def list(self, request):
        """List all issues"""
        issues = Issue.objects.all() if request.user.is_superuser else Issue.objects.filter(user=request.user)
        serializer = IssueSerializer(issues, many=True)
        return Response({'data': serializer.data})

    def create(self, request):
        """Create a new issue"""
        form = CreateIssueSerializer(data=request.data)
        form.is_valid(raise_exception=True)
        issue = form.save(user=request.user)
        return Response(status=status.HTTP_201_CREATED, data=IssueSerializer(issue).data)

    def retrieve(self, request, pk):
        """Query an issue"""
        issue = get_object_or_404(Issue, pk=pk)
        self.check_object_permissions(request, issue)

        serializer = IssueSerializer(issue)
        return Response({'data': serializer.data})

    @action(detail=True, methods=['post'])
    def comment(self, request, pk):
        """Create a new message in an issue"""
        issue = get_object_or_404(Issue, pk=pk)
        self.check_object_permissions(request, issue)
        form = CreateMessageSerializer(data=request.data)
        form.is_valid(raise_exception=True)
        message = form.save(user=request.user, issue=issue)
        return Response(status=status.HTTP_201_CREATED, data=MessageSerializer(message).data)

    @action(detail=True, methods=['post'])
    def pause(self, request, pk):
        """Pause an issue"""
        issue = get_object_or_404(Issue, pk=pk)
        self.check_object_permissions(request, issue)

        try:
            task = pause_issue.delay(issue.id)
            task.wait()
        except Exception as e:
            return Response(status=status.HTTP_400_BAD_REQUEST_NOT_FOUND, data=str(e))

        issue = get_object_or_404(Issue, pk=pk)
        data = IssueSerializer(issue).data
        return Response(status=status.HTTP_200_OK, data=data)

    @action(detail=True, methods=['post'])
    def resolve(self, request, pk):
        """Resolve an issue"""
        issue = get_object_or_404(Issue, pk=pk)
        self.check_object_permissions(request, issue)

        try:
            task = resolve_issue.delay(issue.id)
            task.wait()
        except Exception as e:
            return Response(status=status.HTTP_400_BAD_REQUEST_NOT_FOUND, data=str(e))

        data = IssueSerializer(issue).data
        return Response(status=status.HTTP_200_OK, data=data)

    @action(detail=True, methods=['post'])
    def reopen(self, request, pk):
        """Reopen an issue"""
        issue = get_object_or_404(Issue, pk=pk)
        self.check_object_permissions(request, issue)

        try:
            task = reopen_issue.delay(issue.id)
            task.wait()
        except Exception as e:
            return Response(status=status.HTTP_400_BAD_REQUEST_NOT_FOUND, data=str(e))

        data = IssueSerializer(issue).data
        return Response(status=status.HTTP_200_OK, data=data)
