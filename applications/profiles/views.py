from rest_framework.viewsets import mixins, GenericViewSet

from applications.profiles.models import UserProfile
from applications.profiles.permissions import IsProfileOwner
from applications.profiles.serializers import ProfileSerializer

class ProfileViewSet(mixins.ListModelMixin, mixins.RetrieveModelMixin, mixins.UpdateModelMixin, GenericViewSet):
    serializer_class = ProfileSerializer
    permission_classes = [IsProfileOwner]
    queryset = UserProfile.objects.all()
    