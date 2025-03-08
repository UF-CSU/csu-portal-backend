"""
Override default django-allauth functionality
by extending their DefaultAccountAdapter. This
new class is set as the primary adapter in settings.py

Docs: https://django-allauth.readthedocs.io/en/latest/socialaccount/adapter.html
"""

from allauth.socialaccount.adapter import DefaultSocialAccountAdapter


class CustomAdapter(DefaultSocialAccountAdapter):
    """Custom logic for OAuth authentication."""

    def get_connect_redirect_url(self, request, socialaccount):
        print("source:", request.GET.get("source", None))
        return super().get_connect_redirect_url(request, socialaccount)
