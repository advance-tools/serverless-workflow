from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import AllowAny

from django.conf import settings
from django.urls import reverse

from serverlessWorkflow.task import create_http_task

from task_services.models import Task
from task_services.choices import SubTaskInputTypeChoices, StatusChoices

from typing import Optional


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
    permission_classes: tuple = (AllowAny,)

    def put(self, request, *args, **kwargs):

        obj: Optional[Task] = None

        # Getting Task
        queryset = Task.objects.filter(id=kwargs.get("id"))

        # If queryset exists getting first instance
        if queryset.exists():

            obj = queryset.first()
        
        # If object is not None and 
        # object's sub_task_next is not None or 
        # length of sub_task_next is greater than 0 and 
        # Checking if current tasks all children's task_status and 
        # sub_task_status is Completed
        
        if obj and obj.sub_task_next is not None and len(obj.sub_task_next) > 0 and not Task.objects.filter(
            code__contains=obj.code.split(",")[-1]
        ).exclude(code__endswith=obj.code.split(",")[-1]).exclude(
            task_status=StatusChoices.COMPLETED,
            sub_task_status=StatusChoices.COMPLETED
        ).exists():
            
            for sub_next_data in obj.sub_task_next:
                
                # getting url
                url: str = sub_next_data["url"]

                # getting method
                method: str = sub_next_data["method"]

                # getting headers
                headers = obj.response["headers"]

                # getting payload
                payload = {}

                if sub_next_data["input_type"] == SubTaskInputTypeChoices.NONE:

                    payload = None

                # getting the payload from response of current instance
                if sub_next_data["input_type"] == SubTaskInputTypeChoices.CURRENT_RESPONSE:

                    payload = obj.response["data"]

                # getting the payload from sub_task response
                elif sub_next_data["input_type"] == SubTaskInputTypeChoices.SUB_TASK_RESPONSE:

                    payload = obj.sub_task.all().values_list("response", flat=True)

                # getting the payload from current response and sub task response
                elif sub_next_data["input_type"] == SubTaskInputTypeChoices.CURRENT_AND_SUB_TASK_RESPONSE:

                    payload = [obj.response] + obj.sub_task.all().values_list("response", flat=True)

                # getting the payload from custom_input of sub_task_data
                elif sub_next_data["input_type"] == SubTaskInputTypeChoices.CUSTOM_INPUT:

                    payload = sub_next_data["custom_input"]
                create_http_task(url, payload, headers=headers, method=method, in_seconds=5)

            obj.sub_task_next = []

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
        ).exclude(code__endswith=obj.code.split(",")[-1]).exclude(
            task_status=StatusChoices.COMPLETED,
            sub_task_status=StatusChoices.COMPLETED
        ).exists():
            
            # setting sub_task_status as Completed
            obj.sub_task_status = StatusChoices.COMPLETED
            
            obj.save()

            # If Obj's parent_task is not None then calling check for parent task.
            if obj.parent_task_id is not None:
                
                # getting url for check endpoint
                url = reverse("task-check", kwargs={"my_user":obj.my_user_id,"id": obj.parent_task_id})
                
                create_http_task(settings.CURRENT_HOST + url, payload={}, method="PUT")
                
                return Response(data={"detail": "The current task's sub-tasks have been completed. Now we are initiating the same check for current task's parent_task."}, status=status.HTTP_200_OK)
            
            # If obj is Root Node then we will delete the instance
            elif obj.parent_task_id is None:
                
                obj.delete()

            return Response(data={"detail": "This task's sub-tasks have been completed."}, status=status.HTTP_200_OK)

        return Response(data={"detail": "This task's sub-tasks are still pending."}, status=status.HTTP_200_OK)
