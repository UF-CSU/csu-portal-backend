from typing import Optional

from django.contrib import admin

from clubs.forms import TeamMembershipForm
from clubs.models import (
    Club,
    ClubMembership,
    ClubRole,
    ClubSocialProfile,
    ClubTag,
    Event,
    EventAttendance,
    EventAttendanceLink,
    EventTag,
    RecurringEvent,
    Team,
    TeamMembership,
)
from clubs.serializers import ClubCsvSerializer, ClubMembershipCsvSerializer
from clubs.services import ClubService
from core.abstracts.admin import ModelAdminBase


class ClubMembershipInlineAdmin(admin.StackedInline):
    """Create club memberships in admin."""

    model = ClubMembership
    extra = 0

    def get_formset(self, request, obj: Optional[Club] = None, **kwargs):
        """Override default formset."""
        formset = super().get_formset(request, obj, **kwargs)

        # Restrict roles to ones owned by club
        try:
            roles_qs = formset.form.base_fields["roles"].queryset
            formset.form.base_fields["roles"].queryset = roles_qs.filter(
                club__id=obj.id
            )
        except Exception as e:
            print("Unable to override membership field in admin:", e)

        return formset


class ClubRoleInlineAdmin(admin.StackedInline):
    """Manage club roles in admin."""

    model = ClubRole
    extra = 0


class ClubSocialInlineAdmin(admin.TabularInline):
    """Manage links to club social media in admin."""

    model = ClubSocialProfile
    extra = 0


class ClubAdmin(ModelAdminBase):
    """Admin config for Clubs."""

    csv_serializer_class = ClubCsvSerializer

    inlines = (ClubRoleInlineAdmin, ClubMembershipInlineAdmin, ClubSocialInlineAdmin)
    filter_horizontal = ("tags",)
    list_display = (
        "name",
        "alias",
        "id",
        "members_count",
        "created_at",
    )

    def members_count(self, obj):
        return obj.memberships.count()


class ClubTagAdmin(ModelAdminBase):
    """Manage club tags in admin dashboard."""


class RecurringEventAdmin(admin.ModelAdmin):

    list_display = (
        "__str__",
        "day",
        "location",
        "start_date",
        "end_date",
    )
    actions = ("sync_events",)

    @admin.action(description="Sync Events")
    def sync_events(self, request, queryset):

        for recurring in queryset.all():
            ClubService.sync_recurring_event(recurring)

        return


class EventAttendanceInlineAdmin(admin.TabularInline):
    """List event attendees in event admin."""

    model = EventAttendance
    extra = 0
    readonly_fields = ("created_at",)


class EventAttendenceLinkInlineAdmin(admin.StackedInline):
    """List event links in event admin."""

    model = EventAttendanceLink
    readonly_fields = (
        "target_url",
        "club",
        "tracking_url_link",
    )
    extra = 0

    def tracking_url_link(self, obj):
        return obj.as_html()


class EventAdmin(admin.ModelAdmin):
    """Admin config for club events."""

    list_display = (
        "__str__",
        "id",
        "location",
        "start_at",
        "end_at",
    )
    ordering = ("start_at",)

    inlines = (EventAttendenceLinkInlineAdmin, EventAttendanceInlineAdmin)
    filter_horizontal = ("tags", "other_clubs")


class TeamMembershipInlineAdmin(admin.TabularInline):
    """Manage user assignments to a team."""

    model = TeamMembership
    extra = 1
    form = TeamMembershipForm

    def get_formset(self, request, obj=None, **kwargs):
        if obj:
            self.form.parent_model = obj
        return super().get_formset(request, obj, **kwargs)


class TeamAdmin(admin.ModelAdmin):
    """Manage club teams in admin dashboard."""

    list_display = (
        "__str__",
        "club",
        "points",
    )
    inlines = (TeamMembershipInlineAdmin,)


class ClubMembershipAdmin(ModelAdminBase):
    """Manage club memberships in admin."""

    csv_serializer_class = ClubMembershipCsvSerializer

    list_display = (
        "__str__",
        "club",
        "club_roles",
        "created_at",
    )

    def club_roles(self, obj):
        return ", ".join(str(role) for role in list(obj.roles.all()))


admin.site.register(Club, ClubAdmin)
admin.site.register(ClubTag, ClubTagAdmin)
admin.site.register(Event, EventAdmin)
admin.site.register(EventTag)
admin.site.register(RecurringEvent, RecurringEventAdmin)
admin.site.register(Team, TeamAdmin)
admin.site.register(ClubMembership, ClubMembershipAdmin)
