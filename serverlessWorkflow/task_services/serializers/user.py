from django.contrib.auth import get_user_model

from rest_framework import serializers
from rest_framework.request import Request
from rest_framework.authtoken.models import Token

from serverlessWorkflow.exception import IDUpdateValidationError, EmailValidationError
from task_services.models import User

from uuid import UUID
from collections import OrderedDict


class UserSerializer(serializers.ModelSerializer):

    id                              = serializers.UUIDField(read_only=True)
    email                           = serializers.EmailField(required=True)
    password                        = serializers.CharField(required=True,write_only=True)
    name                            = serializers.CharField(required=True)
    created_at                      = serializers.DateTimeField(read_only=True)

    class Meta:
        model  = get_user_model()
        fields = [
            "id",
            "email",
            "password",
            "name",
            "created_at",
        ]
    
    def validate_email(self, value: str) -> str:

        if User.objects.filter(email=value).exists():

            raise EmailValidationError()

        return value.lower()


class UserListSerializer(serializers.ModelSerializer):

    class Meta:
        model   = get_user_model()
        fields  = [
            "name",
            "email",
        ]


class UserUpdateSerializer(serializers.ModelSerializer):

    id                              = serializers.UUIDField(read_only=True, format='hex_verbose', help_text="Primary Key of the Employee")
    email                           = serializers.EmailField(required=True)
    password                        = serializers.CharField(required=False, write_only=True)
    name                            = serializers.CharField(required=True)

    class Meta:
        model  = get_user_model()
        fields = [
            "id",
            "email",
            "password",
            "name",
        ]
    
    def validate_id(self, value: UUID) -> UUID:

        if self.instance:

            if self.context.get("view").kwargs.get("pk") != str(value):

                raise IDUpdateValidationError()

        return value

    def validate_email(self, value: str) -> str:

        request: Request = self.context.get("view").request

        if request.method == "PUT":

            if User.objects.filter(email=value).exists():

                raise EmailValidationError()

        return value.lower()
    
    def update(self, instance: User, validated_data: OrderedDict) -> User:

        instance.name   = validated_data['name']
        instance.email  = validated_data['email']

        if validated_data['password'] and instance.password != validated_data['password']:

            instance.set_password(validated_data['password'])

        instance.save()

        return instance

