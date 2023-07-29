from rest_framework.generics import CreateAPIView, DestroyAPIView
from rest_framework.permissions import AllowAny
from django.db import transaction

from drf_spectacular.utils import extend_schema, extend_schema_view
from task_services.models import User
from task_services.serializers.profile import UserProfileSerializer


with open('./task_services/views/docs/profile/profile_create.md') as f:
    user_profile_create = f.read()

with open('./task_services/views/docs/profile/profile_destroy.md') as f:
    user_profile_destroy = f.read()

@extend_schema_view(
    post=extend_schema(
        tags=['Profile'],
        summary='Perform Signin',
        description=user_profile_create,
    ),
    delete=extend_schema(
        tags=['Profile'],
        summary='Perform Signout',
        description=user_profile_destroy,
    ),
)
class ProfileAPIView(CreateAPIView, DestroyAPIView):
    serializer_class            = UserProfileSerializer
    permission_classes: tuple   = (AllowAny,)

    def get_queryset(self):

        return User.objects.all()

    def get_object(self):

        return self.get_queryset().get(id=self.request.user.id)

    def get_serializer_context(self):

        return {'view': self}
    
    def perform_create(self,serializer):

        if serializer.is_valid(raise_exception=True):

            with transaction.atomic():
                
                serializer.save()

    def perform_destroy(self,instance:User):

        with transaction.atomic():
                
            instance.auth_token.delete()


