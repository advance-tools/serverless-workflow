from rest_framework.generics import ListCreateAPIView, RetrieveUpdateDestroyAPIView
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.pagination import CursorPagination
from django.core.exceptions import  FieldError
from django.db import IntegrityError, transaction
from django.db.transaction import TransactionManagementError

from drf_spectacular.utils import extend_schema, extend_schema_view
from task_services.exceptions import ServerError
from task_services.models import User
from task_services.serializers.user import UserSerializer, UserListSerializer, UserUpdateSerializer


with open('./task_services/views/docs/user/user_list.md') as f:
    user_list = f.read()

with open('./task_services/views/docs/user/user_create.md') as f:
    user_create = f.read()

@extend_schema_view(
    post=extend_schema(
        tags=['User'],
        summary='Register a User',
        description=user_create,
    ),
    get=extend_schema(
        tags=['User'],
        summary='List all Users',
        description=user_list,
    ),
)
class UserListCreateAPIView(ListCreateAPIView):
    permission_classes: tuple   = (AllowAny,)
    pagination_class            = CursorPagination
    ordering: tuple             = ('-timestamp',)

    def get_serializer_class(self):

        if self.request.method == "POST": return UserSerializer

        if self.request.method == "GET" : return UserListSerializer

    def get_queryset(self):

        return User.objects.all()
    
    def get_serializer_context(self):

        return {'view': self}

    def perform_create(self, serializer):

        try:

            if serializer.is_valid(raise_exception=True):

                with transaction.atomic():

                    return serializer.save()
        
        except (FieldError, TransactionManagementError, IntegrityError, AttributeError) as exc:

            raise ServerError(exc)



with open('./task_services/views/docs/user/user_retrieve.md') as f:
    user_retrieve = f.read()

with open('./task_services/views/docs/user/user_update.md') as f:
    user_update = f.read()

with open('./task_services/views/docs/user/user_delete.md') as f:
    user_delete = f.read()

@extend_schema_view(
    get=extend_schema(
        tags=['User'],
        summary='Fetch User by ID',
        description=user_retrieve,
    ),
    put=extend_schema(
        tags=['User'],
        summary='Update User by ID',
        description=user_update,
    ),
    delete=extend_schema(
        tags=['User'],
        summary='Delete User by ID',
        description=user_delete,
    ),
)
class UserRetrieveUpdateDeleteAPIView(RetrieveUpdateDestroyAPIView):
    serializer_class            = UserUpdateSerializer
    permission_classes: tuple   = (IsAuthenticated,)
    http_method_names           = ['get', 'put', 'delete' 'head', 'option']

    def get_queryset(self):

        return User.objects.filter(id=self.request.user.id)

    def get_serializer_context(self):

        return {'view': self}

    def perform_update(self, serializer):

        try:

            if serializer.is_valid(raise_exception=True):

                with transaction.atomic():
                    # save model
                    return serializer.save()

        except (FieldError, TransactionManagementError, IntegrityError, AttributeError) as exc:

            raise ServerError(exc)

    def perform_destroy(self, instance: User):

        try:

            with transaction.atomic():

                instance.delete()
            
        except Exception as exc:

            raise ServerError(exc)

