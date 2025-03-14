"""
Unit tests focused around REST APIs for the Clubs Service.
"""

from django.urls import reverse
from clubs.tests.utils import create_test_club
from core.abstracts.tests import ApiTestsBase, EmailTestsBase
from lib.faker import fake


def get_club_invite_url(club_id: int):
    return reverse("api-clubs:invite", args=[club_id])


class ClubsApiTests(ApiTestsBase, EmailTestsBase):
    """Tests for club api routes."""

    def test_send_email_invites_api(self):
        """Should be able to send email invites via the API."""

        email_count = 5

        club = create_test_club()
        url = get_club_invite_url(club.id)
        payload = {"emails": [fake.safe_email() for _ in range(email_count)]}

        res = self.client.post(url, payload)
        self.assertResCreated(res)
        self.assertEmailsSent(email_count)
