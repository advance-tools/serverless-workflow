This endpoint will return all the task Initiated by user.

    field name          | method | lookup | example
    --------------------|--------|-------------|----------
    id                  | filter or exclude | in | 1. ?id=`58b346e6-7b83-4ab6-8da4-d97399e15dbc`,<br> 2. ?exclude:id=`58b346e6-7b83-4ab6-8da4-d97399e15dbc`
    parent_task         | filter or exclude | in, isnull | 1. ?parent_task='58b346e6-7b83-4ab6-8da4-d97399e15dbc'<br> 2.?parent_task.isnull=tru
    task_status         | filter or exclude | in | 1. ?task_status=0 <br> 2. ?exclude:task_status=2
    code                | filter or exclude | in, contains, icontains, exact, iexact, startswith, endswith | 1. ?code.startswith=`registartion--58b346e6-7b83-4ab6-8da4-d97399e15dbc`
    created_at          | filter or exclude | lte, gte, gt, lt, range, startswith, endswith, in            | 1. ?created_at.lte=`2020-03-22`,<br> 2. ?filter:created_at.gte=`2020-03-22`, <br> 3. ?exclude:created_at.range=`2020-03-22,2020-11-26`