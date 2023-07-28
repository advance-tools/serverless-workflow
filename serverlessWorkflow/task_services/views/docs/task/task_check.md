An api endpoint to Check Task's Completion.

    ## Things happening in this endpoint:
    * Checking if all the children's `task_status` and `sub_task_status` is **Completed** of the Current Task and Current Task's `sub_task_next's length` is greater than **0**.
        * then all the Sub Task will be triggered one by one.
    * Checking if all the children's `task_status` and `sub_task_status` is **Completed** of the Current Task and Current Task's `sub_task_next's length` is **0**.
        * then `SubTaskStatus` of the Current Task will be Marked as **Completed**.
        * Checking if Current Task's `parent_task` is **not None**.
            * then triggering check for the parent_task.
        * Checking if Current Task's `parent_task` is **None**.
            * **Deleting** the `Current Task` and its `Children`.