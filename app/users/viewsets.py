"""
Views for the user API.
"""

from rest_framework import authentication, generics
from rest_framework.authtoken.views import ObtainAuthToken
from rest_framework.settings import api_settings

from core.abstracts.viewsets import ModelViewSetBase
from users.serializers import UserSerializer


class CreateUserView(generics.CreateAPIView):
    """Create a new user in the system."""

    serializer_class = UserSerializer


class AuthTokenView(ObtainAuthToken, generics.RetrieveAPIView, generics.GenericAPIView):
    """Create a new auth token for user."""

    renderer_classes = api_settings.DEFAULT_RENDERER_CLASSES
    authentication_classes = [
        authentication.TokenAuthentication,
        authentication.SessionAuthentication,
    ]


class ManageUserView(generics.RetrieveUpdateAPIView):
    """Manage the authenticated user."""

    serializer_class = UserSerializer
    authentication_classes = ModelViewSetBase.authentication_classes
    permission_classes = ModelViewSetBase.permission_classes

    def get_object(self):
        """Retrieve and return the authenticated user."""

        return self.request.user
