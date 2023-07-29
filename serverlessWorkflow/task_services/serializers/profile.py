from django.contrib.auth import authenticate, get_user_model

from rest_framework import serializers
from rest_framework.request import Request
from rest_framework.authtoken.models import Token

from serverlessWorkflow.exception import EmailPasswordValidationError
from task_services.models import User

from collections import OrderedDict


class UserProfileSerializer(serializers.ModelSerializer):
    email       = serializers.EmailField(required=True)
    password    = serializers.CharField(required=True,write_only=True)
    token       = serializers.SerializerMethodField(help_text="User's Token Key will be given in response if User has logged in Correctly")

    class Meta:
        model = get_user_model()
        fields = [
            'email',
            'password',
            'token',
        ]

    def get_token(self, instance: User) -> str:

        return instance.auth_token.key
    
    def validate(self, data: OrderedDict) -> OrderedDict:

        request: Request = self.context.get('view').request

        ################
        # Authenticate
        ################
        
        self.user: User = authenticate(request, email=data.get('email').lower(), password=data.get('password'))

        if self.user is None:

            raise EmailPasswordValidationError()

        return data

    def create(self, validated_data: OrderedDict) -> User:

        if hasattr(self.user, 'auth_token'):

            self.user.auth_token.delete()

        Token.objects.create(user=self.user)

        return self.user

