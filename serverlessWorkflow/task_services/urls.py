from django.urls import path

from task_services.views.task import TaskInitAPIView, TaskCompletedAPIView, TaskCheckAPIView, TaskDeleteAPIView, ChoicesAPIView


urlpatterns = [
    path("choices", ChoicesAPIView.as_view(), name="task-choices"),
    path("init", TaskInitAPIView.as_view(), name="task-init"),
    path("complete", TaskCompletedAPIView.as_view(), name="task-complete"),
    path("check/<str:id>", TaskCheckAPIView.as_view(), name="task-check"),
    path("delete/<str:id>", TaskDeleteAPIView.as_view(), name="task-delete")
]
