from django.urls import path
from task_services.views.profile import ProfileAPIView
from task_services.views.user import UserListCreateAPIView, UserRetrieveUpdateDeleteAPIView
from task_services.views.task import TaskInitAPIView, TaskCompletedAPIView, TaskRetryAPIView, TaskDeleteAPIView, TaskListAPIView, TaskRetryAPIView
from task_services.views.choices import ChoicesAPIView
from task_services.views.check import TaskCheckAPIView

urlpatterns = [
    path("users", UserListCreateAPIView.as_view(), name='create-user'),
    path("users/<str:pk>", UserRetrieveUpdateDeleteAPIView.as_view(), name='rud-user'),
    path("profile", ProfileAPIView.as_view(), name='profile-create'),
    path("choices", ChoicesAPIView.as_view(), name="task-choices"),
    
    path("tasks/<str:my_user>", TaskListAPIView.as_view(), name="task-list"),
    path("tasks/init/<str:my_user>", TaskInitAPIView.as_view(), name="task-init"),
    path("tasks/complete/<str:my_user>/<str:id>", TaskCompletedAPIView.as_view(), name="task-complete"),
    path("tasks/check/<str:my_user>/<str:id>", TaskCheckAPIView.as_view(), name="task-check"),
    path("tasks/retry/<str:my_user>/<str:id>", TaskRetryAPIView.as_view(), name="task-retry"),
    path("tasks/delete/<str:my_user>/<str:id>", TaskDeleteAPIView.as_view(), name="task-delete")
]
