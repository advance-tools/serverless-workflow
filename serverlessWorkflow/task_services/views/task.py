from rest_framework import status
from rest_framework.generics import CreateAPIView, UpdateAPIView, ListAPIView, DestroyAPIView
from rest_framework.permissions import AllowAny
from rest_framework.pagination import CursorPagination
from rest_framework.exceptions import APIException

from django.core.exceptions import FieldDoesNotExist, FieldError, ObjectDoesNotExist, MultipleObjectsReturned
from django.db import IntegrityError, transaction
from django.db.models.deletion import ProtectedError
from django.db.transaction import TransactionManagementError

from drf_spectacular.utils import extend_schema, extend_schema_view
from querybuilder import querybuilder
from serverlessWorkflow.task import create_http_task
from task_services.exceptions import ServerError, ObjectNotFound, CannotDelete
from task_services.models import Task, User
from task_services.serializers.task import InitTaskSerializer, CompleteTaskSerializer, ListTaskSerializer

from uuid import uuid4


with open('./task_services/views/docs/task/task_list.md') as f:
    task_list = f.read()

@extend_schema_view(
    get=extend_schema(
        tags=['Task'],
        summary='List All Tasks',
        description=task_list,
    ),
)
class TaskListAPIView(ListAPIView):
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



with open('./task_services/views/docs/task/task_init.md') as f:
    task_init = f.read()

@extend_schema_view(
    post=extend_schema(
        tags=['Task'],
        summary='Register Initialization of Task from Node',
        description=task_init,
    ),
)
class TaskInitAPIView(CreateAPIView):
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



with open('./task_services/views/docs/task/task_completed.md') as f:
    task_completed = f.read()

@extend_schema_view(
    put=extend_schema(
        tags=['Task'],
        summary='Register Completion of Task from Node',
        description=task_completed,
    ),
)
class TaskCompletedAPIView(UpdateAPIView):
    serializer_class            = CompleteTaskSerializer
    permission_classes: tuple   = (AllowAny,)
    http_method_names           = ['put', 'head', 'option']

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

        except Exception as exc:
            print(exc)
            raise ServerError(exc)



with open('./task_services/views/docs/task/task_retry.md') as f:
    task_retry = f.read()

@extend_schema_view(
    delete=extend_schema(
        tags=['Task'],
        summary='Retry Task',
        description=task_retry,
        request=None,
        responses=None
    ),
)
class TaskRetryAPIView(DestroyAPIView):
    permission_classes: tuple   = (AllowAny,)

    def get_object(self):

        try:

            return Task.objects.get(id=self.kwargs.get("id"))
        
        except ObjectDoesNotExist as exc:

            raise ObjectNotFound(exc)

        except MultipleObjectsReturned as exc:

            raise ServerError(exc)
    
    def perform_destroy(self, instance: Task):
        
        # if User.objects.filter(id=self.kwargs.get('my_user')).exists():

        #     if instance.parent_task != None:
                    
        #         raise APIException(detail=f"Task is not root task and has parent task with id: {instance.parent_task.id}.", code=status.HTTP_400_BAD_REQUEST)
        # else:

        #     raise APIException(detail=f"User with id: {self.kwargs.get('my_user')} does not exists.", code=status.HTTP_400_BAD_REQUEST)
        
        # find children task of given id with task status ERRORS.
        # error_tasks = Task.objects.filter(code__startswith=instance.code, task_status=StatusChoices.ERRORS).order_by('created_at')
        error_tasks = Task.objects.filter(id=instance.id) #filter(code__startswith=instance.code, task_status=StatusChoices.ERRORS).order_by('created_at')
        
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



with open('./task_services/views/docs/task/task_delete.md') as f:
    task_delete = f.read()

@extend_schema_view(
    delete=extend_schema(
        tags=['Task'],
        summary='Delete Task',
        description=task_delete,
        request=None,
        responses=None
    ),
)
class TaskDeleteAPIView(DestroyAPIView):
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
        
        # if Task.objects.filter(
        #     code__startswith=instance.code,
        # ).alias(
        #     has_children=Exists(Task.objects.filter(parent_task=OuterRef('id')))
        # ).filter(
        #     has_children=False,
        #     task_status__in=[StatusChoices.COMPLETED, StatusChoices.ERRORS],
        #     sub_task_status__in=[StatusChoices.COMPLETED, StatusChoices.ERRORS]
        # ).exists():


        # if Task.objects.filter(
        #     code__startswith=instance.code,
        # ).alias(
        #     has_children=Exists(Task.objects.filter(parent_task=OuterRef('id')))
        # ).filter(
        #     has_children=False,
        # ).filter(
        #     Q(task_status__in=[StatusChoices.COMPLETED, StatusChoices.ERRORS]) |
        #     Q(sub_task_status__in=[StatusChoices.COMPLETED, StatusChoices.ERRORS])
        # ).exists():
            
        try:
            
            instance.delete()
        
        except ProtectedError as exc:
            
            raise CannotDelete(exc)

        except (FieldDoesNotExist, FieldError, IntegrityError) as exc:
            
            raise ServerError(exc)
        # else:
            
        #     raise APIException(detail="Task status or sub task status is PENDING.", code=status.HTTP_400_BAD_REQUEST)
        