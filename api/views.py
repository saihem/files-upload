from rest_framework import viewsets

from core.models import Owner
from .serializers import UserSerializer


class UserViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows users to be viewed or edited.
    """

    queryset = Owner.objects.order_by('-date_joined')
    serializer_class = UserSerializer
