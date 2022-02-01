from django.db import models
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager
from django.contrib.postgres.fields import ArrayField
from task_services.choices import StatusChoices
from datetime import datetime
from uuid import UUID, uuid4
from typing import Optional, Dict, Any, List

# Create your models here.

class UserManager(BaseUserManager):

    def create(self, email, password=None, **extra_fields):

        if not email:
            raise ValueError('Users must have an email address')

        if not password:
            raise ValueError('Users must have a password')

        user = self.model(email=self.normalize_email(email), **extra_fields)

        user.is_staff       = False
        user.is_superuser   = False

        user.set_password(password)

        user.save(using=self._db)

        return user

    def create_superuser(self, email, password, **extra_fields):

        if not email:
            raise ValueError('Users must have an email address')

        if not password:
            raise ValueError('Users must have a password')

        user = self.model(email=self.normalize_email(email), **extra_fields)

        user.is_staff       = True
        user.is_superuser   = True

        user.set_password(password)

        user.save(using=self._db)

        return user


class User(AbstractBaseUser):

    id: UUID                = models.UUIDField(primary_key=True, editable=False, default=uuid4)
    email: str              = models.EmailField(max_length=255, unique=True, default="abc@gmail.com")
    name: str               = models.CharField(max_length=100)
    active: bool            = models.BooleanField(default=True)
    timestamp: datetime     = models.DateTimeField(auto_now_add=True)
    USERNAME_FIELD          = 'email'
    REQUIRED_FIELDS         = ['name']
    
    objects                 = UserManager()

    def __str__(self):
        return self.email

    def is_active(self):
        return self.active

    def has_perm(self, perm, obj=None):
        return True

    def has_module_perms(self, app_label):
        return True


class Task(models.Model):

    id: str                             = models.CharField(max_length=250, primary_key=True)
    parent_task                         = models.ForeignKey("self", null=True, on_delete=models.CASCADE, related_name="sub_task") # type: Task
    my_user: User                       = models.ForeignKey(User, on_delete=models.CASCADE, related_name="tasks")
    task_status: int                    = models.IntegerField(choices=StatusChoices.choices, default=StatusChoices.PENDING)
    sub_task_status: int                = models.IntegerField(choices=StatusChoices.choices, default=StatusChoices.PENDING)

    code: str                           = models.TextField()

    request: Optional[Dict[str, Any]]   = models.JSONField(null=True)
    response: Optional[Dict[str, Any]]  = models.JSONField(null=True)

    immediate_next: Optional[List[Dict[str, Any]]] = ArrayField(models.JSONField(null=True), null=True)
    sub_task_next: Optional[List[Dict[str, Any]]]  = ArrayField(models.JSONField(null=True), null=True)

    buffer_immediate_next   = ArrayField(models.JSONField(null=True), null=True)
    buffer_sub_task_next    = ArrayField(models.JSONField(null=True), null=True)

    created_at: datetime    = models.DateTimeField(auto_now_add=True)
    updated_at: datetime    = models.DateTimeField(auto_now=True)

    objects                 = models.Manager()

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields  = ['my_user','code'],
                name    = "Unique_User-Code"
            )
        ]

    def __str__(self):
        return f"{self.id} {self.task_status} {self.sub_task_status}"
