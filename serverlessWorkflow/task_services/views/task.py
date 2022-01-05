from rest_framework import status
from rest_framework.generics import CreateAPIView, UpdateAPIView, DestroyAPIView
from rest_framework.views import APIView
from rest_framework.response import Response

from django.core.exceptions import FieldDoesNotExist, FieldError, ObjectDoesNotExist, MultipleObjectsReturned
from django.db import IntegrityError, transaction
from django.db.models.deletion import ProtectedError
from django.db.transaction import TransactionManagementError
from django.urls import reverse

from serverlessWorkflow.task import create_http_task

from task_services.exceptions import ServerError, ObjectNotFound, CannotDelete

from task_services.models import Task, StatusChoices, ImmediateInputTypeChoices, SubTaskInputTypeChoices
from task_services.serializers.task import InitTaskSerializer, CompleteTaskSerializer, ChoicesSerializer

from uuid import uuid4


class ChoicesAPIView(APIView):
    """
    get: Task Choices\n
    This will return all the Choices need in Task.
    """
    serializer_class = ChoicesSerializer

    def get(self, request, *args, **kwargs):

        data = {
            "status_choices"                : dict(StatusChoices.choices),
            "immediate_input_type_choices"  : dict(ImmediateInputTypeChoices.choices),
            "sub_task_input_type_choices"   : dict(SubTaskInputTypeChoices.choices)
        }

        return Response(data=data, status=status.HTTP_200_OK)


class TaskInitAPIView(CreateAPIView):
    """
    post: Task Init POST\n
    An api endpoint to Initiate Tasks.
    """
    serializer_class = InitTaskSerializer

    def get_queryset(self):

        return Task.objects.all()

    def perform_create(self, serializer):

        try:

            if serializer.is_valid(raise_exception=True):

                with transaction.atomic():

                    code = None

                    # checking if parent_task is not None
                    if serializer.validated_data.get("parent_task"):

                        # updating parent_code
                        parent_codes: str = serializer.validated_data.get("parent_task").code
                    
                        # concating string
                        code = parent_codes + f",{uuid4()}"

                    else:

                        code = f"{uuid4()}"

                    # save model
                    return serializer.save(code=code)

        except (FieldDoesNotExist, FieldError, TransactionManagementError, IntegrityError, AttributeError) as exc:

            raise ServerError(exc)


class TaskCompletedAPIView(UpdateAPIView):

    """
    put: Task Completed PUT\n
    An api endpoint to Mark Task Completed.

    ## Things happening in this endpoint:
    * Checking if TaskStatus is Completed
        * then Triggering all ImmediateNext Tasks One by One
    * Checking if Length of ImmediateNext is 0 or None
        * then Check endpoint is called for the Current Task

    | Validation | Error Code | Error Messages |
    |------------|------------|----------------|
    | If ImmediateNext is None or [] then SubTaskNext should be None or [] | 400 | Sub Task Next should be None when Immediate Next is None. |

    patch: Task Completed PATCH\n
    (PUT Recommended) An api endpoint to Mark Task Completed.

    ## Things happening in this endpoint:
    * Checking if TaskStatus is Completed
        * then Triggering all ImmediateNext Tasks One by One
    * Checking if Length of ImmediateNext is 0 or None
        * then Check endpoint is called for the Current Task

    | Validation | Error Code | Error Messages |
    |------------|------------|----------------|
    | If ImmediateNext is None or [] then SubTaskNext should be None or [] | 400 | Sub Task Next should be None when Immediate Next is None. |
    """
    serializer_class = CompleteTaskSerializer

    def get_queryset(self):

        return Task.objects.all()

    def get_object(self):

        try:

            return self.get_queryset().get(id=self.request.data.get("id"))

        except ObjectDoesNotExist as exc:

            raise ObjectNotFound(exc)

        except MultipleObjectsReturned as exc:

            raise ServerError(exc)

    def perform_update(self, serializer):

        try:

            if serializer.is_valid(raise_exception=True):

                with transaction.atomic():

                    # save model
                    return serializer.save()

        except (FieldDoesNotExist, FieldError, TransactionManagementError, IntegrityError, AttributeError) as exc:

            raise ServerError(exc)


class TaskCheckAPIView(APIView):
    """
    put: Task Check PUT\n
    An api endpoint to Check Task's Completion.

    ## Things happening in this endpoint:
    * Checking if all the children's `task_status` and `sub_task_status` is **Completed** of the Current Task and Current Task's `sub_task_next's length` is greater than **0**.
        * then all the Sub Task will be triggered one by one.
    * Checking if all the children's `task_status` and `sub_task_status` is **Completed** of the Current Task and Current Task's `sub_task_next's length` is **0**.
        * then `SubTaskStatus` of the Current Task will be Marked as **Completed**.
        * Checking if Current Task's `parent_task` is **not None**.
            * then triggering check for the parent_task.
        * Checking if Current Task's `parent_task` is **None**.
            * **Deleting** the `Current Task` and its `Children`.
    """
    def put(self, request, *args, **kwargs):

        obj = None

        # Getting Task
        queryset = Task.objects.filter(id=kwargs.get("id"))

        # If queryset exists getting first instance
        if queryset.exists():

            obj = queryset.first()

        # If object is not None and object's sub_task_next is not None or length of sub_task_next is greater than 0 and Checking if current tasks all children's task_status and sub_task_status is Completed
        if obj and obj.sub_task_next is not None and len(obj.sub_task_next) > 0 and not Task.objects.filter(
            code__contains=obj.code.split(",")[-1]
        ).exclude(
            id=kwargs.get("id")
        ).exclude(
            task_status=StatusChoices.COMPLETED,
            sub_task_status=StatusChoices.COMPLETED
        ).exists():

            for sub_next_data in obj.sub_task_next:

                # getting url
                url: str = sub_next_data.get("url")

                # getting method
                method: str = sub_next_data.get("method")

                # getting headers
                headers = obj.response.get("headers")

                # getting payload
                payload = {}

                # getting the payload from response of current instance
                if sub_next_data.get("input_type") == SubTaskInputTypeChoices.CURRENT_RESPONSE:

                    payload = obj.response.get("data")

                # getting the payload from sub_task response
                elif sub_next_data.get("input_type") == SubTaskInputTypeChoices.SUB_TASK_RESPONSE:

                    payload = obj.sub_task.all().values_list("response", flat=True)

                # getting the payload from current response and sub task response
                elif sub_next_data.get("input_type") == SubTaskInputTypeChoices.CURRENT_AND_SUB_TASK_RESPONSE:

                    payload = [obj.response] + obj.sub_task.all().values_list("response", flat=True)

                # getting the payload from custom_input of sub_task_data
                elif sub_next_data.get("input_type") == SubTaskInputTypeChoices.CUSTOM_INPUT:

                    payload = sub_next_data.get("custom_input")

                create_http_task(url, payload, headers=headers, method=method, in_seconds=5)

            obj.sub_task_next = []

            with transaction.atomic():

                obj.save()

        # If obj is not None and obj's sub_task_next is not None and length of sub_task_next is 0 and Checking if current tasks all children's task_status and sub_task_status is Completed
        elif obj and (
            (
                obj.sub_task_next is not None and len(obj.sub_task_next) == 0
            ) or (
                obj.sub_task_next is None
            )
        ) and not Task.objects.filter(
            code__contains=obj.code.split(",")[-1]
        ).exclude(
            id=kwargs.get("id")
        ).exclude(
            task_status=StatusChoices.COMPLETED,
            sub_task_status=StatusChoices.COMPLETED
        ).exists():

            # setting sub_task_status as Completed
            obj.sub_task_status = StatusChoices.COMPLETED

            with transaction.atomic():

                obj.save()

                # If Obj's parent_task is not None then calling check for parent task.
                if obj.parent_task_id is not None:

                    # getting url for check endpoint
                    url = reverse("task-check", kwargs={"id": obj.parent_task_id})

                    create_http_task(host+url, payload={}, method="PUT")

                    return Response(data={"detail": "The current task's sub-tasks have been compeleted. Now we are initiating the same check for current task's parent_task."}, status=status.HTTP_200_OK)

                # If obj is Root Node then we will delete the instance
                elif obj.parent_task_id is None:

                    obj.delete()

            return Response(data={"detail": "This task's sub-tasks have been completed."}, status=status.HTTP_200_OK)

        return Response(data={"detail": "This task's sub-tasks are still pending."}, status=status.HTTP_200_OK)


class TaskDeleteAPIView(DestroyAPIView):
    """
    delete: Task DELETE\n
    An API Endpoint to delete parent task that is Completed. Only Task that has no parent task and task status are Completed or Errors and sub task status are Completed or Errors can only be Deleted.
    """
    def get_object(self):

        try:

            # Filtering Task that has no parent task and task status are Completed or Errors and sub task status are Completed or Errors 
            return Task.objects.filter(parent_task_id=None, task_status__in=[StatusChoices.COMPLETED, StatusChoices.ERRORS], sub_task_status__in=[StatusChoices.COMPLETED, StatusChoices.ERRORS]).get(id=self.kwargs.get("id"))

        except ObjectDoesNotExist as exc:

            raise ObjectNotFound(exc)

        except MultipleObjectsReturned as exc:

            raise ServerError(exc)

    def perform_destroy(self, instance):

        try:

            instance.delete()

        except ProtectedError as exc:

            raise CannotDelete(exc)

        except (FieldDoesNotExist, FieldError, IntegrityError) as exc:

            raise ServerError(exc)
