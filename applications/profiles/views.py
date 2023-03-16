
from rest_framework.permissions import IsAuthenticated
from rest_framework.viewsets import mixins

from applications.profiles.models import UserProfile
from applications.profiles.serializers import ProfileSerializer

class ProfileViewSet(mixins.RetrieveModelMixin, mixins.UpdateModelMixin, GenericViewSet):
    serializer_class = ProfileSerializer
    permission_classes = [IsAuthenticated]
    queryset = UserProfile.objects.all()
    
    def get_queryset(self):
        return UserProfile.objects.filter(user=self.request.user)