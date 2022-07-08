An api endpoint to Mark Task Completed.

    ## Things happening in this endpoint:
    * Checking if TaskStatus is Completed
        * then Triggering all ImmediateNext Tasks One by One
    * Checking if Length of ImmediateNext is 0 or None
        * then Check endpoint is called for the Current Task

    | Validation | Error Code | Error Messages |
    |------------|------------|----------------|
    | Task with given id exists | 404 | Task with given id does not exists. |
    | If the given user exists | 404 | User with given id does not exists. |
    | User of current task and it`s parent task should be same if exists.| 400 | Parent Task of Current task is not valid |
    | If ImmediateNext is None or [] then SubTaskNext should be None or [] | 400 | Sub Task Next should be None when Immediate Next is None. |

    patch: Task Completed PATCH\n
    (PUT Recommended) An api endpoint to Mark Task Completed.

    ## Things happening in this endpoint:
    * Checking if TaskStatus is Completed
        * then Triggering all ImmediateNext Tasks One by One
    * Checking if Length of ImmediateNext is 0 or None
        * then Check endpoint is called for the Current Task

    | Validation | Error Code | Error Messages |
    |------------|------------|----------------|
    | If ImmediateNext is None or [] then SubTaskNext should be None or [] | 400 | Sub Task Next should be None when Immediate Next is None. |