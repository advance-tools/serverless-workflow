from django.db import models


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

