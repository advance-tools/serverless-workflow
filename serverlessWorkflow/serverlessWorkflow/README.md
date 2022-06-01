# What is ServerLess Workflow?

## Purpose

The serverless workflow project aims to implement specific set of task in a tree manner. We are using google cloud tasks to achieve our goal. This google cloud task can schedule request in a queue manner with configurable retries.

```
                +---------------+
                |    Endpoint   |
                +---------------+
                        |
            +-----------+-----------+
            |           |           |
            V           |           V
    +---------------+   |   +---------------+
    |    Endpoint   |   |   |    Endpoint   |
    +---------------+   |   +---------------+
               \        |        /
                \       |       /
                 V      V      V
                +---------------+
                |    Endpoint   |
                +---------------+

```

Every Boxes represents an API Endpoint in your project. The Serverless Workflow will ensure the communication between your API endpoints in a Tree Based Manner.

You will have to create a static method named **`get_workflow_init_data`** and **`get_workflow_complete_data`** inside your APIView class.



## Usage

### Let take an Example:

Suppose we have to extract the information of **Blog** and **Comments** from a data warehouse and create their respective tables in a separate database for better analytical purpose. And this implementation should be done a background task.


```
    [Blog] -------> [Comment]<--+
                        |       |
                        +-------+

    In the database, one Blog can have many Comments and 
    a Comment can again have nested Comments.

    The Schema of the tables are as follows:

    Blog:
    id  | name | description
    int | str  | str

    Comment:
    id  | blog    | comment           | message
    int | FK Blog | FK Comment (null) | str

    The Schema of the Data Warehouse tables are as follows:

    [{
      id: int,
      name: str,
      description: str,
      comments: [
        {
          id: int,
          comments: [
            {
              id: str,
              comments: [...],
               message: str
            }
          ],
          message: str
          },
        },
        ...
      ]
    }, ...]

    The schedule of the tasks can be seen in the following example below.

                          +-----------+
                          |  Trigger  |
                          +-----------+
                                |
                              BLOG[] (Page 1)
                               /|\
                              / | \
                             /  |  \
                             V  V  V
                          +------------+
                          | Write Blog |
                          +------------+
                                |
                            Comment[]  +----+
                              / | \    |    |
                             /  |  \   |    |
                             V  V  V   V    |
                       +------------------+ |
                       |   Write Comment  | |
                       +------------------+ |
                                |           |
                        Nested Comment[]    |
                                |           |
                                +-----------+

                        .   .   .   .   .   .

                Repeat the same for Page 2 via SubTaskNext of Trigger Endpoint

```

### We are going to need 3 API Endpoints to Complete the migration from Data Warehouse to Relational Database.

* **Trigger Endpoint:** This Endpoint will return **`List of Blogs`** in a paginated fashion. 
* **Blog Create Endpoint:** This endpoint will Create Blog and **`pop the Comments`** from its payload and returns the popped comments as response. As shown in the diagram above.
* **Comments Create Endpoint:** This endpoint will create Comments and **`Pop the Comments`** from its payload and returns the popped comments as response

## Implementation:

```
            +---------------+ ------ View Init
            |    Trigger    |
            +---------------+ ------ On Complete
                    |
                    |
        +-----------------------+ ------- View Init
        |       Write Blog      |
        +-----------------------+ ------- On Complete
    +--------+      |
    |        |      |
    |   +-----------------------+ ------- View Init
    |   |     Write Comment     |
    |   +-----------------------+ ------- On Complete
    |               |
    +---------------+
        For Nested
         Comments

    - get_workflow_init_data function is referred as View Init
    - get_workflow_complete_data function is referred as On Complete
```

### Note:
* **`get_workflow_init_data`** and **`get_workflow_complete_data`** both the functions are mandatory.
* As seen in the above diagram we can see that *`View Init`* function will be called before the Request goes to the View and when the View Responds the *`On Complete`* function will be called.

```
                Flow of Request
                
                +--------------+
                |   Request    |
                +--------------+
                        |
                        V
        +-------------------------------+
        |    get_workflow_init_data     |
        +-------------------------------+
                        |
                        V
                   +---------+
                   |  View   |
                   +---------+
                        |
                        V
        +-------------------------------+
        |  get_workflow_complete_data   |
        +-------------------------------+
                        |
                        V
                +--------------+
                |   Response   |
                +--------------+
```
### **`Note`**:
* We are using Middleware to achieve this.

### **`About get_workflow_init_data`**:

This function will return a Dictonary that contains id, parent_task and request

```
    {
      id: Some Task ID,
      parent_task: None,
      request: {
        url: request.url,
        method: request.method,
        payload: Payload will be "" if request method is "GET" else request.payload,
        headers: request.headers
      }
    }

    We are storing this data in the task because if by any chance this current task will fail then we still have the entire request object to retry again.
```

### **`About get_workflow_complete_data`**:

This function will return a Dictonary that contains id, response, immediate_next and sub_task_next.

```
    {
      id: Some Task ID,  # This id of get_workflow_init_data and get_workflow_complete_data will be same.
      response: {
        status_code: response's status_code,
        headers: Same as Request's Header
        data: response's data
      },
      immediate_next: [],
      sub_task_next: []
    }

    * Immediate Next will be Trigger Parallely if response's status_code is 200.
    * Sub Task Next will wait untill all the Immediate Next Task are Complete
    * Immediate Next Task's can also spawn Immediate Processes and Sub Next Processes.

    Immediate Next: {
      url: URL to call when the current task status is Completed.
      method: Which method does this URL accept.
      input_type: Type of Input,
      custom_input: {}
    }

    Sub Task Next: {
      url: URL to call when all the immediate processes of current task are Completed.
      method: Which method does this URL accept.
      input_type: Type of Input,
      custom_input: {}
    }
```
