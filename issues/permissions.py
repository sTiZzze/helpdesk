from rest_framework.permissions import BasePermission


class IssuePermission(BasePermission):

    def has_permission(self, request, view):
        return request.user.is_authenticated

    def has_object_permission(self, request, view, obj):
        if view.action in ['retrieve', 'comment']:
            return obj == request.user or request.user.is_staff
        elif view.action in ['pause', 'resolve', 'reopen']:
            return request.user.is_staff
        return False
