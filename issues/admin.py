from django.contrib import admin

from issues.models import Issue, Message


class MessageInline(admin.TabularInline):
    model = Message
    extra = 0
    readonly_fields = ('created_at',)


@admin.action(description='Pause selected issues')
def pause_issues(modeladmin, request, queryset):
    for obj in queryset:
        obj.pause()
        obj.save()


@admin.action(description='Resolve selected issues')
def resolve_issues(modeladmin, request, queryset):
    for obj in queryset:
        obj.resolve()
        obj.save()


@admin.action(description='Reopen selected issues')
def reopen_issues(modeladmin, request, queryset):
    for obj in queryset:
        obj.reopen()
        obj.save()


@admin.register(Issue)
class IssueAdmin(admin.ModelAdmin):
    inlines = [
        MessageInline,
    ]
    readonly_fields = ('state', 'created_at', 'updated_at')
    list_display = ('id', 'user', 'topic', 'text', 'state', 'created_at', 'updated_at')
    actions = [pause_issues, resolve_issues, reopen_issues]
