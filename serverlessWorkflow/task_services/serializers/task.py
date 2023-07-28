from rest_framework import serializers

from django.conf import settings

from task_services.models import Task, User
from task_services.choices import StatusChoices, ImmediateInputTypeChoices, SubTaskInputTypeChoices

from serverlessWorkflow.task import create_http_task

from typing import Dict, Any
from collections import OrderedDict


class ChoicesSerializer(serializers.Serializer):
    pass


class RequestSerializer(serializers.Serializer):

    url                             = serializers.CharField(max_length=10000, help_text="URL of the Request.")
    method                          = serializers.CharField(max_length=20, help_text="Method of the Request.")
    payload                         = serializers.JSONField(allow_null=True,help_text="Payload of the Request.")
    headers                         = serializers.JSONField(help_text="Header of the Request.")

    def validate_url(self, value):

        if value.startswith("http://"):
            value = value.replace("http://","https://")

        return value

class ImmediateNextSerializer(serializers.Serializer):
    url                             = serializers.CharField(max_length=10000, help_text="URL of Immediate Next Task.")
    method                          = serializers.CharField(max_length=20, help_text="Method of Immediate Next Task.")

    input_type                      = serializers.ChoiceField(choices=ImmediateInputTypeChoices.choices, help_text="Input Type of the Immediate Next Task.")
    custom_input                    = serializers.JSONField(allow_null=True, help_text="Custom Input of the Immediate Next Task.")

    def validate_url(self, value):

        if value.startswith("http://"):
            value = value.replace("http://","https://")

        return value

class SubTaskSerializer(serializers.Serializer):
    url                             = serializers.CharField(max_length=10000, help_text="Url of Sub Task.")
    method                          = serializers.CharField(max_length=20, help_text="Method of Sub Task.")

    input_type                      = serializers.ChoiceField(choices=SubTaskInputTypeChoices.choices, help_text="Input Type of the Sub Task.")
    custom_input                    = serializers.JSONField(allow_null=True, help_text="Custom Input of the Sub Task.")

    def validate_url(self, value):

        if value.startswith("http://"):
            value = value.replace("http://","https://")

        return value
        
class ResponseSerializer(serializers.Serializer):
    status_code                     = serializers.IntegerField(help_text="Status Code of the Response.")
    headers                         = serializers.JSONField(help_text="Headers of the Response.")
    data                            = serializers.JSONField(allow_null=True, help_text="Response Data.")


class ListTaskSerializer(serializers.ModelSerializer):
    id                              = serializers.CharField(max_length=250)
    parent_task                     = serializers.PrimaryKeyRelatedField(read_only=True, allow_null=True, help_text="Primary Key of the Parent Task.")
    task_status                     = serializers.ChoiceField(required=False, choices=StatusChoices.choices, default=StatusChoices.PENDING, help_text="Status of the Task.")
    sub_task_status                 = serializers.ChoiceField(required=False, choices=StatusChoices.choices, default=StatusChoices.PENDING, help_text="Status of the Sub Task.")

    code                            = serializers.CharField(read_only=True, help_text="Code of Current Task and Parent Tasks.")

    request                         = serializers.JSONField(allow_null=True)
    response: dict                  = serializers.JSONField(allow_null=True)
    immediate_next                  = ImmediateNextSerializer(many=True, required=False, allow_null=True, help_text="Immediate Next List. All the Immediate Next endpoints will be called one by one once the task_status is Completed.")
    sub_task_next                   = SubTaskSerializer(many=True, required=False, allow_null=True, help_text="Sub Task Next List. All the Sub Task Next endpoints will be called one by one once all children's task_status and sub_task_status is Completed.")

    created_at                      = serializers.DateTimeField(read_only=True)
    updated_at                      = serializers.DateTimeField(read_only=True)

    class Meta:
        model = Task
        fields = [
            "id",
            "parent_task",
            "task_status",
            "sub_task_status",
            "code",

            "request",
            "response",
            "immediate_next",
            "sub_task_next",

            "created_at",
            "updated_at"
        ]


class InitTaskSerializer(serializers.ModelSerializer):
    id                              = serializers.CharField(max_length=250)
    my_user                         = serializers.PrimaryKeyRelatedField(queryset=User.objects.all(),allow_null=False,help_text="Primary Key of User.")
    parent_task                     = serializers.PrimaryKeyRelatedField(queryset=Task.objects.all(), allow_null=True, help_text="Primary Key of the Parent Task.")

    request                         = RequestSerializer(allow_null=True, help_text="Request Object.")

    task_status                     = serializers.ChoiceField(required=False, choices=StatusChoices.choices, default=StatusChoices.PENDING, help_text="Status of the Task.")
    sub_task_status                 = serializers.ChoiceField(required=False, choices=StatusChoices.choices, default=StatusChoices.PENDING, help_text="Status of the Sub Task.")

    code                            = serializers.CharField(required=False, help_text="Code of Current Task and Parent Tasks.")

    class Meta:
        model = Task
        fields = [
            "id",
            "my_user",
            "parent_task",

            "request",

            "task_status",
            "sub_task_status",

            "code",
        ]
    
    def validate_request(self, value: Dict[str, Any]) -> dict:
        
        return dict(value)

    def validate_id(self, value: str) -> str:
                
        # Checking if Task with the given id already exists.
        if Task.objects.filter(id=value).exists():
            
            # raise error
            raise serializers.ValidationError(detail=f"Task with id: {value} already exists.")
        
        return value
    
    def validate_my_user(self, value: User) -> User:
        
        # Checking if the given user exists.
        if User.objects.filter(id=value.id).exists():
            
            return value
    
        raise serializers.ValidationError(detail=f"User with id: {value.id} does not exists.")
    
    def validate(self, data: OrderedDict) -> OrderedDict:
        
        if data['parent_task']:

            # Check for user of current task and parent task is same if exists.
            if Task.objects.filter(id=data['parent_task'].id).exists():
                
                parent_task_user = Task.objects.get(id=data['parent_task'].id).my_user

                
                if data['my_user'] != parent_task_user:

                    raise serializers.ValidationError("Parent Task of Current task is not valid")
        
        return data
    
        
class CompleteTaskSerializer(serializers.ModelSerializer):
    id                              = serializers.CharField(max_length=250)
    my_user                         = serializers.PrimaryKeyRelatedField(queryset=User.objects.all(),allow_null=False,help_text="Primary Key of User.")
    parent_task                     = serializers.PrimaryKeyRelatedField(queryset=Task.objects.all(), allow_null=True, help_text="Primary Key of the Parent Task.")

    response                        = ResponseSerializer(allow_null=True, required=False, help_text="Response Object")

    immediate_next                  = ImmediateNextSerializer(many=True, required=False, allow_null=True, help_text="Immediate Next List. All the Immediate Next endpoints will be called one by one once the task_status is Completed.")
    sub_task_next                   = SubTaskSerializer(many=True, required=False, allow_null=True, help_text="Sub Task Next List. All the Sub Task Next endpoints will be called one by one once all children's task_status and sub_task_status is Completed.")

    code                            = serializers.CharField(read_only=True, help_text="Code of Current Task and Parent Tasks.")

    class Meta:
        model = Task
        fields = [
            "id",
            "my_user",
            "parent_task",
            "response",

            "immediate_next",
            "sub_task_next",

            "code"
        ]

    def validate_id(self, value: str) -> str:
    
        if Task.objects.filter(id=value).exists():

            return value
        
        raise serializers.ValidationError(detail=f"Task with id: {value} does not exists.")

    def validate_my_user(self, value: User) -> User:

        if User.objects.filter(id=value.id).exists():

            return value
        # print(f"User with id: {value.id} does not exists.")
        raise serializers.ValidationError(detail=f"User with id: {value.id} does not exists.")

    def validate(self, data: OrderedDict) -> OrderedDict:
        
        if data['parent_task']:

            if Task.objects.filter(id=data['parent_task'].id).exists():
            
                parent_task_user = Task.objects.get(id=data['parent_task'].id).my_user

                if data['my_user'] != parent_task_user:
                    # print("Parent Task of Current task is not valid")
                    raise serializers.ValidationError("Parent Task of Current task is not valid")

        # If ImmediateNext is None or []
        if data.get("immediate_next") is None or len(data["immediate_next"]) == 0:

            # then SubTaskNext should be None or [] as well.
            if data.get("sub_task_next") is not None and len(data["sub_task_next"]) != 0:
                # print("Sub Task Next should be None when Immediate Next is None.")
                # raise error
                raise serializers.ValidationError(detail="Sub Task Next should be None when Immediate Next is None.")

        return data

    def update(self, instance: Task, validated_data: OrderedDict) -> Task:
        
        # If response's status_code greater than 299
        if validated_data.get("response").get("status_code") > 299:
            
            # then task_status will be set as Errors
            instance.task_status    = StatusChoices.ERRORS

        # If response's status_code is lesser than 300
        else:

            # then task_status will be set as Completed
            instance.task_status    = StatusChoices.COMPLETED

        instance.response               = validated_data.get("response", instance.response)
        instance.immediate_next         = validated_data.get("immediate_next", instance.immediate_next)
        instance.sub_task_next          = validated_data.get("sub_task_next", instance.sub_task_next)
        
        # to save task_status before calling create_hhtp_task.
        instance.save()

        # If ImmediateNext is None or Length of ImmediateNext is 0 and
        if (instance.immediate_next is None or len(instance.immediate_next) == 0) and instance.parent_task_id is not None:

            instance.sub_task_status = StatusChoices.COMPLETED

            instance.save()

            # 8001
            # print(f"{settings.CURRENT_HOST}/api/tasks/check/{instance.my_user_id}/{instance.parent_task_id}")
            create_http_task(f"{settings.CURRENT_HOST}/api/tasks/check/{instance.my_user_id}/{instance.parent_task_id}", payload={}, method="PUT", in_seconds=5)
        
        elif (instance.immediate_next is None or len(instance.immediate_next) == 0) and instance.parent_task_id is None:

            instance.sub_task_status = StatusChoices.COMPLETED

            instance.save()

            # 8001
            create_http_task(f"{settings.CURRENT_HOST}/api/tasks/check/{instance.my_user_id}/{instance.id}", payload={}, method="PUT", in_seconds=5)

        # Checking if current task's status is Completed
        elif instance.immediate_next is not None and len(instance.immediate_next) > 0 and instance.task_status == StatusChoices.COMPLETED:

            for next_data in instance.immediate_next:

                # Getting the url
                url: str = next_data["url"]

                # Getting the method
                method: str = next_data["method"]

                # Getting the headers
                headers: Dict[str, Any] = instance.response["headers"]

                # Insert Authorization key of user into Target-Authorization key
                if 'Authorization' in headers:
                    headers['Target-Authorization'] = headers['Authorization']
                    
                # Initializing payload as {}
                payload = {}

                # getting the response of current instance
                if next_data.get("input_type") == ImmediateInputTypeChoices.NONE:
                    
                    payload = None

                if next_data.get("input_type") == ImmediateInputTypeChoices.CURRENT_RESPONSE:

                    payload = instance.response.get("data")

                # getting the custom_input from current immediate_data
                elif next_data.get("input_type") == ImmediateInputTypeChoices.CUSTOM_INPUT:

                    payload = next_data.get("custom_input")

                # sending request
                create_http_task(url, payload=payload, method=method, headers=headers)

            # setting immediate_next to [] after calling create_http_task for each immediate_next
            instance.immediate_next = []

            instance.save()

        return instance

