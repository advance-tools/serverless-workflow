from rest_framework.exceptions import APIException
from rest_framework import status
import sys
import os
from django.utils import timezone


def register_bug(exc):
    exc_type, exc_obj, exc_tb = sys.exc_info()
    filename = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
    time_recorded = timezone.now()
    description = str(exc)
    # Console log Bug
    print('\n-----------------------------------------------------------------------------------------------', end=" ")
    print('Bug Registered: ', time_recorded, end=" ")
    print('-----------------------------------------------------------------------------------------------', end=" ")
    print('Exception Type: ', exc_type, end=" ")
    print('Message: ', description, end=" ")
    print('Path: ', exc_tb.tb_frame.f_code.co_filename, end=" ")
    print('Filename: ', filename, end=" ")
    print('Line No: ', exc_tb.tb_lineno, end=" ")
    print('-----------------------------------------------------------------------------------------------\n', end=" ")


class ServerError(APIException):
    status_code = status.HTTP_500_INTERNAL_SERVER_ERROR
    default_detail = 'Internal server error found, your bug has been registered. Please try again later sometime.'
    default_code = 'Server Error'

    def __init__(self, exc):
        super().__init__()

        self.exc = exc

        self.detail = str(exc)

        register_bug(self.exc)


class ObjectNotFound(APIException):
    status_code = status.HTTP_404_NOT_FOUND
    default_detail = 'Object you requested does not exist!'
    default_code = 'Object does not exist'

    def __init__(self, exc):
        super().__init__()

        self.exc = exc

        self.detail = str(exc)

        register_bug(self.exc)


class CannotDelete(APIException):
    status_code = status.HTTP_403_FORBIDDEN
    default_detail = 'Cannot delete object because there are dependencies.'
    default_code = 'Cannot delete object'

    def __init__(self, exc):
        super().__init__()

        self.exc = exc

        self.detail = str(exc)

        register_bug(self.exc)
