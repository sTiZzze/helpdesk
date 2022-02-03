from django.shortcuts import get_object_or_404
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.viewsets import ViewSet

from issues.permissions import IssuePermission

from .models import Issue
from .serializers import (CreateIssueSerializer, CreateMessageSerializer,
                          IssueSerializer, MessageSerializer)
from .tasks import pause_issue, resolve_issue, reopen_issue


class IssueViewSet(ViewSet):
    """
    Issues API
    """
    permission_classes = [IssuePermission]

    def list(self, request):
        """List all issues"""
        issues = Issue.objects.all() if request.user.is_superuser else Issue.objects.filter(user=request.user)
        serializer = IssueSerializer(issues, many=True)
        return Response({'data': serializer.data})

    def create(self, request):
        """Create a new issue"""
        form = CreateIssueSerializer(data=request.data)
        try:
            if form.is_valid():
                issue = form.save(user=request.user)
                return Response(status=201, data=IssueSerializer(issue).data)
            else:
                return Response(status=400, data=form.errors)
        except Exception as e:
            return Response(status=400, data=str(e))

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
        try:
            form = CreateMessageSerializer(data=request.data)
            if form.is_valid():
                message = form.save(user=request.user, issue=issue)
                return Response(status=201, data=MessageSerializer(message).data)
            else:
                return Response(status=400, data=form.errors)
        except Exception as e:
            return Response(status=400, data=str(e))

    @action(detail=True, methods=['post'])
    def pause(self, request, pk):
        """Pause an issue"""
        issue = get_object_or_404(Issue, pk=pk)
        self.check_object_permissions(request, issue)

        try:
            task = pause_issue.delay(issue.id)
            task.wait()
        except Exception as e:
            return Response(status=400, data=str(e))

        issue = get_object_or_404(Issue, pk=pk)
        data = IssueSerializer(issue).data
        return Response(status=200, data=data)

    @action(detail=True, methods=['post'])
    def resolve(self, request, pk):
        """Resolve an issue"""
        issue = get_object_or_404(Issue, pk=pk)
        self.check_object_permissions(request, issue)

        try:
            task = resolve_issue.delay(issue.id)
            task.wait()
        except Exception as e:
            return Response(status=400, data=str(e))

        data = IssueSerializer(issue).data
        return Response(status=200, data=data)

    @action(detail=True, methods=['post'])
    def reopen(self, request, pk):
        """Reopen an issue"""
        issue = get_object_or_404(Issue, pk=pk)
        self.check_object_permissions(request, issue)

        try:
            task = reopen_issue.delay(issue.id)
            task.wait()
        except Exception as e:
            return Response(status=400, data=str(e))

        data = IssueSerializer(issue).data
        return Response(status=200, data=data)
