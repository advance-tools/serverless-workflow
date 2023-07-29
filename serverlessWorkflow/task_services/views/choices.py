from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response

from drf_spectacular.utils import extend_schema, extend_schema_view, inline_serializer
from rest_framework import serializers
from task_services.choices import StatusChoices, ImmediateInputTypeChoices, SubTaskInputTypeChoices
from task_services.serializers.task import ChoicesSerializer


with open('./task_services/views/docs/choices/choices.md') as f:
    task_choice = f.read()

@extend_schema_view(
    get=extend_schema(
        tags=['Choices'],
        summary='List all Choices of the APIs',
        description=task_choice,
        request=None,
        responses=inline_serializer(name='ChoicesAPISerializer', fields={
            'data': serializers.JSONField(),
        }),
    ),
)
class ChoicesAPIView(APIView):
    serializer_class = ChoicesSerializer

    def get(self, request, *args, **kwargs):

        data = {
            "status_choices"                : dict(StatusChoices.choices),
            "immediate_input_type_choices"  : dict(ImmediateInputTypeChoices.choices),
            "sub_task_input_type_choices"   : dict(SubTaskInputTypeChoices.choices)
        }

        return Response(data=data, status=status.HTTP_200_OK)
