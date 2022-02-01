from rest_framework.exceptions import APIException
from rest_framework import status


class IDUpdateValidationError(APIException):
    status_code = status.HTTP_400_BAD_REQUEST
    default_detail = 'Cannot Update Id of the Instance. (Err Code: 4039)'


class EmailValidationError(APIException):
    status_code = status.HTTP_400_BAD_REQUEST
    default_detail = 'Email address already exists (Err Code: 4050)'
    default_code = 'service_unavailable'


class EmailPasswordValidationError(APIException):
    status_code = status.HTTP_400_BAD_REQUEST
    default_detail = 'Invalid Email or Password (Err Code: 4070)'
    default_code = 'service_unavailable'