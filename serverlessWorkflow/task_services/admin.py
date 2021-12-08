from django.contrib import admin

# Register your models here.
from task_services.models import Task

class TaskAdmin(admin.ModelAdmin):
    list_display = ('id', 'parent_task', 'task_status', 'sub_task_status', 'code')
    ordering = ('code',)

admin.site.register(Task, TaskAdmin)
