from rest_framework import status
from rest_framework.generics import CreateAPIView, UpdateAPIView, ListAPIView, DestroyAPIView
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import AllowAny
from rest_framework.pagination import CursorPagination
from rest_framework.exceptions import APIException

from django.core.exceptions import FieldDoesNotExist, FieldError, ObjectDoesNotExist, MultipleObjectsReturned
from django.db import IntegrityError, transaction
from django.db.models import Exists, OuterRef 
from django.db.models.deletion import ProtectedError
from django.db.transaction import TransactionManagementError

from querybuilder import querybuilder
from serverlessWorkflow.task import create_http_task
from task_services.exceptions import ServerError, ObjectNotFound, CannotDelete 
from task_services.choices import StatusChoices, ImmediateInputTypeChoices, SubTaskInputTypeChoices
from task_services.models import Task, User
from task_services.serializers.task import InitTaskSerializer, CompleteTaskSerializer, ChoicesSerializer, ListTaskSerializer

from uuid import uuid4


class ChoicesAPIView(APIView):
    """
    get: Task Choices\n
    This endpoint will return all the Choices need in Task.
    """
    serializer_class = ChoicesSerializer

    def get(self, request, *args, **kwargs):

        data = {
            "status_choices"                : dict(StatusChoices.choices),
            "immediate_input_type_choices"  : dict(ImmediateInputTypeChoices.choices),
            "sub_task_input_type_choices"   : dict(SubTaskInputTypeChoices.choices)
        }

        return Response(data=data, status=status.HTTP_200_OK)


class TaskListAPIView(ListAPIView):
    """
    get: Task List\n
    This endpoint will return all the task Initiated by user.

    field name          | method | lookup | example
    --------------------|--------|-------------|----------
    id                  | filter or exclude | in | 1. ?id=`58b346e6-7b83-4ab6-8da4-d97399e15dbc`,<br> 2. ?exclude:id=`58b346e6-7b83-4ab6-8da4-d97399e15dbc`
    parent_task         | filter or exclude | in, isnull | 1. ?parent_task='58b346e6-7b83-4ab6-8da4-d97399e15dbc'<br> 2.?parent_task.isnull=tru
    task_status         | filter or exclude | in | 1. ?task_status=0 <br> 2. ?exclude:task_status=2
    code                | filter or exclude | in, contains, icontains, exact, iexact, startswith, endswith | 1. ?code.startswith=`registartion--58b346e6-7b83-4ab6-8da4-d97399e15dbc`
    created_at          | filter or exclude | lte, gte, gt, lt, range, startswith, endswith, in            | 1. ?created_at.lte=`2020-03-22`,<br> 2. ?filter:created_at.gte=`2020-03-22`, <br> 3. ?exclude:created_at.range=`2020-03-22,2020-11-26`
    """
    serializer_class            = ListTaskSerializer
    permission_classes: tuple   = (AllowAny,)
    pagination_class            = CursorPagination
    valid_pairs                 = {
        "id"                        : ["in"],
        "parent_task"               : ["in","isnull"],
        "task_status"               : ["in"],
        "code"                      : ["icontains", "contains", "in", "exact", "iexact", "startswith", "endswith"],
        "created_at"                : ["lte", "gte", "gt", "lt", "range", "in", "contains", "icontains"],
    }
    ordering: tuple             = ('-created_at',)

    def get_queryset(self):

        try:

            queryset    = Task.objects.filter(my_user=self.kwargs.get('my_user'))

            queries     = querybuilder(queryset, self.request.GET, self.valid_pairs)

            if queries is False:

                raise APIException(detail="Invalid QueryParams!!", code=status.HTTP_400_BAD_REQUEST)

            self.only = queries.get("only")

            return queries.get("queryset")

        except (FieldDoesNotExist, FieldError) as exc:

            raise ServerError(exc)

    
class TaskInitAPIView(CreateAPIView):
    """
    post: Task Init POST\n
    An api endpoint to Initiate Tasks.

    | Validation | Error Code | Error Messages |
    | Primary Key(id) should be Unique. The format of Id should be UUID and you cannot re-enter the id. | 406 | Task with given id already exists. |
    | If the given user exists | 404 | User with given id does not exists. |
    | User of current task and it`s parent task should be same if exists.| 400 | Parent Task of Current task is not valid |
    """
    serializer_class            = InitTaskSerializer
    permission_classes:tuple    = (AllowAny,)
    
    def get_queryset(self):

        return Task.objects.filter(my_user=self.kwargs.get("my_user"))

    def perform_create(self, serializer: InitTaskSerializer):

        try:

            if serializer.is_valid(raise_exception=True):

                with transaction.atomic():

                    code = serializer.validated_data.get("code")

                    # checking if parent_task is not None
                    if serializer.validated_data.get("parent_task"):

                        # updating parent_code
                        parent_codes: str = serializer.validated_data.get("parent_task").code
                    
                        # concating string
                        code = parent_codes + f",{uuid4()}"
                    
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
    | Task with given id exists | 404 | Task with given id does not exists. |
    | If the given user exists | 404 | User with given id does not exists. |
    | User of current task and it`s parent task should be same if exists.| 400 | Parent Task of Current task is not valid |
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
    serializer_class            = CompleteTaskSerializer
    permission_classes: tuple   = (AllowAny,)

    def get_queryset(self):

        return Task.objects.filter(my_user=self.kwargs.get("my_user"))

    def get_object(self):
        
        try:

            return self.get_queryset().get(id=self.kwargs.get("id"))

        except ObjectDoesNotExist as exc:

            raise ObjectNotFound(exc)

        except MultipleObjectsReturned as exc:

            raise ServerError(exc)

    def perform_update(self, serializer: CompleteTaskSerializer):

        try:

            if serializer.is_valid(raise_exception=True):

                with transaction.atomic():

                    # save model
                    return serializer.save()

        except (FieldDoesNotExist, FieldError, TransactionManagementError, IntegrityError, AttributeError) as exc:

            raise ServerError(exc)


class TaskRetryAPIView(DestroyAPIView):
    """
    delete:Task DELETE and RETRY 
    This endpoint will delete the specified task if task_status is error and Retry with same payload.
    
    | Validation | Error Code | Error Messages |
    | Task with given id Exists .| 404 | Task with given id does not Exists. |
    | If the given user exists | 404 | User with given id does not exists.|
    | Parent task is null | 400 | Task is not root node and has Parent Task. |
    | Task status is Error | 400 | Task is Completed or Pending. Only Task having status Error can be retry. |
    """
    permission_classes: tuple   = (AllowAny,)

    def get_object(self):

        try:

            return Task.objects.get(id=self.kwargs.get("id"))
        
        except ObjectDoesNotExist as exc:

            raise ObjectNotFound(exc)

        except MultipleObjectsReturned as exc:

            raise ServerError(exc)
    
    def perform_destroy(self, instance: Task):

        if User.objects.filter(id=self.kwargs.get('my_user')).exists():

            if instance.parent_task != None:
                    
                raise APIException(detail=f"Task is not root task and has parent task with id: {instance.parent_task.id}.", code=status.HTTP_400_BAD_REQUEST)
        else:

            raise APIException(detail=f"User with id: {self.kwargs.get('my_user')} does not exists.", code=status.HTTP_400_BAD_REQUEST)
        
        # find children task of given id with task status ERRORS.
        error_tasks = Task.objects.filter(code__startswith=instance.code, task_status=StatusChoices.ERRORS).order_by('created_at')
        
        if error_tasks.exists():
            
            task = error_tasks.first()
            
            try:
        
                task.delete()

            except ProtectedError as exc:
                
                raise CannotDelete(exc)
            
            except (FieldDoesNotExist, FieldError, IntegrityError) as exc:
                
                raise ServerError(exc)
            
            create_http_task(url=task.request['url'], payload=task.request['payload'], headers=task.request['headers'], method=task.request['method'])

        else:

            raise APIException(detail="Task has Completed or Pending status\n Only Task having status Error can be retried.", code=status.HTTP_400_BAD_REQUEST)


class TaskDeleteAPIView(DestroyAPIView):
    """
    delete: Task DELETE\n
    An API Endpoint to delete parent task that is Completed. Only Task that has no parent task and task status are Completed or Errors and sub task status are Completed or Errors can only be Deleted.
    
    | Validation | Error Code | Error Messages |
    | Task with given id Exists .| 404 | Task with given id does not Exists. |
    | If the given user exists | 404 | User with given id does not exists.|
    | Parent task is null | 400 | Task is not root node and has Parent Task. |
    | Task status and Sub task status is COMPLETED or ERROR | 403 | Task status is PENDING. (task_status:0 or sub_task_status:0) |
    """
    permission_classes: tuple   = (AllowAny,)
    
    def get_object(self):

        try:
            
            return Task.objects.get(id=self.kwargs.get("id"))
        
        except ObjectDoesNotExist as exc:

            raise ObjectNotFound(exc)

        except MultipleObjectsReturned as exc:

            raise ServerError(exc)
    
    def perform_destroy(self,instance):

        if User.objects.filter(id=self.kwargs.get('my_user')).exists():
                
            if instance.parent_task != None:
                    
                raise APIException(detail=f"Task is not root task and has parent task with id: {instance.parent_task.id}.", code=status.HTTP_400_BAD_REQUEST)
                
        else:
                
            raise APIException(detail=f"User with id: {self.kwargs.get('my_user')} does not exists.", code=status.HTTP_400_BAD_REQUEST)
        
        if Task.objects.filter(
            code__startswith=instance.code,
        ).annotate(
            has_children=Exists(Task.objects.filter(parent_task=OuterRef('id')))
        ).filter(
            has_children=False,
            task_status__in=[StatusChoices.COMPLETED, StatusChoices.ERRORS],
            sub_task_status__in=[StatusChoices.COMPLETED, StatusChoices.ERRORS]
        ).exists():
            
            try:
                
                instance.delete()
            
            except ProtectedError as exc:
                
                raise CannotDelete(exc)

            except (FieldDoesNotExist, FieldError, IntegrityError) as exc:
                
                raise ServerError(exc)
        else:
            
            raise APIException(detail="Task status or sub task status is PENDING.", code=status.HTTP_400_BAD_REQUEST)
        