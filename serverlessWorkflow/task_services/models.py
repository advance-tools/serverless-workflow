from django.db import models
from django.contrib.postgres.fields import ArrayField

from tasks.create import create_http_task

from uuid import uuid4


localtunnel_url = "https://8010.9a1249e76586779ebe526fe618468e04.codespace.advancedware.in"
# Create your models here.

class StatusChoices(models.IntegerChoices):
    PENDING                         = 0
    COMPLETED                       = 1
    ERRORS                          = 2


class ImmediateInputTypeChoices(models.IntegerChoices):
    NONE                            = 0
    CURRENT_RESPONSE                = 1
    CUSTOM_INPUT                    = 2


class SubTaskInputTypeChoices(models.IntegerChoices):
    NONE                            = 0
    CURRENT_RESPONSE                = 1
    SUB_TASK_RESPONSE               = 2
    CURRENT_AND_SUB_TASK_RESPONSE   = 3
    CUSTOM_INPUT                    = 4


class Task(models.Model):

    id: str                 = models.CharField(max_length=250, primary_key=True)
    parent_task             = models.ForeignKey("self", null=True, on_delete=models.CASCADE, related_name="sub_task") # type: Task

    task_status: int        = models.IntegerField(choices=StatusChoices.choices, default=StatusChoices.PENDING)
    sub_task_status: int    = models.IntegerField(choices=StatusChoices.choices, default=StatusChoices.PENDING)

    code: str               = models.TextField()

    request                 = models.JSONField(null=True)
    response: dict          = models.JSONField(null=True)

    immediate_next: list    = ArrayField(models.JSONField(null=True), null=True)
    sub_task_next: list     = ArrayField(models.JSONField(null=True), null=True)

    buffer_immediate_next   = ArrayField(models.JSONField(null=True), null=True)
    buffer_sub_task_next    = ArrayField(models.JSONField(null=True), null=True)

    objects                 = models.Manager()

    def __str__(self):
        return f"{self.id} {self.task_status} {self.sub_task_status}"

