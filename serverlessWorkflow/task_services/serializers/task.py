from rest_framework import serializers, status

from task_services.models import Task, StatusChoices, ImmediateInputTypeChoices, SubTaskInputTypeChoices
from tasks.create import create_http_task
from task_services.models import localtunnel_url


class ChoicesSerializer(serializers.Serializer):
    pass


class RequestSerializer(serializers.Serializer):

    url                             = serializers.CharField(max_length=10000, help_text="URL of the Request.")
    method                          = serializers.CharField(max_length=20, help_text="Method of the Request.")
    payload                         = serializers.JSONField(help_text="Payload of the Request.")
    headers                         = serializers.JSONField(help_text="Header of the Request.")


class InitTaskSerializer(serializers.ModelSerializer):
    id                              = serializers.CharField(max_length=250)

    parent_task                     = serializers.PrimaryKeyRelatedField(queryset=Task.objects.all(), allow_null=True, help_text="Primary Key of the Parent Task.")

    request                         = RequestSerializer(allow_null=True, help_text="Request Object.")

    task_status                     = serializers.ChoiceField(required=False, choices=StatusChoices.choices, default=StatusChoices.PENDING, help_text="Status of the Task.")
    sub_task_status                 = serializers.ChoiceField(required=False, choices=StatusChoices.choices, default=StatusChoices.PENDING, help_text="Status of the Sub Task.")

    code                            = serializers.CharField(read_only=True, help_text="Code of Current Task and Parent Tasks.")

    class Meta:
        model = Task
        fields = [
            "id",

            "parent_task",

            "request",

            "task_status",
            "sub_task_status",

            "code",
        ]

    def validate_request(self, value):

        return dict(value)

    def validate_id(self, value):

        # Checking if Task with the given id already exists.
        if Task.objects.filter(id=value).exists():

            # raise error
            raise serializers.ValidationError(detail=f"Task with id: {value} already exists.")

        return value


class ImmediateNextSerializer(serializers.Serializer):
    url                             = serializers.CharField(max_length=10000, help_text="URL of Immediate Next Task.")
    method                          = serializers.CharField(max_length=20, help_text="Method of Immediate Next Task.")

    input_type                      = serializers.ChoiceField(choices=ImmediateInputTypeChoices.choices, help_text="Input Type of the Immediate Next Task.")
    custom_input                    = serializers.JSONField(allow_null=True, help_text="Custom Input of the Immediate Next Task.")


class SubTaskSerializer(serializers.Serializer):
    url                             = serializers.CharField(max_length=10000, help_text="Url of Sub Task.")
    method                          = serializers.CharField(max_length=20, help_text="Method of Sub Task.")

    input_type                      = serializers.ChoiceField(choices=SubTaskInputTypeChoices.choices, help_text="Input Type of the Sub Task.")
    custom_input                    = serializers.JSONField(allow_null=True, help_text="Custom Input of the Sub Task.")


class ResponseSerializer(serializers.Serializer):
    status_code                     = serializers.IntegerField(help_text="Status Code of the Response.")
    headers                         = serializers.JSONField(help_text="Headers of the Response.")
    data                            = serializers.JSONField(help_text="Response Data.")


class CompleteTaskSerializer(serializers.ModelSerializer):
    id                              = serializers.CharField(max_length=250)

    response                        = ResponseSerializer(allow_null=True, required=False, help_text="Response Object")

    immediate_next                  = ImmediateNextSerializer(many=True, required=False, allow_null=True, help_text="Immediate Next List. All the Immediate Next endpoints will be called one by one once the task_status is Completed.")
    sub_task_next                   = SubTaskSerializer(many=True, required=False, allow_null=True, help_text="Sub Task Next List. All the Sub Task Next endpoints will be called one by one once all children's task_status and sub_task_status is Completed.")

    code                            = serializers.CharField(read_only=True, help_text="Code of Current Task and Parent Tasks.")

    class Meta:
        model = Task
        fields = [
            "id",

            "response",

            "immediate_next",
            "sub_task_next",

            "code"
        ]

    def validate(self, data):

        # If ImmediateNext is None or []
        if data.get("immediate_next") is None or len(data.get("immediate_next")) == 0:

            # then SubTaskNext should be None or [] as well.
            if data.get("sub_task_next") is not None and len(data.get("sub_task_next")) != 0:

                # raise error
                raise serializers.ValidationError(detail="Sub Task Next should be None when Immediate Next is None.")

        return data

    def update(self, instance, validated_data):

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
        instance.buffer_immediate_next  = instance.immediate_next
        instance.buffer_sub_task_next   = instance.sub_task_next

        instance.save()

        # If ImmediateNext is None or Length of ImmediateNext is 0 and 
        if (instance.immediate_next is None or len(instance.immediate_next) == 0) and instance.parent_task_id is not None:

            instance.sub_task_status = StatusChoices.COMPLETED

            instance.save()

            # 8007
            create_http_task(f"{localtunnel_url}/task/check/{instance.parent_task_id}", payload={}, method="PUT")

        # Checking if current task's status is Completed
        elif instance.immediate_next is not None and len(instance.immediate_next) > 0 and instance.task_status == StatusChoices.COMPLETED:

            for next_data in instance.immediate_next:

                # Getting the url
                url: str = next_data.get("url")

                # Getting the method
                method: str = next_data.get("method")

                # Getting the headers
                headers = instance.response.get("headers")

                # Initializing payload as {}
                payload = {}

                # getting the response of current instance
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
