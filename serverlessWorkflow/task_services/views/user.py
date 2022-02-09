from rest_framework.generics import ListCreateAPIView, RetrieveUpdateDestroyAPIView, CreateAPIView, DestroyAPIView
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.pagination import CursorPagination
from django.core.exceptions import  FieldError
from django.db import IntegrityError, transaction
from django.db.transaction import TransactionManagementError

from task_services.exceptions import ServerError
from task_services.models import User
from task_services.serializers.user import UserSerializer, UserListSerializer, UserUpdateSerializer, UserProfileSerializer


class UserListCreateAPIView(ListCreateAPIView):
    """
    post: User Create\n
    This endpoint will return new user created with provided input.
    """
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


class UserRetrieveUpdateDeleteAPIView(RetrieveUpdateDestroyAPIView):
    """
    Retrieve, Update or Delete an Existing User Instance.

    get: User RETRIEVE\n
    This endpoint will return User information of authenticated user.The data will appear in the form of key/value properties. The data can be retrieved with the help of the id of that User.

    ### Authentication:
    * Required Token Authentication

    put: User UPDATE\n
    This endpoint will update information of authenticated user.A User update request must have all data in the correct form of key/value property. The collection must contain all the required properties.

    ### Authentication:
    * Required Token Authentication

    delete: User DELETE\n
    This endpoint will delete authenticated user.User deletion will also delete all the task associate with that user.

    ### Authentication:
    * Required Token Authentication
    """

    serializer_class            = UserUpdateSerializer
    permission_classes: tuple   = (IsAuthenticated,)

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


class UserProfileAPIView(CreateAPIView,DestroyAPIView):
    """
    post: Profile CREATE\n
    This endpoint will return Authorization token for user if user has provided correct email and password.
    """
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


