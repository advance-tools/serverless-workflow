An API Endpoint to delete parent task that is Completed. Only Task that has no parent task and task status are Completed or Errors and sub task status are Completed or Errors can only be Deleted.
    
    | Validation | Error Code | Error Messages |
    | Task with given id Exists .| 404 | Task with given id does not Exists. |
    | If the given user exists | 404 | User with given id does not exists.|
    | Parent task is null | 400 | Task is not root node and has Parent Task. |
    | Task status and Sub task status is COMPLETED or ERROR | 403 | Task status is PENDING. (task_status:0 or sub_task_status:0) |