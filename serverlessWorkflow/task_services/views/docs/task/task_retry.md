This endpoint will delete the specified task if task_status is error and Retry with same payload.
    
    | Validation | Error Code | Error Messages |
    | Task with given id Exists .| 404 | Task with given id does not Exists. |
    | If the given user exists | 404 | User with given id does not exists.|
    | Parent task is null | 400 | Task is not root node and has Parent Task. |
    | Task status is Error | 400 | Task is Completed or Pending. Only Task having status Error can be retry. |