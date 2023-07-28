from google.cloud import tasks_v2
from google.cloud.tasks_v2.types import Task
from google.protobuf import timestamp_pb2
import datetime
import json
from typing import Dict, Any, Optional, cast, Union


def create_http_task(url: str, payload: Union[Optional[Dict[str, Any]], str] = None, method: str ="POST", headers: Dict[str, Any]={"Content-Type": "application/json"}, queue: str = 'serverless-workflow-q', in_seconds: Optional[int] = None, task_name: Optional[str] = None) -> Task:

    # Create a client.
    client  = tasks_v2.CloudTasksClient()

    project = 'advancedware'
    region  = 'europe-west1'

    # Construct the fully qualified queue name.
    parent = client.queue_path(project, region, queue)

    task: Dict[str, Any] = {
        'http_request': {  # Specify the type of request.
            'http_method': method,
            'url': url,  # The full url path that the task will be sent to.
            'oidc_token': {
                'service_account_email': 'books-356@advancedware.iam.gserviceaccount.com'
            },
            'headers': headers
        }
    }
    
    if payload is not None:
        
        if isinstance(payload, dict):
            # Convert dict to JSON string
            payload = cast(str, json.dumps(payload))
        
        # The API expects a payload of type bytes.
        converted_payload = payload.encode()

        # Add the payload to the request.
        task["http_request"]["body"] = converted_payload

    if in_seconds is not None:
        # Convert "seconds from now" into an rfc3339 datetime string.
        d = datetime.datetime.utcnow() + datetime.timedelta(seconds=in_seconds)

        # Create Timestamp protobuf.
        timestamp = timestamp_pb2.Timestamp()
        timestamp.FromDatetime(d)

        # Add the timestamp to the tasks.
        task["schedule_time"] = timestamp

    if task_name is not None:
        # Add the name to tasks.
        task["name"] = task_name

    # Use the client to build and send the task.
    response = client.create_task(request={"parent": parent, "task": task})

    return response
